from dotenv import load_dotenv



load_dotenv()

from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get

mcp = FastMCP("mcp_server")

tavily_client = TavilyClient()

@mcp.tool()
def search_web(query: str) -> Dict[str, Any]:
    """Search the web for information"""

    results = tavily_client.search(query)

    return results

@mcp.prompt()
def prompt():
    """A Wedding Planner who can plan Flights, Venue and Select the Music matching the right genre from the music database"""
    return """
    You are a helpful Wedding Planner 
    """