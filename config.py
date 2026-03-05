import streamlit as st
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = st.secrets.get("AIzaSyAMmzhQARIo-qgOb6RBA_ZyldW354Ts7oU") or os.getenv("AIzaSyAMmzhQARIo-qgOb6RBA_ZyldW354Ts7oU")