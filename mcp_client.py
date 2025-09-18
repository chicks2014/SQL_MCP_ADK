import asyncio
from dataclasses import dataclass, field
from typing import Union, cast



import openai
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam, ChatCompletionMessageToolCall
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os

from mcp import ClientSession
# from mcp.client.streamable_http import streamablehttp_client, StreamableHTTPConnectionParams
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams


load_dotenv()

# Create server parameters for stdio connection
# server_params = StdioServerParameters(
#     command="python",  # Executable
#     args=["./mcp_server.py"],  # Optional command line arguments
#     env=None,  # Optional environment variables
# )

server_params=StreamableHTTPConnectionParams(
            url = f'http://{os.getenv("MCP_HOST", "localhost")}:{os.getenv("MCP_PORT", 8001)}/mcp/',  # URL of the MCP server
            timeout=20,  # Timeout in seconds for establishing the connection to the MCP Streamable HTTP server
        )

MODEL = "gpt-4o-mini"  # Model to use for OpenAI API calls

# Use an async OpenAI client
openai_client = openai.AsyncClient()


@dataclass
class Chat:
    messages: list[ChatCompletionMessageParam] = field(default_factory=list)

    system_prompt: str = """You are a master SQLite assistant. 
    Your job is to use the tools at your dispoal to execute SQL queries and provide the results to the user."""

    async def process_query(self, session: ClientSession, query: str) -> None:
        response = await session.list_tools()
        available_tools: list[ChatCompletionToolParam] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]

        print("Available tools:", available_tools)
        print("Calling OpenAI API...")
        try:
            res = await openai_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.messages,
                ],
                tools=available_tools,
                tool_choice="auto",
                max_tokens=8000,
            )
            print("OpenAI API call succeeded.")
            print("OpenAI response:", res.choices[0].message)
        except Exception as e:
            print("OpenAI API call failed:", e)
            return

        message = res.choices[0].message
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_call = cast(ChatCompletionMessageToolCall, tool_call)
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                # tool_args is a JSON string, parse it
                import json
                tool_args_dict = json.loads(tool_args)

                # Execute tool call
                print(f"Calling tool: {tool_name} with args: {tool_args_dict}")
                try:
                    result = await session.call_tool(tool_name, tool_args_dict)
                    print(f"Tool call result: {getattr(result.content[0], 'text', '')}")
                except Exception as e:
                    print(f"Tool call failed: {e}")
                    continue

                self.messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_args,
                            },
                        }
                    ],
                })
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": getattr(result.content[0], "text", ""),
                })

                # Get next response from OpenAI
                print("Calling OpenAI API for next message...")
                try:
                    res = await openai_client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            *self.messages,
                        ],
                        tools=available_tools,
                        tool_choice="auto",
                        max_tokens=8000,
                    )
                    print("OpenAI API call for next message succeeded.")
                    next_message = res.choices[0].message
                    self.messages.append({
                        "role": "assistant",
                        "content": next_message.content or "",
                    })
                    print(next_message.content or "")
                except Exception as e:
                    print("OpenAI API call for next message failed:", e)
        else:
            self.messages.append({
                "role": "assistant",
                "content": message.content or "",
            })
            print(message.content or "")


    async def chat_loop(self, session: ClientSession):
        while True:
            query = input("\nQuery: ").strip()
            self.messages.append({
                "role": "user",
                "content": query,
            })
            await self.process_query(session, query)

    async def run(self):
        print("Connecting to MCP server...")
        print(f"Using command: {server_params.command} {server_params.args}")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                await self.chat_loop(session)



chat = Chat()
asyncio.run(chat.run())