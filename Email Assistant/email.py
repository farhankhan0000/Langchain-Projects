from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Callable
from langchain.tools import tool, ToolRuntime
from langchain.agents import AgentState,create_agent
from langchain.messages import ToolMessage
from langgraph.types import Command
from langchain.agents.middleware import wrap_model_call,dynamic_prompt,HumanInTheLoopMiddleware
from langchain.agents.middleware import ModelRequest,ModelResponse

load_dotenv()

@dataclass
class EmailContext:
    email_address : str = "farhan123@example"
    password : str = "password123"


class AuthenticatedState(AgentState):
    authenticated: bool



@tool
def check_inbox() -> str:
    """Check the inbox for the recent emails"""

    return """
    Hey Farhan I am in the town for a week, How about we meet and discuss business,
    if you can make some time and come for a dinner let me know,
    -best, Julie(julie@example.com)
    """

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send a response Email"""

    return f"Email Sent to {to} with subject {subject} body {body}"


@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
    """Authenticate the User with given email and password"""
    if email == runtime.context.email_address and password == runtime.context.password:
        return Command(
            update={
                "Authenticated" : True,
                "messages" : [ToolMessage("Successfully authenticated", tool_call_id=runtime.tool_call_id)],
            }
        )

    else:
        return Command(
            update={
                "Authenticated" : False,
                "messages" : [ToolMessage("Authentication failed", tool_call_id=runtime.tool_call_id)]
            }
        )


@wrap_model_call
async def dynamic_tool_call(
        request: ModelRequest, handler: Callable[[ModelRequest],ModelResponse]
) -> ModelResponse:
    """Allow read inbox and send Email tools only if user provide correct email and password"""

    authenticated = request.state(authenticate)

    if authenticated:
        tools=[check_inbox,send_email]
    else:
        tools=[authenticate]

    request=request.override(tools=tools)
    return await handler(request)


authenticated_prompt = "You are a helpful Assistant that can check the inbox and send the emails."
unauthenticated_prompt = "You are a helpful Assistant that authenticate users."

@dynamic_prompt
def dynamic_prompt_func(request: ModelRequest) -> str:
    """Generate System Prompt based on authentication status"""

    authenticated = request.state(authenticate)

    if authenticated:
        return authenticated_prompt

    else:
        return unauthenticated_prompt

agent = create_agent("google_genai:gemini-2.5-flash",
                     tools=[check_inbox,send_email,authenticate],
                     state_schema=AuthenticatedState,
                     context_schema=EmailContext,
                     middleware=[dynamic_tool_call,
                                 dynamic_prompt_func,
                                 HumanInTheLoopMiddleware(
                                     interrupt_on={
                                         "authenticate" : False,
                                         "check_inbox" : False,
                                         "send_email" : True
                                     }
                                 )])