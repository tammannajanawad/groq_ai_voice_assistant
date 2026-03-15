import streamlit as st


def init_session():

    defaults = {
        "messages": [],
        "tokens": 0,
        "response_times": [],
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def trim_history(max_turns):

    st.session_state.messages = st.session_state.messages[-max_turns * 2 :]