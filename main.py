import streamlit as st
import openai
import random
import textstat
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "previous_inputs" not in st.session_state:
    st.session_state.previous_inputs = {}
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""

# === HUMANIZER ENGINE ===

# 1. Banned casual fillers, contractions, slang
BANNED_PHRASES = {
    "still", "this matters", "commentary",
    "don't", "can't", "won't", "it's", "you're", "they're",
    "gonna", "wanna", "kinda", "basically", "sort of", "stuff",
    "a lot", "lots of", "really", "very", "just", "quite"
}

# 2. Informal → formal substitutions
FORMAL_MAP = {
    "don't": "do not",     "can't": "cannot",  "won't": "will not",
    "it's": "it is",       "you're": "you are",
    "gonna": "going to",   "wanna": "want to",
    "kinda": "rather",     "stuff": "items",
    "a lot": "many",       "lots of": "many",
    "really": "truly",     "very": "extremely", "just": "merely",
    "basically": "fundamentally", "sort of": "somewhat"
}

def enforce_formality(sent: str) -> str:
    """Substitute informal tokens with formal equivalents."""
    for informal, formal in FORMAL_MAP.items():
        sent = re.sub(rf"\b{re.escape(informal)}\b", formal, sent, flags=re.IGNORECASE)
    return sent

def contains_banned(sent: str) -> bool:
    """Detect any banned phrase."""
    low = sent.lower()
    return any(phrase in low for phrase in BANNED_PHRASES)

def process_paragraph(par: str) -> str:
    """
    Paraphrase the entire paragraph, preserving all content, while:
      • Alternating short (6–12 words) and long (20–30 words) sentences.
      • Maintaining neutral-formal academic tone.
      • Introducing mild imperfections (e.g. occasional fragments) and minor redundancies.
      • NOT using banned fillers, slang, or contractions.
    """
    style_block = """
Rewrite the following paragraph in full (do not summarize or omit any
information), but rephrase it in a neutral-formal academic tone. Alternate
between short (6–12 words) and long (20–30 words) sentences. Introduce mild
imperfections (e.g. occasional sentence fragments) and minor redundancies
(e.g. echoing a key term once per paragraph). Do NOT use banned fillers,
slang, or contractions.
"""
    prompt = style_block + "\nOriginal paragraph:\n" + par
    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": style_block},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.75,
        max_tokens=len(par.split()) * 3
    )
    out = resp.choices[0].message.content.strip()
    out = enforce_formality(out)
    return out

def humanize_text(text: str) -> str:
    """Apply full-paragraph paraphrasing with our student-essay style rules."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    rewritten = [process_paragraph(p) for p in paras]
    return "\n\n".join(rewritten)

# === UI (v4.4 layout with v4.5 label) ===

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
    score = round(textstat.flesch_reading_ease(edited_output), 1)
    st.markdown(f"**📊 Output Word Count:** {words} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; **🧠 Readability Score:** {score}%")

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
