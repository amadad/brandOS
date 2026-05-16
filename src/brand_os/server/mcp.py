"""MCP server (optional)."""
from __future__ import annotations


def create_mcp_server():
    """Create MCP server for LLM integration.

    Requires: fastmcp optional dependency.
    """
    try:
        from fastmcp import FastMCP
    except ImportError as exc:
        raise ImportError("fastmcp required. Install with: pip install brand-os[server]") from exc

    return FastMCP("brandos")


def run_server() -> None:
    """Run the MCP server with default stdio transport."""
    mcp = create_mcp_server()
    mcp.run()


if __name__ == "__main__":
    run_server()
