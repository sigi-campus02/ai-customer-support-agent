# -----------------------------------------------
# MCP Server – mcp_server.py
#
# Serves the tools for the support agent as a separate microservice.
# Runs on http://127.0.0.1:8000 and is accessed via HTTP.
# Tools are loaded dynamically by the agent at runtime.

from fastmcp import FastMCP
import pandas as pd
from datetime import datetime

# FastMCP instance – name is returned when list_tools() is called
mcp = FastMCP("Support Tools")

# Load data once on startup
customers = pd.read_excel("data/customers.xlsx")
products = pd.read_excel("data/products.xlsx")


@mcp.tool()
def get_customer(customer_id: int) -> str:
    """Get customer details using customer_id"""

    # filter DataFrame by customer_id and return as dict
    result = customers[customers["customer_id"] == int(customer_id)]
    if result.empty:
        return "Customer not found"
    return str(result.to_dict(orient="records"))


@mcp.tool()
def get_product(product_id: str) -> str:
    """Get product details using product_id"""
    result = products[products["product_id"] == product_id]
    if result.empty:
        return "Product not found"
    return str(result.to_dict(orient="records"))


@mcp.tool()
def log_escalation(
    data: str,
    reason: str = "",
    tools_used: str = "",
    model_used: str = ""
) -> str:
    """Log escalation if issue cannot be solved. Include reason and tools used."""

    # append new entry to existing CSV (mode="a")
    # header=False to avoid duplicate column headers

    df = pd.DataFrame([{
        "timestamp": datetime.now(),
        "data": data,               # full summary of the customer request
        "reason": reason,           # why the issue could not be resolved
        "tools_used": tools_used,   # which tools were called
        "model_used": model_used    # which model was used
    }])
    df.to_csv("escalations.csv", mode="a", header=False, index=False)
    return "Escalation logged"


@mcp.tool()
def update_customer(customer_id: int, field: str, value: str) -> str:
    """Update a field of an existing customer. Fields: first_name, last_name, email, city, status"""

    # global variable so changes persist in memory
    global customers

    if customer_id not in customers["customer_id"].values:
        return f"Customer {customer_id} not found"

    # only allowed fields can be updated
    allowed_fields = ["first_name", "last_name", "email", "city", "status"]
    if field not in allowed_fields:
        return f"Field '{field}' not allowed. Allowed fields: {allowed_fields}"

    # update value in DataFrame and write back to Excel immediately
    customers.loc[customers["customer_id"] == customer_id, field] = value
    customers.to_excel("data/customers.xlsx", index=False)

    return f"Customer {customer_id} updated: {field} = {value}"


if __name__ == "__main__":
    # start server – runs on http://127.0.0.1:8000
    # streamable-http = HTTP-based MCP transport protocol
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
