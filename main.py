import streamlit as st
import openai
import random
import textstat # Keep for readability score
import re

# --- OpenAI API Key Setup ---
# Fetches the key from Streamlit secrets
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key not found in Streamlit secrets. Please add it.")
    st.stop()
except Exception as e:
    st.error(f"Error setting up OpenAI API key: {e}")
    st.stop()

# --- Session State Initialization ---
if "human_output" not in st.session_state:
    st.session_state.human_output = ""
if "last_input_text" not in st.session_state: # Retain for potential re-humanize logic
    st.session_state.last_input_text = ""

# === NEW HUMANIZER ENGINE v5.0 ===

GPT_MODEL = "gpt-4o"

def call_gpt_humanizer(system_message, user_prompt, temperature=0.6, max_tokens=2000):
    """
    Generalized function to call OpenAI API for the humanizer stages.
    """
    try:
        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None # Or raise the exception

def stage1_deconstruct_and_simplify(text):
    """
    Breaks down complex text, simplifies vocabulary, and introduces basic naturalness.
    """
    system_message = (
        "You are an expert text simplifier. Your task is to make academic or formal text "
        "easier to understand by breaking it down and using more common language, "
        "while preserving the original meaning and detail. Avoid sounding robotic."
    )
    prompt = (
        f"Please process the following text:\n\n\"\"\"\n{text}\n\"\"\"\n\n"
        "Apply these transformations:\n"
        "1.  Identify and replace overly formal vocabulary (e.g., 'utilize' with 'use', 'subsequently' with 'then', 'commence' with 'start') and common AI phrases (e.g., 'it is paramount to', 'delve into', 'the landscape of') with simpler, more natural alternatives. Do not just use a fixed dictionary; understand context.\n"
        "2.  Break down long, complex sentences into shorter, more direct sentences. Aim for clarity.\n"
        "3.  Introduce common contractions (e.g., 'it's', 'don't', 'can't') where they fit naturally.\n"
        "4.  Convert passive voice to active voice where it improves directness and flow.\n"
        "5.  Ensure the core meaning, all original ideas, and details are fully preserved.\n"
        "Output only the processed text."
    )
    # st.write("DEBUG: Stage 1 Prompt:", prompt) # For debugging
    return call_gpt_humanizer(system_message, prompt, temperature=0.4, max_tokens=len(text.split())*3 + 100) # Estimate tokens

def stage2_structural_and_rhythmic_variation(text):
    """
    Introduces human-like sentence structure and rhythm variations.
    """
    system_message = (
        "You are a writing style enhancer. Your task is to take simplified text and make it "
        "flow more like natural human writing by varying sentence structure and rhythm, "
        "without making it sound overly polished or artificial."
    )
    prompt = (
        f"Take the following text, which has already been simplified:\n\n\"\"\"\n{text}\n\"\"\"\n\n"
        "Now, apply these stylistic variations:\n"
        "1.  Vary sentence lengths significantly: Mix short, punchy sentences (3-7 words) with medium sentences (10-15 words), and include 1-2 well-placed longer sentences (20-25 words) per paragraph for better readability and flow, if appropriate for the content. Avoid a monotonous rhythm.\n"
        "2.  Introduce slight, natural-sounding repetition of 1-2 key phrases or ideas if it helps with emphasis or mimics how a person might reiterate a point for clarity. Do not overdo this.\n"
        "3.  Occasionally re-order clauses within a sentence or the order of 1-2 sentences if it breaks up a too-perfectly-logical flow and reflects a more natural, human thought progression. The overall logic must remain clear.\n"
        "4.  Ensure the text reads smoothly but not robotically. It should feel like a human drafted it, with some natural unevenness in pacing.\n"
        "Output only the processed text."
    )
    # st.write("DEBUG: Stage 2 Prompt:", prompt)
    return call_gpt_humanizer(system_message, prompt, temperature=0.6, max_tokens=len(text.split())*3 + 100)

