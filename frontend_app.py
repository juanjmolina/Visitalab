import streamlit as st
import requests

API = "http://localhost:8000"

st.title("VisitaLab PRO")

if st.button("Test API"):
    r = requests.get(API)
    st.write(r.json())
