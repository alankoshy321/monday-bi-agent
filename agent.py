import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from dotenv import load_dotenv

# Ensure the local modules can be imported
from monday_api import get_deals_df, get_work_orders_df

load_dotenv()

def fetch_and_analyze_deals(query: str = "") -> str:
    """
    Fetches the live Deals board from Monday.com and returns a summarized answer based on the query.
    Data contains: Deal name, Value, Stage, Expected Close Date, Sector, etc.
    """
    try:
        df = get_deals_df()
        summary = f"Fetched {len(df)} Deals. Columns available: {', '.join(df.columns)}. \n\nRaw Data Preview:\n{df.head(10).to_string()}"
        return summary
    except Exception as e:
        return f"Error fetching Deals: {str(e)}"

def fetch_and_analyze_work_orders(query: str = "") -> str:
    """
    Fetches the live Work Orders board from Monday.com and returns a summarized answer based on the query.
    Data contains: Order ID, Status, Priority, Client, Due Date, etc.
    """
    try:
        df = get_work_orders_df()
        summary = f"Fetched {len(df)} Work Orders. Columns available: {', '.join(df.columns)}. \n\nRaw Data Preview:\n{df.head(10).to_string()}"
        return summary
    except Exception as e:
        return f"Error fetching Work Orders: {str(e)}"

tools_map = {
    "fetch_and_analyze_deals": fetch_and_analyze_deals,
    "fetch_and_analyze_work_orders": fetch_and_analyze_work_orders
}

def run_query(query: str, chat_history: list = None, callback=None):
    if chat_history is None:
        chat_history = []
        
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0, 
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_and_analyze_deals",
                "description": "Fetches the live Deals board from Monday.com. Use this when the user asks about deals, revenue, pipeline, expected close dates, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_and_analyze_work_orders",
                "description": "Fetches the live Work Orders board from Monday.com. Use this when the user asks about work orders, status, priority, clients, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": []
                }
            }
        }
    ]
    
    system_prompt = SystemMessage(content="""You are a senior Business Intelligence AI Agent assisting founders and executives.
Your goal is to answer their business questions quickly and accurately using live data from Monday.com.

**Core Directives**:
1. **Live Data Only**: Always use the provided tools to query Monday.com. Do NOT use prior knowledge.
2. **Data Resilience**: The data you receive may be intentionally messy (missing/null values, inconsistent formats). Provide insights but ALWAYS communicate data quality caveats.
3. **Query Understanding**: Interpret founder-level questions (e.g., "pipeline health", "sector performance"). If a query is entirely ambiguous, ask a clarifying question.
4. **Cross-Board Insights**: If necessary, use both tools to query across both boards.

When you receive the raw data from the tools, process it mentally, calculate the metrics the user asked for (handling currency strings, nulls, etc. appropriately in your reasoning), and formulate a clear, insightful response.
""")
    
    messages = [system_prompt] + chat_history + [HumanMessage(content=query)]
    
    while True:
        response = llm.invoke(messages, tools=tools)
        messages.append(response)
        
        if not response.tool_calls:
            break
            
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            if callback:
                 callback(tool_name, str(tool_args))
                 
            tool_func = tools_map.get(tool_name)
            if tool_func:
                try:
                    tool_result = tool_func(**tool_args)
                except Exception as e:
                    tool_result = str(e)
            else:
                tool_result = f"Unknown tool: {tool_name}"
                
            messages.append(ToolMessage(tool_call_id=tool_call['id'], content=tool_result, name=tool_name))
            
    return messages[-1].content

if __name__ == "__main__":
    print(run_query("How many deals do we have?"))
