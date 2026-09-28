from dataclasses import dataclass

from huggingface_hub.cli.inference_endpoints import update
from langchain.tools import tool, ToolRuntime
from langchain.agents import AgentState,create_agent
from langchain.messages import ToolMessage
from langgraph.types import command



@dataclass
class EmailContext:
    email_address: str
    password: str


class AuthenticatedState(AgentState):
    authenticated: bool

@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> command:
    """Authenticate the User with given email and password"""
    if email == runtime.context.email_address and password == runtime.context.password:
        return command(
            update={
                "Authenticated" : True,
                "messages" : [ToolMessage("Successfully authenticated", tool_call_id=runtime.tool_call_id)],
            }
        )

    else:
        return command(
            update={
                "Authenticated" : False,
                "messages" : [ToolMessage("Authentication failed", tool_call_id=runtime.tool_call_id)]
            }
        )