def stage3_idiosyncrasy_and_human_voice(text):
    """
    Injects subtle human-like imperfections, discourse markers, and a target voice.
    Simulates a "college student with average fluency and effort."
    """
    system_message = (
        "You are a writing persona emulator. Your task is to make text sound as if it were written by a "
        "college student with average fluency and effort – thoughtful but not overly polished or perfect. "
        "The goal is to avoid sounding like a sophisticated AI or a professional writer."
    )
    prompt = (
        f"The following text has been simplified and structurally varied. Now, infuse it with the voice of a 'college student with average fluency and effort':\n\n\"\"\"\n{text}\n\"\"\"\n\n"
        "Apply these subtle changes:\n"
        "1.  Add 2-3 natural discourse markers or mild fillers (e.g., 'Well,', 'So,', 'You know,', 'Actually,', 'I mean,', 'Kind of like'). Integrate them smoothly, where a student might pause or transition thought.\n"
        "2.  Introduce 1-2 very subtle, *plausible* 'imperfections' or slightly informal turns of phrase. This could be a slightly less common (but still correct) word choice where a simpler one was used before, a phrase that's a bit more conversational, or a sentence structure that's a little less 'tidy'. The text should still be grammatically correct and clear. The aim is to reduce 'robotic perfection'. For example, instead of 'The data shows...', perhaps 'So, looking at the data, it seems like...'.\n"
        "3.  Ensure the tone reflects focused effort but not professional eloquence. It should sound like someone who understands the material but is still in the process of mastering formal academic writing. Avoid sounding too casual or too sophisticated.\n"
        "4.  If there are very short, choppy sentences from previous stages, try to connect one or two of them if it makes the thought flow more like a student piecing ideas together, but don't make it too smooth.\n"
        "5.  Do NOT add new information or explain concepts. Preserve the original ideas and details.\n"
        "Output only the processed text."
    )
    # st.write("DEBUG: Stage 3 Prompt:", prompt)
    return call_gpt_humanizer(system_message, prompt, temperature=0.75, max_tokens=len(text.split())*3 + 100) # Higher temp for voice

def stage4_final_polish_and_evasion_check(text):
    """
    A final pass to refine human-likeness and check for remaining AI tells, from the perspective of an AI detector.
    """
    system_message = (
        "You are an AI writing style critic and editor, specializing in making text indistinguishable from human writing. "
        "Your task is to review text and make final, very subtle tweaks to eliminate any remaining AI-like patterns. "
        "You are trying to make it pass an AI detector."
    )
    prompt = (
        f"Review the following text, which has been through several humanization stages. Your goal is to make it sound even more authentically human-written and less like AI:\n\n\"\"\"\n{text}\n\"\"\"\n\n"
        "1.  Read the text critically. Do any phrases, sentence structures, or transitions still feel a bit too 'perfect', too balanced, or characteristic of AI writing (even sophisticated AI)?\n"
        "2.  If so, apply 1-3 very subtle, final tweaks. These could be: \n"
        "    a. Changing one or two words to slightly less common but still natural synonyms to vary word choice in an unexpected way.\n"
        "    b. Slightly altering the rhythm of one sentence.\n"
        "    c. Ensuring transitions between sentences are natural and not overly signposted (e.g., remove 'however' if a simpler contrast works).\n"
        "3.  The changes should be almost unnoticeable individually but collectively enhance the human feel.\n"
        "4.  Do NOT introduce errors. Do NOT change the core meaning or add/remove information.\n"
        "5.  The output should be only the finally polished text. If you believe no further changes are needed to enhance human-likeness, return the input text as is.\n"
    )
    # st.write("DEBUG: Stage 4 Prompt:", prompt)
    return call_gpt_humanizer(system_message, prompt, temperature=0.5, max_tokens=len(text.split())*3 + 100)

