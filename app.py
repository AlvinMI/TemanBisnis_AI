import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

st.set_page_config(page_title="Teman Bisnis AI", page_icon="💼")
st.title("💼 Teman Bisnis AI")
st.write("Partner diskusi bisnismu dari nol sampai sukses!")

if not api_key:
    st.error("Waduh, API Key Groq belum ada di file .env nih!")
else:
    llm = ChatGroq(model_name="llama3-70b-8192", groq_api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Tanya apa saja soal bisnis..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        response = llm.invoke(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.content})
        st.chat_message("assistant").write(response.content)