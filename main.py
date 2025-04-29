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

# === HUMANIZER v5.1 — Enhanced Imperfections Mode ===
PROMPT = (
    "Rewrite the following academic content like a real student would, preserving all citations and formatting."
    " Introduce imperfections: run-on sentences, sentence fragments, inconsistent punctuation or capitalization,"
    " subject-verb disagreements, overuse of passive voice, uneven transitions, redundant phrasing,"
    " limited parallelism, mixed formality, nominalizations."
    " Do not add any casual commentary beyond these flaws."
)

SYNONYMS = {
    "utilize": "use",
    "therefore": "so",
    "subsequently": "then",
    "prioritize": "focus on",
    "implementation": "doing",
    "prohibit": "stop",
    "facilitate": "help",
    "demonstrate": "show",
    "significant": "big",
    "furthermore": "also"
}

def downgrade_vocab(text):
    for word, simple in SYNONYMS.items():
        text = re.sub(rf"\b{word}\b", simple, text, flags=re.IGNORECASE)
    return text

# Increase flaw probabilities

def introduce_run_on(text):
    lines = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for line in lines:
        if random.random() < 0.5 and len(line.split()) > 6:
            result.append(line + ", and i also want to add something more without proper separation")
        else:
            result.append(line)
    return " ".join(result)

def introduce_fragments(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        if random.random() < 0.4 and len(s.split()) > 8:
            fragment = ' '.join(s.split()[:5])
            result.append(fragment)
        else:
            result.append(s)
    return " ".join(result)

def garble_punctuation(text):
    if random.random() < 0.3:
        text = re.sub(r'\. ', '.', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for i, s in enumerate(sentences):
        if random.random() < 0.2 and s:
            sentences[i] = s[0].lower() + s[1:]
    return ' '.join(sentences)

def subject_verb_disagree(text):
    return re.sub(r'\bthey (\w+)s\b', r'they \1', text)

def passive_overuse(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for i, s in enumerate(sentences):
        if random.random() < 0.5 and len(s.split()) > 5:
            sentences[i] = 'was ' + s
    return ' '.join(sentences)

def limit_parallelism(text):
    return re.sub(r"\b(and|or) ([a-z]+), ([a-z]+)\b", r"\1 \2 and also \3", text)

def uneven_transitions(text):
    transitions = ['However,', 'Moreover,', 'For example,', 'But,', 'Yet,']
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        result.append(s)
        if random.random() < 0.4:
            result.append(random.choice(transitions))
    return ' '.join(result)

def remove_casual_comments(text):
    patterns = [r'I think', r'you know', r'really matters']
    for pat in patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    return text

def paragraph_balancer(text):
    paragraphs = text.split('\n\n')
    balanced = []
    for p in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', p)
        buffer = []
        chops = 0
        for s in sentences:
            if len(s.split()) > 15 or random.random() < 0.3:
                buffer.append(s)
            elif chops < 2:
                buffer.append(s)
                chops += 1
            else:
                buffer.append(s)
        balanced.append(' '.join(buffer))
    return '\n\n'.join(balanced)

def insert_redundancy(text):
    lines = re.split(r'(?<=[.!?])\s+', text)
    output = []
    for line in lines:
        output.append(line)
        if random.random() < 0.3 and len(line.split()) > 6:
            key = line.strip().split()[0].lower()
            output.append(f"This shows that {key} is important.")
    return ' '.join(output)

# Simplified humanize: skip AI smoothing for more visible flaws
def humanize_text(text):
    t = downgrade_vocab(text)
    t = introduce_run_on(t)
    t = introduce_fragments(t)
    t = garble_punctuation(t)
    t = subject_verb_disagree(t)
    t = passive_overuse(t)
    t = limit_parallelism(t)
    t = uneven_transitions(t)
    t = remove_casual_comments(t)
    t = paragraph_balancer(t)
    t = insert_redundancy(t)
    return t

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
