import streamlit as st

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

is_dark = st.session_state.dark_mode
new_mode = st.toggle("🌙 Dark Mode" if is_dark else "☀️ Light Mode", value=is_dark, key="theme_toggle")

if new_mode != is_dark:
    st.session_state.dark_mode = new_mode
    st.rerun()

st.write(f"Dark mode is: {st.session_state.dark_mode}")
