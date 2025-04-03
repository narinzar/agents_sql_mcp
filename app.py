import asyncio
import threading
import queue
import os
import time
import sqlite3
from typing import Union, cast, Optional, List, Dict, Any

import gradio as gr
import anthropic
from anthropic.types import MessageParam, TextBlock, ToolUnionParam, ToolUseBlock
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

# Initialize Anthropic client
anthropic_client = anthropic.AsyncAnthropic()

# Create a console for rich text formatting
console = Console()

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=["./mcp_server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)

# Global message queue for async communication
message_queue = queue.Queue()

# Check if database exists, if not create a sample one
def initialize_database():
    if not os.path.exists("database.db"):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # Create sample tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
        ''')
        
        # Insert sample data
        cursor.executemany('''
        INSERT INTO users (name, email) VALUES (?, ?)
        ''', [
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com'),
            ('Bob Johnson', 'bob@example.com'),
        ])
        
        cursor.executemany('''
        INSERT INTO products (name, price, stock) VALUES (?, ?, ?)
        ''', [
            ('Laptop', 999.99, 10),
            ('Smartphone', 699.99, 20),
            ('Headphones', 149.99, 30),
            ('Monitor', 299.99, 15),
        ])
        
        conn.commit()
        conn.close()
        print("Created sample database with users and products tables")

class ChatProcessor:
    def __init__(self):
        self.messages: list[MessageParam] = []
        self.system_prompt: str = """You are a master SQLite assistant. 
        Your job is to use the tools at your disposal to execute SQL queries and provide the results to the user.
        
        When you need to display table results, format them in a nice markdown table format.
        When you need to execute a SQL query, use the query_data tool. 
        Always explain the results of your query in a clear, easy-to-understand way.
        If there's an error with a query, explain what went wrong and suggest a fix."""
        
        # Start the MCP server and processing thread
        self.start_backend()
    
    def start_backend(self):
        """Start the backend processing thread that handles MCP communication"""
        threading.Thread(target=self._start_mcp_server, daemon=True).start()
    
    def _start_mcp_server(self):
        """Initialize and run the MCP server connection"""
        asyncio.run(self._run_server())
    
    async def _run_server(self):
        """Run the MCP server and initialize the connection"""
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Process messages from the queue
                while True:
                    try:
                        # Check if there are any messages in the queue
                        if not message_queue.empty():
                            query, response_callback = message_queue.get()
                            result = await self._process_query(session, query)
                            response_callback(result)
                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
                        
                    # Short sleep to prevent CPU hogging
                    await asyncio.sleep(0.1)
    
    async def _process_query(self, session: ClientSession, query: str) -> List[str]:
        """Process a query and return the response messages"""
        response = await session.list_tools()
        available_tools: list[ToolUnionParam] = [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        
        # Add the user message to the conversation
        self.messages.append(
            MessageParam(
                role="user",
                content=query,
            )
        )
        
        # All Claude responses will be collected here
        all_responses = []

        # Initial Claude API call
        res = await anthropic_client.messages.create(
            model="claude-3-7-sonnet-latest",
            system=self.system_prompt,
            max_tokens=8000,
            messages=self.messages,
            tools=available_tools,
        )

        assistant_message_content: list[Union[ToolUseBlock, TextBlock]] = []
        for content in res.content:
            if content.type == "text":
                assistant_message_content.append(content)
                all_responses.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await session.call_tool(tool_name, cast(dict, tool_args))

                assistant_message_content.append(content)
                self.messages.append(
                    {"role": "assistant", "content": assistant_message_content}
                )
                self.messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": getattr(result.content[0], "text", ""),
                            }
                        ],
                    }
                )
                # Get next response from Claude
                res = await anthropic_client.messages.create(
                    model="claude-3-7-sonnet-latest",
                    max_tokens=8000,
                    messages=self.messages,
                    tools=available_tools,
                )
                
                response_text = getattr(res.content[0], "text", "")
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": response_text,
                    }
                )
                all_responses.append(response_text)

        return all_responses

def submit_query(query: str, chat_history: list) -> tuple[list, list]:
    """Submit a query to the chat processor and update the chat history"""
    if not query.strip():
        return chat_history, chat_history
    
    # Add user message to history immediately
    chat_history.append((query, None))
    
    # Create a result container
    result_container = []
    
    # Define callback for when the result is ready
    def on_result(responses):
        combined_response = "\n\n".join(responses)
        result_container.append(combined_response)
    
    # Submit the query to the processor
    message_queue.put((query, on_result))
    
    # Wait for the result
    while not result_container:
        time.sleep(0.1)
    
    # Update the last history entry with the response
    chat_history[-1] = (query, result_container[0])
    
    return chat_history, chat_history

def main():
    # Initialize the database with sample data if needed
    initialize_database()
    
    # Initialize the chat processor
    chat_processor = ChatProcessor()
    
    # Create the Gradio interface
    with gr.Blocks(title="AI SQL Assistant", theme=gr.themes.Soft(), css="footer {visibility: hidden}") as demo:
        gr.Markdown("# AI SQL Assistant")
        gr.Markdown("""This application allows you to interact with a SQLite database using natural language. 
        Ask questions about the data or request SQL operations, and the AI will generate and execute the appropriate SQL queries.
        
        **Sample tables in the database:**
        - `users` (id, name, email, created_at)
        - `products` (id, name, price, stock)
        """)
        
        chatbot = gr.Chatbot(
            label="Chat", 
            height=500,
            bubble_full_width=False,
            show_copy_button=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Ask a question or request a SQL operation",
                placeholder="For example: 'Show me all users' or 'How many products do we have in stock?'",
                scale=9
            )
            submit = gr.Button("Submit", scale=1)
        
        with gr.Accordion("Example Queries", open=False):
            example_queries = [
                "List all tables in the database",
                "Show me all users",
                "Count how many products cost more than $300",
                "What's the total value of all products in stock?",
                "Insert a new product called 'Tablet' with price $499.99 and stock 5",
                "Update the price of Laptop to $1099.99"
            ]
            gr.Examples(
                examples=example_queries,
                inputs=msg
            )
        
        # Set up event handlers
        submit.click(submit_query, [msg, chatbot], [chatbot, chatbot]).then(
            lambda: "", None, [msg]  # Clear the input box after submission
        )
        msg.submit(submit_query, [msg, chatbot], [chatbot, chatbot]).then(
            lambda: "", None, [msg]  # Clear the input box after submission
        )
        
    # Launch the interface
    demo.launch(share=False, server_port=7860)

if __name__ == "__main__":
    main()
