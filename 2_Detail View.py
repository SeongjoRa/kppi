import streamlit as st

st.set_page_config(
    page_title="K/PP Index",
    page_icon="🧊",
    layout="wide",
)
st.write(st.session_state["greeting"])
st.header("Detail View")
st.dataframe(st.session_state['df2'], use_container_width=True)	# Display the full data