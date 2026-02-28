# Monday.com BI Agent

An AI agent that answers founder-level business intelligence queries by integrating with monday.com boards containing Work Orders and Deals data.

## Features
- **Conversational Interface**: Ask questions via a Streamlit chat UX.
- **Live Integration**: Fetches data from Monday.com's GraphQL v2 API directly upon query. No caching or pre-loading.
- **Data Resilience**: Powered by GPT-4o, handles inconsistent and messy data (null values, mismatched currencies) gracefully while communicating data quality caveats.
- **Action Visibility**: Shows exactly when the agent is scraping data from Monday.com vs processing.

## Setup Requirements

1. **Python 3.10+** is required.
2. Clone/Extract the repository.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your credentials:
   ```env
   MONDAY_API_TOKEN=your_token_here
   OPENAI_API_KEY=your_openai_key_here
   DEALS_BOARD_ID=XXXXXXX
   WORK_ORDERS_BOARD_ID=YYYYYYY
   ```
   *(Note: You must first import the provided Excel/CSV files into Monday.com to generate these Board IDs).*

## Running the App

Execute the following command in your terminal:
```bash
streamlit run app.py
```
