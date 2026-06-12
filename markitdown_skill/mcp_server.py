from mcp.server.fastmcp import FastMCP
from markitdown_skill import MarkItDownParser
import os

# Initialize FastMCP Server
mcp = FastMCP("MarkItDown Document Parser")

@mcp.tool()
def parse_document(file_path: str) -> str:
    """
    Parses any document (including PDF, Word .docx, Excel .xlsx, PPT .pptx, HTML, CSV, JSON) into clean Markdown.
    Use this tool automatically whenever you need to read, inspect, or analyze the content of a document file.
    
    :param file_path: The absolute path of the file to parse.
    :return: The converted Markdown text content of the document.
    """
    normalized_path = os.path.abspath(file_path)
    if not os.path.exists(normalized_path):
        return f"Error: The target file was not found at: {normalized_path}"

    try:
        parser = MarkItDownParser()
        result = parser.parse(normalized_path)
        return result["content"]
    except Exception as e:
        return f"Error occurred during file parsing: {str(e)}"

def main():
    # Run the server via stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
