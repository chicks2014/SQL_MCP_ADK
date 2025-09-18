# server.py
import asyncio
import logging
import os
import sqlite3
from typing import Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join("logs", "demo_mcp_server.log")),
    ],
)
logger = logging.getLogger("demo_mcp_server")

# Create an MCP server
mcp = FastMCP("Demo")


@mcp.tool()
def query_data(sql: str) -> str:
    """Execute SQL queries safely."""
    db_path = os.environ.get("DATABASE_PATH", "./chinook.db")
    logger.info(f"Executing SQL query: {sql}")
    try:
        conn = sqlite3.connect(db_path)
        try:
            result = conn.execute(sql).fetchall()
            conn.commit()
            logger.info(f"Query executed successfully. Rows returned: {len(result)}")
            return "\n".join(str(row) for row in result)
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return f"Error: {str(e)}"
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return f"Error: {str(e)}"

# --- Additional MCP database tools ---
@mcp.tool()
def preview_table(table_name: str, limit: int = 5) -> str:
    """Preview the first few rows of a table."""
    db_path = os.environ.get("DATABASE_PATH", "./chinook.db")
    logger.info(f"Previewing table: {table_name}, limit: {limit}")
    try:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute(f'SELECT * FROM "{table_name}" LIMIT ?', (limit,))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            preview = [" | ".join(columns)]
            for row in rows:
                preview.append(" | ".join(str(item) for item in row))
            return "\n".join(preview)
        except Exception as e:
            logger.error(f"Table preview error: {e}")
            return f"Error: {str(e)}"
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def column_summary(table_name: str) -> str:
    """Get column names and types for a table."""
    db_path = os.environ.get("DATABASE_PATH", "./chinook.db")
    logger.info(f"Getting column summary for table: {table_name}")
    try:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            if not columns:
                return f"No columns found for table '{table_name}'."
            summary = ["Column | Type | NotNull | Default | PK"]
            for col in columns:
                summary.append(f"{col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]}")
            return "\n".join(summary)
        except Exception as e:
            logger.error(f"Column summary error: {e}")
            return f"Error: {str(e)}"
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def schema_discovery() -> str:
    """List all tables and their columns in the database."""
    db_path = os.environ.get("DATABASE_PATH", "./chinook.db")
    logger.info("Discovering database schema.")
    try:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            if not tables:
                return "No tables found in the database."
            schema = []
            for table in tables:
                schema.append(f"Table: {table}")
                col_cursor = conn.execute(f'PRAGMA table_info("{table}")')
                columns = col_cursor.fetchall()
                for col in columns:
                    schema.append(f"  - {col[1]} ({col[2]})")
            return "\n".join(schema)
        except Exception as e:
            logger.error(f"Schema discovery error: {e}")
            return f"Error: {str(e)}"
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return f"Error: {str(e)}"

@mcp.prompt()
def example_prompt(code: str) -> str:
    logger.info("Prompt requested for code review.")
    return f"Please review this code:\n\n{code}"


async def main():
    logger.info("Initializing MCP server...")
    try:
        mcp.settings.host = os.getenv("MCP_HOST", "localhost")
        mcp.settings.port = int(os.getenv("MCP_PORT", "8000"))
        mcp.settings.streamable_http_path = os.getenv("MCP_PATH", "/mcp/")
        logger.info(
            f"Starting MCP server on {mcp.settings.host}:{mcp.settings.port} with path {mcp.settings.streamable_http_path}"
        )
        await mcp.run_streamable_http_async()
        logger.info("MCP server started successfully.")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")


if __name__ == "__main__":
    asyncio.run(main())
