import streamlit as st
import openai
import re
import textstat

openai.api_key = st.secrets["OPENAI_API_KEY"]

if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "previous_inputs" not in st.session_state:
    st.session_state.previous_inputs = {}
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""
if "total_words_used" not in st.session_state:
    st.session_state.total_words_used = 0

# === HUMANIZER ENGINE (rebuilt carefully to match user's examples) ===

PROMPT = (
    "Rewrite the following academic text to match real student-level writing, based on provided examples."
    " Maintain formal but accessible academic tone."
    " Structure paragraphs logically with a clear topic sentence, development, evidence, and conclusion."
    " Alternate naturally between short (6–12 words), medium (12–20 words), and long (20–35 words) sentences."
    " Avoid stacking more than two of the same length in a row."
    " Allow mild repetition or slight rephrasing for emphasis, as seen in real student writing."
    " Use accessible academic vocabulary without slang or ultra-complex words."
    " Insert simple natural transitions (thus, because, however) without mechanical overuse."
    " Preserve all original citations and factual content. No invention of new information."
    " Ensure slight imperfections and a natural thoughtful rhythm, like a real student essay."
)

ACADEMIC_VOCAB_SIMPLIFY = {
    "utilize": "use",
    "subsequently": "then",
    "prioritize": "focus on",
    "implementation": "process",
    "prohibit": "prevent",
    "facilitate": "help",
    "demonstrate": "show",
    "significant": "important",
    "ameliorate": "improve",
    "commence": "begin",
    "therefore": "thus",
    "furthermore": "also"
}

def simplify_vocabulary(text):
    for complex_word, simple_word in ACADEMIC_VOCAB_SIMPLIFY.items():
        text = re.sub(rf'\b{complex_word}\b', simple_word, text, flags=re.IGNORECASE)
    return text

def enforce_sentence_structure(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    final_sentences = []
    last_length_type = None
    same_type_count = 0

    for sentence in sentences:
        word_count = len(sentence.split())

        if word_count <= 12:
            length_type = "short"
        elif word_count <= 20:
            length_type = "medium"
        else:
            length_type = "long"

        if length_type == last_length_type:
            same_type_count += 1
        else:
            same_type_count = 1
            last_length_type = length_type

        if same_type_count > 2:
            if length_type == "short":
                sentence = sentence + " This idea supports the main point."
            elif length_type == "long":
                parts = sentence.split(", ")
                if len(parts) > 1:
                    sentence = parts[0] + ". " + ", ".join(parts[1:])
            same_type_count = 1

        final_sentences.append(sentence.strip())

    return " ".join(final_sentences)

def humanize_text(text):
    simplified_text = simplify_vocabulary(text)
    structured_text = enforce_sentence_structure(simplified_text)

    full_prompt = f"{PROMPT}\n\n{structured_text}\n\nRewrite following the above instructions carefully."

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.4,
        max_tokens=1600
    )

    result = response.choices[0].message.content.strip()
    return result

# === UI (Unchanged from original) ===

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

    words = len(edited_output.split())
    score = round(textstat.flesch_reading_ease(edited_output), 1)
    st.markdown(f"**📊 Output Word Count:** {words} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; **🧠 Readability Score:** {score}%")

    st.download_button("💾 Download Output", data=edited_output, file_name="humanized_output.txt", mime="text/plain")

st.markdown("**Version 5.0 — Real Student Academic Mode**")
st.markdown("---")
st.markdown("""
<div class='features-grid'>
    <div class='feature'>
        <strong>✍️ Natural Cadence:</strong><br>
        Words flow like a real, thinking student.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🔁 Structured Variance:</strong><br>
        Paragraphs breathe with short and long sentences naturally.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>📚 Academic Realism:</strong><br>
        Tone matches thoughtful university-level work — not polished editorials.
    </div>
</div>
""", unsafe_allow_html=True)
