import streamlit as st
from datetime import datetime
import time

# Set page configuration FIRST
st.set_page_config(page_title="ChatStreamlit", page_icon="💬", layout="centered")

from streamlit_chat import message
from source import streamlit_helper

# Custom CSS for professional and elegant design
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&display=swap');

:root {
    --background-dark: #0f0f0f;
    --surface-dark: #1a1a1a;
    --text-primary: #E0E0E0;
    --text-secondary: #4CAF50;
    --accent-color: #4CAF50;
    --border-radius: 16px;
}

* {
    font-family: 'JetBrains Mono', monospace !important;
}

body {
    background-color: var(--background-dark);
    color: var(--text-primary);
    line-height: 1.6;
    font-size: 16px;
}

.stApp {
    background-color: var(--background-dark);
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.message-group {
    display: flex;
    width: 100%;
    margin-bottom: 15px;
}

.message-bubble {
    max-width: 75%;
    padding: 12px 16px;
    border-radius: 18px;
    line-height: 1.4;
    position: relative;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}

.user-message-group {
    justify-content: flex-end;
}

.ai-message-group {
    justify-content: flex-start;
}

.user-bubble {
    background: linear-gradient(135deg, #2C5E1E, #4CAF50);
    color: var(--text-primary);
    border-bottom-right-radius: 4px;
}

.ai-bubble {
    background: linear-gradient(135deg, #1E1E1E, #2A2A2A);
    color: var(--text-secondary);
    border-bottom-left-radius: 4px;
}

.message-content {
    display: flex;
    flex-direction: column;
}

.message-text {
    font-size: 0.95rem;
    word-wrap: break-word;
}

.message-timestamp {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.6);
    align-self: flex-end;
    margin-top: 5px;
}

.stTitle {
    color: var(--accent-color);
    text-align: center;
    font-weight: 700;
    font-size: 2rem;
    letter-spacing: -1px;
    background: linear-gradient(90deg, var(--accent-color), #2C2C2C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stTextInput > div > div > input {
    background-color: var(--surface-dark) !important;
    color: var(--text-primary) !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    font-size: 1rem !important;
}

.stSpinner > div > div {
    border-color: var(--accent-color) transparent var(--accent-color) transparent;
}

@media (max-width: 600px) {
    .message-bubble {
        max-width: 90%;
    }
    
    .message-text {
        font-size: 0.9rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# Title with custom styling
st.markdown('<h1 class="stTitle">ChatStreamlit</h1>', unsafe_allow_html=True)

# Initialize session state variables with default values
def initialize_session_state():
    session_states = ["user_prompt_history", "chat_answer_history", "chat_history", "last_response_streamed"]
    for state in session_states:
        if state not in st.session_state:
            if state == "last_response_streamed":
                st.session_state[state] = False
            else:
                st.session_state[state] = []

initialize_session_state()

# User input with custom styling
user_input = st.chat_input("How can I help you...", key="chat_input")

if user_input:
    # Reset the last response streamed flag
    st.session_state.last_response_streamed = False
    
    with st.spinner("Retrieving, Please be patient..."):
        try:
            response = streamlit_helper(user_input, st.session_state.chat_history)
        except Exception as e:
            response = f"An error occurred: {str(e)}"

        # Append user & AI interactions to session state
        st.session_state.user_prompt_history.append(user_input)
        st.session_state.chat_answer_history.append(response)
        st.session_state.chat_history.append(("human", user_input))
        st.session_state.chat_history.append(("ai", response))

# Helper function to display a static message (user or AI)
def display_message(text, is_user=True):
    st.markdown(
        f"""
        <div class="message-group {'user-message-group' if is_user else 'ai-message-group'}">
            <div class="message-bubble {'user-bubble' if is_user else 'ai-bubble'}">
                <div class="message-content">
                    <div class="message-text">
                        {text}
                    </div>
                    <div class="message-timestamp">
                        {datetime.now().strftime("%I:%M %p")}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Display combined chat history
for i in range(len(st.session_state.user_prompt_history)):
    # 1. Show the user's message
    display_message(st.session_state.user_prompt_history[i], is_user=True)

    # 2. Determine if this is the last response & not streamed yet
    is_last_response = (i == len(st.session_state.user_prompt_history) - 1)
    
    if is_last_response and not st.session_state.last_response_streamed:
        # Stream the AI response character by character
        full_response = st.session_state.chat_answer_history[i]
        response_placeholder = st.empty()  # Single placeholder

        streamed_text = ""
        static_timestamp = datetime.now().strftime("%I:%M %p")
        for char in full_response:
            streamed_text += char
            response_placeholder.markdown(
                f"""
                <div class="message-group ai-message-group">
                    <div class="message-bubble ai-bubble">
                        <div class="message-content">
                            <div class="message-text">
                                {streamed_text}
                            </div>
                            <div class="message-timestamp">
                                {static_timestamp}
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.008)  # Adjust speed as needed

        # Mark that we've streamed this response
        st.session_state.last_response_streamed = True
    else:
        # Show the AI message in one go (already streamed before or not last)
        display_message(st.session_state.chat_answer_history[i], is_user=False)
