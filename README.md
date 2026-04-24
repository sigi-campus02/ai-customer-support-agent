# AI Customer Support Agent

An autonomous customer support agent built with LangChain, OpenAI, and a custom MCP server. The agent handles customer inquiries end-to-end: it retrieves customer and product data via tools, decides which model complexity is appropriate for each request, and escalates unsolvable cases with structured logging – without any hardcoded decision rules.

## Features

- **Dynamic tool loading** – Tools are served by a separate MCP microservice and loaded at runtime via `client.get_tools()`. The agent discovers available tools itself.
- **LLM-based model routing** – `choose_model()` uses the conversation history to decide between a fast and a powerful model, handling edge cases that keyword rules would miss.
- **Autonomous tool loop** – A `while True` loop lets the agent call tools in any order and quantity until it has enough information to respond.
- **Structured escalation logging** – Unresolvable cases are logged to `escalations.csv` with timestamp, summary, reason, tools used, and model used.
- **Voilà GUI** – The notebook can be served as a standalone chat app via Voilà, hiding all implementation cells.

## Tech Stack

- Python, Jupyter Notebook
- LangChain, LangChain OpenAI, LangChain MCP Adapters
- FastMCP
- OpenAI GPT API
- ipywidgets, Voilà
- pandas, openpyxl

## Project Structure

```
ai-customer-support-agent/
├── support_agent.ipynb   ← agent logic + Voilà GUI
├── mcp_server.py         ← MCP tool server
├── .env                  ← OPENAI_API_KEY=sk-...
├── escalations.csv       ← auto-generated on first run
└── data/
    ├── customers.xlsx
    └── products.xlsx
```

## Setup

**Install dependencies:**

```bash
pip install langchain langchain-core langchain-openai langchain-mcp-adapters
pip install fastmcp python-dotenv openpyxl ipywidgets voila
```

**Add your OpenAI API key to `.env`:**

```
OPENAI_API_KEY=sk-...
```

## Usage

**Step 1 – Start the MCP server** (Terminal 1):

```bash
python mcp_server.py
```

**Step 2a – Launch as a Voilà app** (Terminal 2):

```bash
voila support_agent.ipynb --TagRemovePreprocessor.remove_cell_tags=hide
```

Opens at `http://localhost:8866`.

**Step 2b – Run in Jupyter directly:**

Open `support_agent.ipynb` and run all cells. Output appears in the last cell.

## Architecture

```
support_agent.ipynb
        │
        │  connects at runtime
        ▼
mcp_server.py  (FastMCP, http://127.0.0.1:8000)
        │
        ├── get_customer()
        ├── get_product()
        ├── update_customer()
        └── log_escalation()
```

Each incoming message goes through three steps:

1. **Parse** – Extract `customer_id` and `product_id` from the conversation history
2. **Route** – Choose between `gpt-4o-mini` (simple) and `gpt-4o` (complex) based on LLM assessment
3. **Tool loop** – Call tools as needed until the agent produces a final response or escalates
