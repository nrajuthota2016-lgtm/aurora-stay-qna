
import streamlit as st
import requests
import os


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:7860")


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Aurora Stays",
    page_icon="🏨",
    layout="wide"
)


# ---------------------------------------------------------
# Sidebar  -  Model parameters
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ Parameters")

    k = st.slider(
        "k (chunks to retrieve)",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of relevant chunks fetched from the vector store."
    )

    retrieval_mode = st.selectbox(
        "Retrieval mode",
        options=["mmr", "similarity"],
        index=0,
        help="MMR is recommended because it reduces duplicate chunks and improves answer grounding."
    )

    fetch_k = st.slider(
        "MMR fetch_k",
        min_value=4,
        max_value=40,
        value=12,
        step=2,
        help="Number of candidate chunks considered before selecting final k with MMR."
    )

    lambda_mult = st.slider(
        "MMR lambda",
        min_value=0.1,
        max_value=0.9,
        value=0.3,
        step=0.1,
        help="Lower values favor diversity; higher values favor raw similarity."
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Higher values make the output more creative; lower values make it more focused."
    )

    max_tokens = st.slider(
        "Max tokens",
        min_value=64,
        max_value=2048,
        value=512,
        step=64,
        help="Maximum number of tokens in the generated answer."
    )


# ---------------------------------------------------------
# Main area
# ---------------------------------------------------------

st.title("🏨 Aurora Stays")
st.write("Ask a question about Aurora Stays policies.")


# ---------------------------------------------------------
# Response type selection (two options only)
# ---------------------------------------------------------

response_type = st.radio(
    "Response mode",
    ["Answer only", "Answer + Relevant Chunks"],
    horizontal=True
)


# ---------------------------------------------------------
# Query input
# ---------------------------------------------------------

query = st.text_input(
    "Your question",
    placeholder="e.g., What is the waiting period for hospitalization?"
)


# ---------------------------------------------------------
# Submit
# ---------------------------------------------------------

if st.button("Submit", type="primary"):

    if not query.strip():
        st.warning("Please enter a question.")

    else:

        # Pick endpoint
        if response_type == "Answer only":
            endpoint = "/v1/answer"
        else:
            endpoint = "/v1/answer_with_relevant_chunks"

        # Build request payload with parameters
        payload = {
            "query": query,
            "k": k,
            "retrieval_mode": retrieval_mode,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            with st.spinner("Thinking…"):
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json=payload
                )

            if response.status_code == 200:

                result = response.json()

                # -- Answer only --------------------------------
                if response_type == "Answer only":

                    st.subheader("Answer")
                    st.write(result["answer"])

                # -- Answer + Relevant Chunks -------------------
                else:

                    st.subheader("Answer")
                    st.write(result["answer"])

                    st.subheader("Relevant Chunks")
                    for i, chunk in enumerate(result["relevant_chunks"], start=1):
                        with st.expander(f"Chunk {i}"):
                            st.write(chunk)

            else:
                st.error(
                    f"Unable to get a response from the RAG API. "
                    f"Status code: {response.status_code}"
                )

        except requests.exceptions.RequestException:
            st.error(
                "Unable to connect to the RAG API. "
                "Please make sure the backend service is running."
            )