def humanize_text_engine_v5(text_input):
    """
    The main multi-stage humanizing engine.
    """
    if not text_input.strip():
        return ""

    # Estimate initial token count for progress bar, very roughly
    # total_steps = 4
    # progress_bar = st.progress(0)
    # current_step = 0

    # def update_progress():
    #     nonlocal current_step
    #     current_step += 1
    #     progress_bar.progress(current_step / total_steps)

    st.write("🚀 Stage 1: Deconstructing & Simplifying...")
    s1_output = stage1_deconstruct_and_simplify(text_input)
    if s1_output is None: return "Error in Stage 1."
    # update_progress()
    st.write("✅ Stage 1 Complete.")

    st.write("🚀 Stage 2: Varying Structure & Rhythm...")
    s2_output = stage2_structural_and_rhythmic_variation(s1_output)
    if s2_output is None: return "Error in Stage 2."
    # update_progress()
    st.write("✅ Stage 2 Complete.")

    st.write("🚀 Stage 3: Injecting Human Voice & Idiosyncrasies...")
    s3_output = stage3_idiosyncrasy_and_human_voice(s2_output)
    if s3_output is None: return "Error in Stage 3."
    # update_progress()
    st.write("✅ Stage 3 Complete.")

    st.write("🚀 Stage 4: Final Polish & Evasion Check...")
    s4_output = stage4_final_polish_and_evasion_check(s3_output)
    if s4_output is None: return "Error in Stage 4."
    # update_progress()
    st.write("✅ Stage 4 Complete. Humanization finished!")
    
    # progress_bar.empty() # Clear progress bar

    # Clean up potential multiple newlines that GPT sometimes adds
    final_text = re.sub(r'\n{3,}', '\n\n', s4_output).strip()
    return final_text

# === UI (v4.4 layout with v4.5 label, adapted for new engine) ===
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

st.markdown('<div class="centered-container"><h1>🤖 InfiniAi-Humanizer v5</h1><p>Turn robotic AI text into real, natural, human-sounding writing.</p></div>', unsafe_allow_html=True)

input_text = st.text_area("Paste your AI-generated academic text below (Max: ~1500 words / 8000 chars for stability):", height=280, max_chars=8000, key="input_text_area")

# Character and word count for input
input_char_count = len(input_text)
input_word_count = len(input_text.split())
st.markdown(f"**Input Stats: {input_word_count} Words, {input_char_count} Characters**")

if input_char_count > 8000:
    st.warning("⚠️ Input is over 8000 characters. Processing may be slow or unstable. Consider shortening.")


if st.button("🔁 Humanize Text", key="humanize_button"):
    if input_text.strip():
        # Update last_input_text for potential re-humanization logic if needed
        st.session_state.last_input_text = input_text 
        
        # Use an empty placeholder for the humanizing messages and output
        status_placeholder = st.empty()
        output_placeholder = st.empty()

        with st.spinner("⚙️ Kicking off humanization engine... This might take a moment..."):
            # Clear previous status messages from placeholder
            status_placeholder.empty() 
            
            # The humanize_text_engine_v5 now uses st.write for status,
            # so we ensure they appear within a controlled area if possible, or just flow.
            # For a cleaner UI, you might pass the placeholder to the engine to write into.
            output = humanize_text_engine_v5(input_text)
        
        if output and not output.startswith("Error in Stage"):
            st.session_state.human_output = output
            st.success("🎉 Humanization complete!")
        elif output.startswith("Error in Stage"):
            st.error(f"An error occurred during humanization: {output}")
        else:
            st.error("Humanization failed or returned empty. Please check API status or input.")

    else:
        st.warning("Please enter some text first.")

if st.session_state.human_output:
    st.markdown("---")
    st.markdown("### ✍️ Humanized Output")
    # Provide a key to the output text_area to allow updates
    edited_output = st.text_area("Edit your result below:", value=st.session_state.human_output, height=300, key="edited_output_area")
    
    # If the user edits the text area, update the session state
    if edited_output != st.session_state.human_output:
        st.session_state.human_output = edited_output
        # Optionally, rerun stats if text changes
        # st.experimental_rerun() 

    output_char_count = len(st.session_state.human_output)
    output_word_count = len(st.session_state.human_output.split())
    
    # Calculate readability score safely
    readability_score_text = "N/A"
    if st.session_state.human_output.strip(): # textstat needs non-empty string
        try:
            score = round(textstat.flesch_reading_ease(st.session_state.human_output), 1)
            readability_score_text = f"{score}%"
        except Exception as e:
            # st.caption(f"Could not calculate readability: {e}") #
            pass

st.markdown("---")
st.markdown("**Engine Version 5.0**")
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

<div class='features-grid' style='margin-top:1rem;'>
    <div class='comment' style='width: 45%;'>
        <em>"This actually sounds like I wrote it after a long study night."</em><br><strong>- Joseph</strong>
    </div>
    <div class='vertical-divider'></div>
    <div class='comment' style='width: 45%;'>
        <em>"Passed the AI check with flying colors. And my professor said it felt authentic."</em><br><strong>- Kate</strong>
    </div>
</div>
""", unsafe_allow_html=True)