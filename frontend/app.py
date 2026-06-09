import streamlit as st
import requests

# -------- PAGE CONFIG --------

st.set_page_config(
    page_title="AI PDF Chatbot",
    layout="wide"
)

st.title("📄 AI PDF Chatbot")

# -------- BACKEND URL --------

BACKEND_URL = "https://ai-pdf-chatbot-npmd.onrender.com"

# -------- SESSION STATE --------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False

# -------- PDF UPLOAD --------

uploaded_file = st.file_uploader(
    "Upload PDF",
    type="pdf"
)

# -------- UPLOAD BUTTON --------

if uploaded_file and not st.session_state.pdf_uploaded:

    if st.button("Upload PDF"):

        files = {
            "file": uploaded_file
        }

        try:

            with st.spinner("Uploading PDF... Please wait"):

                response = requests.post(
                    f"{BACKEND_URL}/upload-pdf",
                    files=files,
                    timeout=300
                )

            if response.status_code == 200:

                st.success("PDF uploaded successfully ✅")

                st.session_state.pdf_uploaded = True

            else:

                st.error(
                    f"Upload failed: {response.text}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to backend server."
            )

        except requests.exceptions.Timeout:

            st.error(
                "Request timeout. Backend may be sleeping."
            )

        except Exception as e:

            st.error(str(e))

# -------- CHAT HISTORY --------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# -------- CHAT INPUT --------

question = st.chat_input(
    "Ask anything from PDF..."
)

# -------- ASK QUESTION --------

if question:

    # ----- USER MESSAGE -----

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    # ----- ASSISTANT RESPONSE -----

    with st.chat_message("assistant"):

        answer_placeholder = st.empty()

        full_response = ""

        try:

            response = requests.post(
                f"{BACKEND_URL}/ask",
                json={
                    "question": question
                },
                stream=True,
                timeout=300
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

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to backend."
            )

        except requests.exceptions.Timeout:

            st.error(
                "Backend timeout. Please retry."
            )

        except Exception as e:

            st.error(str(e))

    # ----- SAVE CHAT HISTORY -----

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })