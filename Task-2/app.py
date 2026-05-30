import os
from pathlib import Path

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv


# ----------------------------
# Load .env from parent folder
# ----------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in .env file")
    st.stop()


# ----------------------------
# Configure Gemini
# ----------------------------
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(
    page_title="AI Faculty Assistant",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Faculty Assistant")
st.write(
    "Enter a topic and generate teaching content automatically."
)

topic = st.text_input(
    "Enter Topic",
    placeholder="Example: Artificial Intelligence in Education"
)


# ----------------------------
# Generate Content
# ----------------------------
if st.button("Generate Content", type="primary"):

    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    prompt = f"""
You are an expert faculty assistant.

Generate educational content for the topic:

{topic}

Provide the output in the following format:

## Learning Objectives
Generate exactly 3 learning objectives.

## Lecture Outline
Generate a structured lecture outline with major headings and subtopics.

## Multiple Choice Questions (MCQs)
Generate exactly 5 MCQs.

For each MCQ provide:
- Question
- A)
- B)
- C)
- D)
- Correct Answer

## Topic Summary
Generate a concise summary of 150-200 words.
"""

    with st.spinner("Generating content..."):

        try:
            response = model.generate_content(prompt)

            st.success("Content Generated Successfully")

            st.markdown("---")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Error: {e}")


# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Future Ready Faculty AI Boot Camp - Assessment Task")