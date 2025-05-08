import streamlit as st
from openai import OpenAI
import textstat

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state
if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "previous_inputs" not in st.session_state:
    st.session_state.previous_inputs = {}
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""

# === AI-Powered Humanizer v6.0 ===
def humanize_text(text: str) -> str:
    system_prompt = """
You are an expert academic humanizer. Given AI-generated scholarly text as input, transform it into natural, human-like prose that evades AI detectors. Apply the following manipulations unpredictably and with human-like inconsistency:

1. Sentence-Length Variation:
   - Alternate between long, clause-rich sentences (20+ words) and short, punchy statements (≤8 words).
   - Never use more than two sentences of similar length consecutively.

2. Punctuation & Spacing:
   - Vary commas, semicolons, em-dashes, and ellipses.
   - Introduce occasional extra or missing spaces around punctuation, random line breaks after short sentences, and errant double spaces.

3. Lexical & Register Shifts:
   - Replace common words with synonyms in about 25% of instances.
   - Switch between third-person and first-person voice sporadically.
   - Inject colloquial phrases (“you see”, “to be honest”, “at the end of the day”) intermittently.

4. Stylistic Flourishes:
   - Insert genuine rhetorical questions after complex ideas.
   - Use parenthetical asides and bracketed footnote markers randomly.

5. Human Imperfections:
   - Seed ~1 minor typo per 200 words (e.g. “teh” for “the”).
   - Include occasional split infinitives or dangling modifiers.
   - Introduce minor capitalization inconsistencies.

6. Thematic Cohesion:
   - Ensure all insertions remain on-topic, reinforcing rather than distracting.
   - Emphasize key points as a real writer would.

Return ONLY the transformed text—no explanations or metadata.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": text}
        ],
        temperature=0.75,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

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

st.markdown(
    '<div class="centered-container"><h1>🤖 InfiniAi-Humanizer</h1>'
    '<p>Turn robotic AI text into real, natural, human-sounding writing.</p></div>',
    unsafe_allow_html=True
)

input_text = st.text_area(
    "Paste your AI-generated academic text below (Max: 10,000 characters):",
    height=280,
    max_chars=10000
)

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
    edited_output = st.text_area(
        "Edit your result below:",
        value=st.session_state.human_output,
        height=300
    )
    st.session_state.human_output = edited_output

    words = len(edited_output.split())
    score = round(textstat.flesch_reading_ease(edited_output), 1)
    st.markdown(
        f"**📊 Output Word Count:** {words} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; **🧠 Readability Score:** {score}%"
    )

    st.download_button(
        "💾 Download Output",
        data=edited_output,
        file_name="humanized_output.txt",
        mime="text/plain"
    )

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
