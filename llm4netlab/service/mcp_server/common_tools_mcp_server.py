import os

from dotenv import load_dotenv
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("common_tools_mcp_server")

load_dotenv("/home/p4/codes/AI4NetOps/.env")


@mcp.tool()
def google_search(query: str) -> dict:
    """Perform a Google search and return the titles and links of the top results.

    Args:
        query (str): The search query.
    Returns:
        dict: A dictionary containing the search results with titles and links.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=5).execute()
    results = [
        {"title": item["title"], "link": item["link"], "snippet": item["snippet"]} for item in res.get("items", [])
    ]
    return {"results": results}


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
    # results = google_search("how is the weather today in torino?")
    # print(results)
