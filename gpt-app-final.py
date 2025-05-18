import openai
import streamlit as st
import os
import json
from hashlib import sha256
from pathlib import Path
from PyPDF2 import PdfReader
import pyttsx3

# ------------------------ USER AUTH ------------------------
USER_DATA_PATH = Path("user_data")
USER_DATA_PATH.mkdir(exist_ok=True)
USER_DB_FILE = USER_DATA_PATH / "users.json"
CHAT_HISTORY_DIR = USER_DATA_PATH / "chat_histories"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

if USER_DB_FILE.exists():
    with open(USER_DB_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)

def login():
    st.sidebar.header("Login / Signup")
    auth_choice = st.sidebar.radio("Choose an option", ["Login", "Signup"])

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    hashed_pw = sha256(password.encode()).hexdigest()

    if auth_choice == "Signup":
        if st.sidebar.button("Create Account"):
            if email in users:
                st.sidebar.warning("User already exists!")
            else:
                users[email] = {"password": hashed_pw}
                save_users()
                st.sidebar.success("Account created! Please login.")

    if auth_choice == "Login":
        if st.sidebar.button("Login"):
            if email in users and users[email]["password"] == hashed_pw:
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = email
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")

# Authenticate user
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ------------------------ MAIN CHATBOT ------------------------
openai.api_key = st.secrets["OPENAI_API_KEY"]
user_email = st.session_state["user_email"]
user_history_file = CHAT_HISTORY_DIR / f"{user_email.replace('@', '_at_')}.json"

if "messages" not in st.session_state:
    if user_history_file.exists():
        with open(user_history_file, "r") as f:
            st.session_state["messages"] = json.load(f)
    else:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

# ------------------------ SIDEBAR & THEME ------------------------
with st.sidebar:
    st.markdown("## 👋 Welcome")
    st.markdown(f"Hello **{user_email}**! Glad to have you back.")

    dark_mode = st.checkbox("🌙 Dark Mode", value=False)

    st.markdown("---")
    st.markdown("### ℹ️ About This App")
    st.markdown("This is an intelligent chatbot powered by OpenAI GPT. Upload a PDF or chat freely!")

    st.markdown("---")
    if st.button("🚪 Sign Out"):
        st.session_state.clear()
        st.rerun()

if dark_mode:
    st.markdown("""
        <style>
        body, .stApp { background-color: #0e1117; color: white; }
        .stTextInput > div > div > input { background-color: #1c1c1c; color: white; }
        .stTextArea textarea { background-color: #1c1c1c; color: white; }
        .stButton button { background-color: #333; color: white; }
        </style>
    """, unsafe_allow_html=True)

# ------------------------ UI LAYOUT ------------------------
st.set_page_config(page_title="ChatGPT Chatbot", page_icon="🤖")
st.title("🤖 Chat with GPT")

if st.button("🗑️ Clear Chat History"):
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    if user_history_file.exists():
        user_history_file.unlink()
    st.experimental_rerun()

uploaded_file = st.file_uploader("📄 Upload a PDF to ask questions about it", type="pdf")
file_text = ""
if uploaded_file:
    pdf = PdfReader(uploaded_file)
    for page in pdf.pages:
        file_text += page.extract_text() or ""
    st.success("PDF content loaded successfully.")

engine = pyttsx3.init()
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

for msg in st.session_state["messages"]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and st.checkbox("🔊 Read reply", key=msg["content"]):
                speak_text(msg["content"])

prompt = st.chat_input("Type your message here...")
if prompt:
    full_prompt = prompt
    if file_text:
        full_prompt = f"Here is the content of a document:\n{file_text}\n\nNow answer this question:\n{prompt}"

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=st.session_state["messages"] + [{"role": "user", "content": full_prompt}]
        )
        reply = response.choices[0].message.content
        st.markdown(reply)
        if st.checkbox("🔊 Read reply", key="latest_response"):
            speak_text(reply)

    st.session_state["messages"].append({"role": "assistant", "content": reply})

    with open(user_history_file, "w") as f:
        json.dump(st.session_state["messages"], f)
