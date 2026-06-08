import streamlit as st
import requests

# -------- CONFIG --------

st.set_page_config(
    page_title="AI PDF Chatbot",
    layout="wide"
)

st.title("📄 AI PDF Chatbot")

# -------- BACKEND URL --------

BACKEND_URL = "http://127.0.0.1:8000"

# AFTER DEPLOYMENT:
# BACKEND_URL = "https://your-backend.onrender.com"

# -------- SESSION --------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------- PDF UPLOAD --------

uploaded_file = st.file_uploader(
    "Upload PDF",
    type="pdf"
)

if uploaded_file:

    files = {
        "file": uploaded_file
    }

    with st.spinner("Uploading PDF..."):

        response = requests.post(
            f"{BACKEND_URL}/upload-pdf",
            files=files
        )

    if response.status_code == 200:

        st.success(
            "PDF uploaded successfully"
        )

# -------- CHAT HISTORY --------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

# -------- USER INPUT --------

question = st.chat_input(
    "Ask anything from PDF..."
)

if question:

    # USER MESSAGE

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    # ASSISTANT MESSAGE

    with st.chat_message("assistant"):

        answer_placeholder = st.empty()

        full_response = ""

        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={
                "question": question
            },
            stream=True
        )

        for chunk in response.iter_content(
            chunk_size=1024
        ):

            if chunk:

                text = chunk.decode("utf-8")

                full_response += text

                answer_placeholder.markdown(
                    full_response + "▌"
                )

        answer_placeholder.markdown(
            full_response
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })