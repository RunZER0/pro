import streamlit as st
import openai
import random
import textstat
import re

# Set OpenAI API key via Streamlit secret
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Session states for persistence
if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "previous_inputs" not in st.session_state:
    st.session_state.previous_inputs = {}
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""

# === Vocabulary simplification dictionary ===
SYNONYMS = {
    "utilize": "use",
    "therefore": "so",
    "subsequently": "then",
    "prioritize": "focus on",
    "implementation": "doing",
    "prohibit": "stop",
    "facilitate": "help",
    "demonstrate": "show",
    "significant": "important",
    "furthermore": "also",
    "approximately": "about",
    "individuals": "people",
    "components": "parts",
    "eliminate": "remove",
    "require": "need",
    "crucial": "important",
    "complex": "complicated",
    "vehicle": "car",
    "performance": "how it works",
    "enhanced": "better",
    "transmitting": "moving",
    "torsional": "twisting",
}

def humanize_text(text):
    prepped = text

    # Strict, professional GPT prompt
    system_prompt = """
You are a rewriting system designed to simplify text in a way that sounds like a non-native English speaker writing clearly but imperfectly. Your output should be understandable and structured, but slightly awkward or clunky. Follow these rules:

1. Use simple, clear vocabulary. Replace complex or decorative words with basic words.
2. Rewrite long or complex sentences into shorter, easier sentences. Use some variety.
3. Use words like "also", "besides", "as well as", "next to", and "along with" instead of "and", even if slightly awkward.
4. Allow small grammar errors or odd phrasing. The tone should feel like a person with decent but imperfect English skills.
5. Keep technical terms if they are needed. Avoid too much repetition.
6. Use hyphens sometimes for listing related ideas, but not excessively.
7. Avoid elegant transitions. The text can feel a bit flat or clunky.
8. Use full sentences most of the time. Avoid sentence fragments.
9. Sound slightly repetitive and unnatural — but still human, not robotic.
10. Do not over-polish. It should feel like a student who writes clearly, but with odd grammar and phrasing.

Always follow these rules. No exceptions. Do not attempt to polish the output.
"""

    user_prompt = f""" Rewrite the following text using the defined rules.

Example Input:
The war caused brutal damage across many cities. Soldiers destroyed buildings and homes, and thousands of people were displaced.

Example Output:
The war brought damage with cruelty to many cities. Buildings were destroyed by soldiers - homes too. Thousands of people faced displacement.

Example Output:
The war brought damage with cruelty to many cities. Buildings were destroyed by soldiers - homes too. Thousands of people faced displacement.

Text to humanize:
{prepped}
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return re.sub(r'\n{2,}', '\n\n', result)

# === UI (Updated: No pre/post-processing dependencies) ===
st.markdown("""
<style>
.stApp { background-color: #0d0d0d; color: #00ffff; font-family: 'Segoe UI', monospace; text-align: center; }
textarea { background-color: #121212 !important; color: #ffffff !important; border: 1px solid #00ffff !important; border-radius: 8px !important; font-size: 16px !important; }
.stButton > button { background-color: #00ffff; color: black; font-weight: bold; border: none; padding: 0.6rem 1.2rem; border-radius: 8px; transition: all 0.3s ease-in-out; }
.stButton > button:hover { background-color: #00cccc; transform: scale(1.03); }
.stDownloadButton button { background-color: #00ffff; color: black; font-weight: bold; border-radius: 5px; }
.centered-container { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.features-grid { display: flex; justify-content: space-around; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #00ffff; }
.feature, .comment { width: 30%; text-align: left; font-size: 14px; }
.vertical-divider { border-left: 1px solid #00ffff; height: 100%; margin: 0 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="centered-container"><h1>🤖 InfiniAi-Humanizer</h1><p>Turn robotic AI text into real, natural, human-sounding writing.</p></div>', unsafe_allow_html=True)

input_text = st.text_area("Paste your AI-generated academic text below (Max: 10,000 characters):", height=280, max_chars=10000)

if len(input_text) > 10000:
    st.warning("⚠️ Your input is over 10,000 characters. Only the first 10,000 characters will be used.")
st.markdown(f"**{len(input_text.split())} Words, {len(input_text)} Characters**")

if st.button("🔁 Humanize / Re-Humanize Text"):
    if input_text.strip():
        trimmed_input = input_text[:10000]
        with st.spinner("Humanizing academic text..."):
            output = humanize_text(trimmed_input)
            st.session_state.human_output = output
            st.session_state.last_input_text = trimmed_input
    else:
        st.warning("Please enter some text first.")

if st.session_state.human_output:
    st.markdown("### ✍️ Humanized Output")
    edited_output = st.text_area("Edit your result below:", value=st.session_state.human_output, height=300)
    st.session_state.human_output = edited_output

    words = len(edited_output.split())
    st.markdown(f"**📊 Output Word Count:** {words}")

    st.download_button("💾 Download Output", data=edited_output, file_name="humanized_output.txt", mime="text/plain")

st.markdown("**Version 4.5**")
st.markdown("---")
st.markdown("""
<div class='features-grid'>
    <div class='feature'>
        <strong>✍️ Natural Cadence:</strong><br>
        Your words flow like a real student — no rigid AI rhythm.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🔁 Structured Variance:</strong><br>
        Paragraphs are well balanced for human clarity.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>📚 Academic Realism:</strong><br>
        The tone mimics thoughtful effort, not perfect computation.
    </div>
</div>

<div class='features-grid'>
    <div class='comment'>
        <em>"This actually sounds like I wrote it after a long study night."</em><br><strong>- Joseph</strong>
    </div>
    <div class='comment'>
        <em>"Passed the AI check with flying colors. And my professor said it felt authentic."</em><br><strong>- Kate</strong>
    </div>
</div>
""", unsafe_allow_html=True)

