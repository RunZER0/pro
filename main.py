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

def downgrade_vocab(text):
    for word, replacement in SYNONYMS.items():
        text = re.sub(rf"\b{word}\b", replacement, text, flags=re.IGNORECASE)
    return text

def light_split(text):
    return re.sub(r'(?<=[.!?])\s+(?=[A-Z])', '. ', text)

def split_into_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())

def add_sentence_variation(sentences):
    new_sentences = []
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 18 and random.random() < 0.5:
            parts = re.split(r'(,| and | but )', sentence)
            chunks = []
            current = ""
            for part in parts:
                current += part
                if len(current.split()) > 10:
                    chunks.append(current.strip())
                    current = ""
            if current:
                chunks.append(current.strip())
            new_sentences.extend(chunks)
        elif len(words) < 6 and random.random() < 0.4:
            if new_sentences:
                new_sentences[-1] += ' ' + sentence
            else:
                new_sentences.append(sentence)
        else:
            new_sentences.append(sentence)
    return new_sentences

def add_professional_redundancy(sentences):
    clarifiers = [
        "This means that {}.",
        "As a result, {}.",
        "{} This could affect other operations.",
        "{} This highlights the importance of clarity."
    ]
    enhanced = []
    for sentence in sentences:
        enhanced.append(sentence)
        if random.random() < 0.25 and len(sentence.split()) > 8:
            phrased = random.choice(clarifiers).format(sentence.rstrip('.'))
            enhanced.append(phrased)
    return enhanced

def post_process_text(text):
    sentences = split_into_sentences(text)
    varied = add_sentence_variation(sentences)
    redundant = add_professional_redundancy(varied)
    return ' '.join(redundant)

def humanize_text(text):
    simplified = downgrade_vocab(text)
    prepped = light_split(simplified)

    # Strict, professional GPT prompt
    system_prompt = (
        "You are a language transformation engine that rewrites technical or robotic text into clear, plain English. "
        "Your output must:\n"
        "- Maintain a professional and neutral tone\n"
        "- Avoid conversational or casual phrasing (no 'you', 'we', 'let’s', etc.)\n"
        "- Remove unnecessary jargon\n"
        "- Preserve the original meaning exactly\n"
        "- Use sentence structures that feel natural, with light variation\n"
        "- Avoid fillers like 'in other words', 'basically', etc.\n"
        "- Do not summarize or interpret the text\n"
        "The tone should be similar to a technical report or official documentation."
    )

    user_prompt = f"Rewrite the following text clearly and professionally:\n\n{prepped}"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    processed = post_process_text(result)
    return re.sub(r'\n{2,}', '\n\n', processed)

# === Streamlit UI ===
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

st.markdown("**Version 4.5 — Custom Professional Humanizer**")
st.markdown("---")
st.markdown("""
<div class='features-grid'>
    <div class='feature'>
        <strong>✍️ Natural Cadence:</strong><br>
        Your words flow like a real human writer — no AI rigidity.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🔁 Structured Variance:</strong><br>
        Sentence rhythm feels natural, not machine-generated.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>📚 Professional Clarity:</strong><br>
        Clear, technical tone without jargon or chatty phrasing.
    </div>
</div>
""", unsafe_allow_html=True)
