import openai
import streamlit as st
from PyPDF2 import PdfReader

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="ChatGPT Chatbot", page_icon="🤖")
st.title("🤖 Chat with GPT")

# Load PDF content if uploaded
uploaded_file = st.file_uploader("📄 Upload a PDF to ask questions about it", type="pdf")
file_text = ""
if uploaded_file:
    pdf = PdfReader(uploaded_file)
    for page in pdf.pages:
        file_text += page.extract_text() or ""
    st.success("PDF content loaded successfully.")

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]

# Clear chat history button
if st.button("🗑️ Clear Chat History"):
    st.session_state["messages"] = [{"role": "system", "content": "You are a helpful assistant."}]
    st.experimental_rerun()

# Display previous messages
for msg in st.session_state["messages"]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# User input prompt
prompt = st.chat_input("Type your message here...")
if prompt:
    # Combine PDF content and user prompt if PDF loaded
    full_prompt = f"Here is the content of a document:\n{file_text}\n\nNow answer this question:\n{prompt}" if file_text else prompt

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from OpenAI
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state["messages"] + [{"role": "user", "content": full_prompt}]
    )
    reply = response.choices[0].message.content

    st.session_state["messages"].append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
