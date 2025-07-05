from typing import Any
import httpx
import logging
from mcp.server.fastmcp import FastMCP

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f" Error making request: {e}")
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
 Event: {props.get('event', 'Unknown')}
 Area: {props.get('areaDesc', 'Unknown')}
 Severity: {props.get('severity', 'Unknown')}
 Description: {props.get('description', 'No description available')}
 Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
     Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return " Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return f" No active alerts for {state}."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """ Echo a message as a resource."""
    return f"Resource echo: {message}"

#  Start the FastMCP server
if __name__ == "__main__":
    print(" Starting FastMCP weather server...")
    import asyncio
    asyncio.run(mcp.run())
