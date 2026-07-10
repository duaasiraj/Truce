"""
app.py
Routing entry point: login gate, then dispatch by role.
Each real page lives in ui/pages/ -- this file only wires them together.
"""
import streamlit as st

from ui.theme import apply_theme
from auth.session import is_logged_in, current_user, logout
from ui.pages import login as login_page
from ui.pages import client_dashboard, freelancer_dashboard

st.set_page_config(page_title="Truce", page_icon=":handshake:", layout="wide")

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"

apply_theme(st.session_state["theme_mode"])

if not is_logged_in():
    login_page.render()
    st.stop()

user = current_user()

with st.sidebar:
    st.markdown(f"**{user['name']}**")
    st.caption(user["role"].title())
    if st.button("Log Out"):
        logout()
        st.rerun()

if user["role"] == "client":
    client_dashboard.render()
else:
    freelancer_dashboard.render()