import streamlit as st
import openai
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "previous_inputs" not in st.session_state:
    st.session_state.previous_inputs = {}
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""
if "total_words_used" not in st.session_state:
    st.session_state.total_words_used = 0

# === HUMANIZER v5.0 — Precision Academic Standard ===
PROMPT = (
    "Rewrite the following academic text to match a natural human writing style."
    " Maintain a formal, neutral academic tone."
    " Structure paragraphs logically: clear topic sentence, expansion, evidence, commentary, transition."
    " Alternate sentence length: short (6–12 words), medium (12–20 words), long (20–35 words)."
    " No more than two short or two long sentences in a row."
    " Integrate natural transitions (such as 'however', 'thus', 'for example')."
    " Insert slight purposeful redundancy for emphasis (but no random choppy fragments)."
    " Always use active voice primarily, passive voice only if needed for flow."
    " Use clear and accessible vocabulary (mid-academic), avoiding slang and overly advanced terms."
    " Do not add new information. Do not invent or remove citations."
    " Ensure the writing feels authentic, serious, and clearly human, suitable for academic purposes."
)

ACADEMIC_VOCAB_SIMPLIFY = {
    "utilize": "use",
    "subsequently": "then",
    "prioritize": "focus on",
    "facilitate": "help",
    "demonstrate": "show",
    "prohibit": "stop",
    "implement": "carry out",
    "significant": "important",
    "endeavor": "effort",
    "ameliorate": "improve",
    "commence": "begin",
}

def simplify_vocabulary(text):
    for complex_word, simple_word in ACADEMIC_VOCAB_SIMPLIFY.items():
        text = re.sub(rf'\b{complex_word}\b', simple_word, text, flags=re.IGNORECASE)
    return text

def enforce_sentence_structure(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    final_sentences = []
    last_length_type = None
    count_same_type = 0

    for sentence in sentences:
        word_count = len(sentence.split())

        if word_count <= 12:
            length_type = "short"
        elif word_count <= 20:
            length_type = "medium"
        else:
            length_type = "long"

        if last_length_type == length_type:
            count_same_type += 1
        else:
            count_same_type = 1
            last_length_type = length_type

        if count_same_type > 2:
            if length_type == "short":
                sentence = sentence + " Thus, it becomes clear."
            elif length_type == "long":
                parts = sentence.split(",")
                if len(parts) > 1:
                    sentence = parts[0] + ". " + ",".join(parts[1:])

            count_same_type = 1

        final_sentences.append(sentence.strip())

    return " ".join(final_sentences)

def humanize_text(text):
    simplified_text = simplify_vocabulary(text)
    structured_text = enforce_sentence_structure(simplified_text)

    full_prompt = f"{PROMPT}\n\n{structured_text}\n\nRewrite following the above instructions precisely."

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.5,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return result

# === UI (Unchanged) ===
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

current_count = len(input_text.split())
if st.session_state.total_words_used + current_count > 700:
    st.error("🚫 Trial limit reached: You’ve used your 700-word quota. Please upgrade to Pro for unlimited access.")
    st.stop()

if st.button("🔁 Humanize / Re-Humanize Text"):
    if input_text.strip():
        trimmed_input = input_text[:10000]
        with st.spinner("Humanizing academic text..."):
            output = humanize_text(trimmed_input)
            st.session_state.human_output = output
            st.session_state.last_input_text = trimmed_input
            st.session_state.total_words_used += len(trimmed_input.split())
    else:
        st.warning("Please enter some text first.")

if st.session_state.human_output:
    st.markdown("### ✍️ Humanized Output")
    edited_output = st.text_area("Edit your result below:", value=st.session_state.human_output, height=300)
    st.session_state.human_output = edited_output

    import textstat
    words = len(edited_output.split())
    score = round(textstat.flesch_reading_ease(edited_output), 1)
    st.markdown(f"**📊 Output Word Count:** {words} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; **🧠 Readability Score:** {score}%")

    st.download_button("💾 Download Output", data=edited_output, file_name="humanized_output.txt", mime="text/plain")

st.markdown("**Version 5.0**")
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
""", unsafe_allow_html=True)
