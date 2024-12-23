import streamlit as st
from datetime import datetime
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.workflows.main_workflow import run_workflow
from frontend.utils.session_manager import (
    init_session_state,
    update_chat_history,
    update_session_state,
    clear_session_state
)

# Initialize session state
init_session_state()

# Streamlit UI
st.title("Interactive Anomalies Detection")
st.write("Interact with the LangGraph workflow by asking a question below.")

# Description of the Prototype
with st.expander("About This Prototype", expanded=False):
    st.markdown("""
    This app is designed to analyze **short cycling energy anomalies** for **Building 530** during the **month of October 2024**.

    #### What You Can Do:
    - **Ask Questions About Short Cycling**:
      - Examples:
        - "Is there any short cycling in Building 530?"
        - "Is there any short cycling in Building 530 on Oct 15th?"
        - "How many short cycles occurred on breaker 28722?"
    - **Get Summarized Insights**:
      - Total short cycles and recommendations for identified issues.
    - **Follow-Up Questions**:
      - Refine or expand your queries based on previous answers.

    #### Important Notes:
    - This app **only supports queries** about **Building 530** and **short cycling** for **October 2024**.
    - Unsupported queries will guide you back to the app's focus.

    Start exploring anomalies and trends with precise, contextualized insights!
    """)

# User query input
query = st.text_input("Enter your query:", placeholder="Type your question here...")

# Submit button
if st.button("Submit"):
    if query:
        try:
            with st.spinner("Processing your query..."):
                # Run workflow and get results
                response, fetched_docs, last_interaction = run_workflow(
                    query,
                    previous_docs=st.session_state.previous_docs,
                    conversation_history=st.session_state.history
                )

                # Update session state
                update_session_state(last_interaction, fetched_docs)
                update_chat_history(query, response)

                # Display answer
                st.success("Generated Answer:")
                st.write(response)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query.")

# Display chat history
st.subheader("Chat History:")
if st.session_state.history:
    for item in st.session_state.history:
        st.markdown(f"**[{item['timestamp']}] Q: {item['query']}**")
        st.markdown(f"A: {item['answer']}")
        st.markdown("---")
else:
    st.info("No chat history yet.")

# Clear History button
if st.button("Clear History"):
    clear_session_state()
    st.info("Chat history cleared.") 