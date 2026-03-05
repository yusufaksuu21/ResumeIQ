import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")