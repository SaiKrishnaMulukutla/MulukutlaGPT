import streamlit as st
import requests

API_KEY = st.secrets["THE_API_KEY"]
MODEL = "openai/gpt-3.5-turbo"

st.set_page_config(page_title="MulukutlaGPT", page_icon="🧠")

st.title("MulukutlaGPT🧬 — Personalised AI Assistance!!")
st.write("💬 Introducing personalized AI-powered chat assistant designed to help you get quick, intelligent, and helpful responses. Built with advanced GPT-3.5-turbo models, it delivers smooth, reliable conversations in real-time.😊")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Namaste! How can I help you today?"}]

def send_message(user_message):
    st.session_state.messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": st.session_state.messages
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    else:
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {response.text}"})

def render_message(role, content):
    if role == "user":
        st.markdown(f"""
            <div style="text-align: right; margin: 10px 0;">
                <div style="
                    display: inline-block;
                    background-color: #007bff;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 20px 20px 0 20px;
                    max-width: 70%;
                    word-wrap: break-word;
                    box-shadow: 0 2px 5px rgb(0 123 255 / 0.4);
                ">
                    {content}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="text-align: left; margin: 10px 0;">
                <div style="
                    display: inline-block;
                    background-color: #e5e5ea;
                    color: #000;
                    padding: 12px 16px;
                    border-radius: 20px 20px 20px 0;
                    max-width: 70%;
                    word-wrap: break-word;
                    box-shadow: 0 2px 5px rgb(0 0 0 / 0.1);
                ">
                    {content}
                </div>
            </div>
        """, unsafe_allow_html=True)

with st.form("user_input_form", clear_on_submit=True):
    user_text = st.text_area("Your message:", "", max_chars=1000, key="input_area", height=100)
    submitted = st.form_submit_button("Send")

    if submitted and user_text.strip():
        send_message(user_text.strip())

for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

st.markdown("---")
st.markdown("<p style='text-align: center;'>Created with ❤️ by Mulukutla Sai Krishna</p>", unsafe_allow_html=True)
