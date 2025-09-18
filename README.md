
# MCP SQL Agent Demo

Build an AI-powered SQL agent using MCP to interact with a SQLite database via natural language.

## Features

- Natural language to SQL conversion using Anthropic Claude 3 Sonnet
- Safe SQL query execution on a SQLite database
- Preview table data and schema
- Discover database structure
- Modular MCP server and client architecture
- Logging for debugging and audit

## Tech Stack

- Python 3.12+
- MCP (Model Context Protocol)
- Anthropic Claude 3 Sonnet
- SQLite
- Loguru
- python-dotenv
- Rich

## Prerequisites

- Python 3.12 or higher
- `uv` package manager
- Anthropic API key (set in `.env`)
- SQLite database file (`chinook.db` or your own)

## Installation

1. **Clone the repository**
  ```sh
  git clone https://github.com/chicks2014/SQL_MCP_ADK.git
  cd SQL_MCP_ADK
  ```

2. **Install dependencies**
  ```sh
  uv sync
  ```

3. **Set up environment variables**
  - Create a `.env` file in the project root:
    ```
    ANTHROPIC_API_KEY=sk-ant-api03-YOUR_API_KEY
    DATABASE_PATH=./chinook.db
    MCP_HOST=localhost
    MCP_PORT=8000
    MCP_PATH=/mcp/
    ```

## Usage

1. **Run the MCP client**
  ```sh
  uv run mcp_client.py
  ```
  - The client will automatically start the MCP server.
  - Enter your queries in natural language.

2. **Available Tools**
  - `query_data(sql: str)`: Execute SQL queries
  - `preview_table(table_name: str, limit: int)`: Preview table rows
  - `column_summary(table_name: str)`: Get column info
  - `schema_discovery()`: List all tables and columns

## Project Structure

```
ADK_MCP_demo/
├── mcp_client.py      # MCP client (AI interface)
├── mcp_server.py      # MCP server (SQL tools)
├── chinook.db         # SQLite database
├── .env               # Environment variables
├── logs/              # Log files
├── test/DB_Agent/     # Example agent code
├── README.md          # Project documentation
├── pyproject.toml     # Python project config
├── uv.lock            # Dependency lock file
```

## Implementation Details

- **Server**: `mcp_server.py` exposes SQL tools via MCP.
- **Client**: `mcp_client.py` uses Anthropic Claude to translate user queries and call server tools.
- **Database**: SQLite file, path configurable via `.env`.
- **Logging**: All server actions are logged to `logs/demo_mcp_server.log`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License – see [LICENSE](LICENSE) for details.
