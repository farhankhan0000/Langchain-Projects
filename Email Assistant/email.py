from dataclasses import dataclass

from huggingface_hub.cli.inference_endpoints import update
from langchain.tools import tool, ToolRuntime
from langchain.agents import AgentState,create_agent
from langchain.messages import ToolMessage
from langgraph.types import Command



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