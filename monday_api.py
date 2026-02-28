import os
import requests
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_API_URL = "https://api.monday.com/v2"

headers = {
    "Authorization": MONDAY_API_TOKEN,
    "API-Version": "2023-10",
    "Content-Type": "application/json"
}

def fetch_board_data(board_id):
    """
    Fetches raw items from a specific Monday.com board.
    Dynamically gets all columns and their text values.
    """
    if not MONDAY_API_TOKEN or MONDAY_API_TOKEN == "your_monday_api_token_here":
         raise Exception("Monday.com API Token is missing or invalid in .env")
    
    # We query the board for its items and their column values
    query = """
    query ($boardId: [ID!]) {
      boards(ids: $boardId) {
        name
        items_page(limit: 100) {
          items {
            id
            name
            column_values {
              id
              text
              type
            }
          }
        }
      }
    }
    """
    
    variables = {
        "boardId": [board_id]
    }
    
    response = requests.post(MONDAY_API_URL, json={"query": query, "variables": variables}, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from Monday.com: {response.text}")
        
    data = response.json()
    
    if "errors" in data:
         raise Exception(f"Monday.com API Error: {data['errors']}")
         
    boards = data.get("data", {}).get("boards", [])
    if not boards:
        return []

    items = boards[0].get("items_page", {}).get("items", [])
    
    # Process items into a list of dictionaries (rows)
    processed_data = []
    for item in items:
        row = {"Item ID": item["id"], "Name": item["name"]}
        for col in item.get("column_values", []):
            row[col["id"]] = col.get("text")
        processed_data.append(row)
        
    return processed_data

def get_deals_df():
    """Fetches Deals board data and converts to DataFrame."""
    board_id = os.getenv("DEALS_BOARD_ID")
    if not board_id or board_id == "your_deals_board_id_here":
        raise Exception("DEALS_BOARD_ID is missing or invalid in .env")
    
    data = fetch_board_data(board_id)
    return pd.DataFrame(data)

def get_work_orders_df():
    """Fetches Work Orders board data and converts to DataFrame."""
    board_id = os.getenv("WORK_ORDERS_BOARD_ID")
    if not board_id or board_id == "your_work_orders_board_id_here":
        raise Exception("WORK_ORDERS_BOARD_ID is missing or invalid in .env")
        
    data = fetch_board_data(board_id)
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Simple test execution
    try:
        deals = get_deals_df()
        print("Successfully fetched Deals. Shape:", deals.shape)
    except Exception as e:
        print(f"Error testing Deals fetch: {e}")
