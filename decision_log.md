# Monday.com BI Agent - Decision Log

## Technology Stack

* **Language**: Python 3.10+
  * *Justification*: Python is the industry standard for AI and data manipulation, offering the most robust libraries for both NLP and data analysis (Pandas).
* **Framework**: Streamlit
  * *Justification*: Provides a rapid, conversational UI out-of-the-box (`st.chat_message`). Its `st.status` feature perfectly fulfills the "Visible action/tool-call trace" requirement without needing complex frontend state management (like React).
* **AI Agent Framework**: LangChain + OpenAI (`gpt-4o`)
  * *Justification*: GPT-4o offers state-of-the-art reasoning for "founder-level questions". LangChain's Tool Calling Agent abstraction maps perfectly to the necessity of querying Monday.com live dynamically (fetching Deals vs Work Orders).
* **Data Processing**: Pandas
  * *Justification*: Essential for handling the messy/inconsistent data format requirement. We pull raw GraphQL JSON from Monday.com and immediately load it into DataFrames to provide the LLM a structured, analyzable preview.

## Architecture & Integration Strategy

### Live API Calls (No Caching)
* **Decision**: We use direct `requests` to Monday.com's `v2` GraphQL API inside the tools (`fetch_and_analyze_deals`, `fetch_and_analyze_work_orders`). 
* **Justification**: This ensures compliance with "Every query must trigger live API calls at query time" and "Do NOT preload or cache data". When a user asks a question, the LLM decides *which* board to fetch based on context, executing the live query on demand.

### Data Resilience Strategy
* **Decision**: We do not strictly type-cast the Monday.com columns defensively in Pandas before sending to the LLM (unless it breaks the JSON). Instead, we pass a raw preview to GPT-4o.
* **Justification**: The prompt instructs the LLM that the data is intentionally messy. GPT-4o is highly capable of recognizing "1,000" and "$1000" and normalizing them conceptually to answer a revenue question. Furthermore, the prompt mandates the LLM to *communicate data quality caveats* directly to the user based on its observation of the raw data (e.g., missing values).

### Agent Action Visibility
* **Decision**: Implemented a custom LangChain Callback Handler combined with Streamlit's `st.status`.
* **Justification**: This provides real-time, clear UX showing exactly when the agent decides to trigger a tool, what the tool is (`fetch_and_analyze_deals`), and signals when the final response is generated.
