import streamlit as st
import os
from dotenv import load_dotenv
from agent import run_query
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Monday.com BI Agent", page_icon="📊", layout="wide")

st.title("📊 Monday.com Strategy & BI Agent")
st.markdown("""
Ask founder-level questions about your Deals and Work Orders.
*Note: This agent queries Monday.com live and does not cache data.*
""")

# Sidebar for Setup / Verification
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.info("To test this agent, ensure you have the following in your `.env` file:")
    st.code("""
MONDAY_API_TOKEN=...
OPENAI_API_KEY=...
DEALS_BOARD_ID=...
WORK_ORDERS_BOARD_ID=...
    """)
    
    # Check if keys are loaded
    if not os.getenv("MONDAY_API_TOKEN") or not os.getenv("OPENAI_API_KEY"):
         st.error("Missing API Keys! The agent will fail.")
    else:
         st.success("API Keys Loaded")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("E.g., How's our pipeline looking for the energy sector this quarter?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # We use st.status to show the visible action/tool-call trace
        with st.status("Agent is working...", expanded=True) as status:
            try:
                # Format chat history for LangChain
                chat_history = []
                for msg in st.session_state.messages[:-1]: # exclude current prompt
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    else:
                        chat_history.append(AIMessage(content=msg["content"]))
                
                def tool_callback(tool_name, tool_input):
                    st.write(f"🔄 **Calling Tool**: `{tool_name}`")
                    st.text(f"Input: {tool_input}")
                
                # Execute agent
                answer = run_query(prompt, chat_history, callback=tool_callback)
                
                status.update(label="Response Generated", state="complete", expanded=False)
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                status.update(label="Agent Error", state="error", expanded=True)
                st.error(f"An error occurred: {str(e)}")
