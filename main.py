import streamlit as st
import openai
import random # Keep if you plan to use it for other things
import textstat
import re

# --- OpenAI API Key Setup ---
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
if "last_input_text" not in st.session_state:
    st.session_state.last_input_text = ""

# === NEW HUMANIZER ENGINE v5.1 - "Disruptor Mode" ===

GPT_MODEL = "gpt-4o" 

def call_gpt_humanizer_v5_1(system_message, user_prompt, temperature=0.7, max_tokens_ratio=2.5):
    """
    Generalized function to call OpenAI API for the humanizer stages.
    max_tokens_ratio: Multiplier for input length to estimate max_tokens.
    """
    # Calculate max_tokens based on prompt length to give ample space for rewriting
    # A simple word count of the user_prompt part containing the text to be rewritten.
    # This is a rough estimate.
    num_input_words = len(user_prompt.split()) # Rough estimate
    estimated_max_tokens = int(num_input_words * max_tokens_ratio) + 200 # Base + buffer
    if estimated_max_tokens > 4000: # Cap to avoid excessive token usage/cost for very long inputs
        estimated_max_tokens = 4000


    try:
        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=estimated_max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        # Log the error for debugging
        print(f"OpenAI API Error: {e}")
        print(f"System Message: {system_message}")
        print(f"User Prompt (first 100 chars): {user_prompt[:100]}")
        return None

def stage1_deep_rephrase_and_structure_overhaul(text_input):
    st.write("🚀 Stage 1: Deep Rephrasing & Structural Overhaul...")
    system_message = (
        "You are a master rewriter specializing in transforming formal, academic, or AI-generated text into "
        "something that sounds fundamentally different in structure and vocabulary, while meticulously preserving "
        "the original meaning and all details. Your goal is to make the text unrecognizable from its original phrasing."
    )
    prompt = (
        f"Completely rephrase and restructure the following text. Your main goal is to make it sound as if "
        f"written by a different person with a simpler, more direct style. Preserve ALL original ideas and details.\n\n"
        f"Follow these strict instructions:\n"
        f"1.  **Radical Rephrasing:** Do not use any of the original text's key phrases or sentence structures if possible. Change almost every sentence.\n"
        f"2.  **Vocabulary Simplification:** Aggressively replace formal, academic, or complex words with common, everyday equivalents. For example, 'utilize' becomes 'use,' 'commence' becomes 'start,' 'myriad' becomes 'many.'\n"
        f"3.  **Structural Breakdown:** Break down long, multi-clause sentences into several shorter, simpler sentences. Aim for an average sentence length that is noticeably shorter than typical academic text.\n"
        f"4.  **Active Voice & Directness:** Convert passive voice to active voice. Make statements direct and clear.\n"
        f"5.  **Contractions:** Integrate common contractions (it's, don't, isn't, we're, they're) naturally throughout the text.\n"
        f"6.  **Eliminate AI-isms:** Remove phrases like 'it is important to note,' 'furthermore,' 'in conclusion,' 'the intricate tapestry of,' 'delve into,' 'navigating the complex landscape of.'\n"
        f"7.  **Preserve Meaning Absolutely:** This is critical. The rephrased text must convey the exact same information, arguments, and nuances as the original, just in a completely different style.\n\n"
        f"Original Text:\n\"\"\"\n{text_input}\n\"\"\"\n\n"
        f"Completely Rephrased and Simplified Text (preserving all original meaning and details):\n"
    )
    output = call_gpt_humanizer_v5_1(system_message, prompt, temperature=0.5, max_tokens_ratio=2.0)
    if output: st.write("✅ Stage 1 Complete.")
    return output

def stage2_inject_average_student_voice(text_from_stage1):
    st.write("🚀 Stage 2: Injecting 'Average Student' Voice & Idiosyncrasies...")
    system_message = (
        "You are a writing style emulator. Your specific persona is an 'average college student' who is "
        "articulate but not a professional writer. The student tries their best, and their writing is clear, "
        "but it lacks polish and might have some common student-like writing habits. "
        "Your goal is to make the text sound authentically like this student wrote it."
    )
    prompt = (
        f"Take the following simplified text and rewrite it in the distinct voice of an 'average college student'. "
        f"This student understands the material but their writing isn't perfect or overly sophisticated. "
        f"Preserve ALL original ideas and details from the input text.\n\n"
        f"Input Text (already simplified):\n\"\"\"\n{text_from_stage1}\n\"\"\"\n\n"
        f"Follow these guidelines to achieve the 'average college student' voice:\n"
        f"1.  **Sentence Length & Flow:** Use a mix of sentence lengths. Include some short, direct sentences, some medium ones, and occasionally a slightly longer sentence that might feel a little run-on (but is still grammatically understandable). The flow should feel natural for a student, not perfectly crafted.\n"
        f"2.  **Discourse Markers/Fillers:** Add 2-4 common, subtle discourse markers or filler phrases that a student might use when thinking through their writing. Examples: 'So,', 'Well,', 'I mean,', 'You know,', 'Like,', 'Basically,', 'It's kind of like...'. Integrate them naturally, not awkwardly.\n"
        f"3.  **Slightly Less Direct Phrasing (Occasional):** For 1-2 ideas, rephrase them in a way that's a bit less direct or more explanatory, as if the student is ensuring their point is understood or thinking it through. For example, 'The results were clear.' might become 'So, when you look at the results, it was pretty clear that...'.\n"
        f"4.  **Word Choice:** Stick to common vocabulary. If the input text still has any complex words, simplify them further. Avoid sounding overly academic or using jargon unless it's absolutely essential and the input implied a student would know it.\n"
        f"5.  **Repetition (Subtle):** A student might subtly repeat a key idea or phrase for emphasis, or when transitioning. If appropriate, introduce this once or twice, very naturally.\n"
        f"6.  **Avoid Polish:** Do NOT make the text sound smooth, elegant, or professionally edited. It should have a touch of 'student effort' — clear, but not perfect. No sophisticated transitions like 'Furthermore' or 'Nevertheless' unless the input text strongly implies their necessity and simplicity.\n"
        f"7.  **Maintain All Original Information:** Critically important. No new ideas, no summarization, no loss of detail.\n\n"
        f"Rewritten Text (in the voice of an average college student):\n"
    )
    output = call_gpt_humanizer_v5_1(system_message, prompt, temperature=0.75, max_tokens_ratio=2.5) # Higher temp for voice
    if output: st.write("✅ Stage 2 Complete.")
    return output

def stage3_final_human_polish_and_evasion(text_from_stage2):
    st.write("🚀 Stage 3: Final 'Human Polish' & Evasion Tweaks...")
    system_message = (
        "You are an expert at making AI text sound completely human, specifically like it was written by an average, "
        "non-expert human (e.g., a student). Your final task is to review the provided text and apply very subtle "
        "changes to eliminate any remaining hints of AI-like perfection or unnatural phrasing. The goal is maximum human authenticity."
    )
    prompt = (
        f"This text has been processed to sound like an average college student. Now, perform a final 'human polish' "
        f"to make it even more authentically human and less detectable as AI. Preserve ALL original ideas and details.\n\n"
        f"Text to Polish:\n\"\"\"\n{text_from_stage2}\n\"\"\"\n\n"
        f"Apply 1-3 of the following *very subtle* tweaks ONLY if you detect any remaining AI-like smoothness or perfection. If it already sounds authentically 'average student,' make minimal or no changes:\n"
        f"1.  **Word Order Variation (One Sentence Max):** Slightly alter the word order in one sentence to make it sound less 'perfectly constructed,' without making it ungrammatical. Example: 'The experiment clearly showed the effect.' to 'The effect, well, the experiment showed it pretty clearly.'\n"
        f"2.  **Slightly Awkward but Natural Phrasing (One Instance Max):** Introduce one very minor phrase that feels a tiny bit informal or 'spoken' rather than 'written,' characteristic of an average student. Example: 'This is important because...' to 'The thing is, this is important because...'\n"
        f"3.  **Pacing Adjustment (One Instance Max):** If a section flows too smoothly, consider breaking one sentence into two shorter ones, or connect two very short ones with a simple conjunction like 'and' or 'so,' to vary the pacing in a slightly less optimized way.\n"
        f"4.  **Vocabulary Nuance (One Word Max):** Change one common word to another common, but perhaps slightly less 'default' or 'AI-preferred' synonym that a student might plausibly choose. E.g., 'big' instead of 'significant' if 'significant' still feels too formal for the student voice.\n"
        f"Remember, these are final, *extremely subtle* tweaks. The text should primarily retain the 'average student' character. "
        f"The goal is to disrupt any lingering predictability that AI detectors might pick up on. "
        f"Output ONLY the finally polished text.\n\n"
        f"Final Polished Text:\n"
    )
    output = call_gpt_humanizer_v5_1(system_message, prompt, temperature=0.6, max_tokens_ratio=1.5) # Lower temp for subtle polish
    if output: st.write("✅ Stage 3 Complete.")
    return output

def humanize_text_engine_v5_1(text_input):
    """
    The main multi-stage humanizing engine - Disruptor Mode.
    """
    if not text_input.strip():
        return ""

    s1_out = stage1_deep_rephrase_and_structure_overhaul(text_input)
    if not s1_out: return "Error in Stage 1: No output received or API call failed."

    s2_out = stage2_inject_average_student_voice(s1_out)
    if not s2_out: return "Error in Stage 2: No output received or API call failed."
    
    s3_out = stage3_final_human_polish_and_evasion(s2_out)
    if not s3_out: return "Error in Stage 3: No output received or API call failed."

    st.success("🎉 Humanization complete!")
    final_text = re.sub(r'\n{3,}', '\n\n', s3_out).strip() # Clean up extra newlines
    return final_text

# === UI (Mostly unchanged from your v4.5, just updated version number and engine call) ===
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

st.markdown('<div class="centered-container"><h1>🤖 InfiniAi-Humanizer v5.1</h1><p>Turn robotic AI text into real, natural, human-sounding writing (Disruptor Mode).</p></div>', unsafe_allow_html=True)

input_text = st.text_area("Paste your AI-generated academic text below (Max: ~1000 words / 6000 chars for stability):", height=280, max_chars=6000, key="input_text_area_v5_1")

input_char_count = len(input_text)
input_word_count = len(input_text.split())
st.markdown(f"**Input Stats: {input_word_count} Words, {input_char_count} Characters**")

if input_char_count > 6000: # Reduced max_chars for stability with more complex prompts
    st.warning("⚠️ Input is over 6000 characters. Processing may be slow, unstable, or hit token limits. Consider shortening.")

if st.button("🔁 Humanize Text", key="humanize_button_v5_1"):
    if input_text.strip():
        st.session_state.last_input_text = input_text
        
        # Placeholder for status messages (optional, as st.write is now inside engine)
        # status_placeholder = st.empty()

        with st.spinner("⚙️ Engaging Humanizer Engine v5.1... This may take some time..."):
            output = humanize_text_engine_v5_1(input_text)
        
        if output and not output.lower().startswith("error in stage"):
            st.session_state.human_output = output
            # No success message here, it's in the engine now.
        elif output and output.lower().startswith("error in stage"):
            st.error(f"An error occurred: {output}")
            st.session_state.human_output = "" # Clear previous output on error
        else:
            st.error("Humanization failed or returned an empty result. Please check API status or input text. If the input is very short, the engine might struggle.")
            st.session_state.human_output = "" # Clear previous output on error
    else:
        st.warning("Please enter some text first.")

if st.session_state.human_output:
    st.markdown("---")
    st.markdown("### ✍️ Humanized Output")
    edited_output = st.text_area("Edit your result below:", value=st.session_state.human_output, height=300, key="edited_output_area_v5_1")
    
    if edited_output != st.session_state.human_output:
        st.session_state.human_output = edited_output

    output_char_count = len(st.session_state.human_output)
    output_word_count = len(st.session_state.human_output.split())
    
    readability_score_text = "N/A"
    if st.session_state.human_output.strip():
        try:
            score = round(textstat.flesch_reading_ease(st.session_state.human_output), 1)
            readability_score_text = f"{score}%"
        except Exception:
            pass

    st.markdown(f"**📊 Output Stats: {output_word_count} Words, {output_char_count} Characters    |    🧠 Readability Score (Flesch):** {readability_score_text}")
    st.download_button("💾 Download Output", data=st.session_state.human_output, file_name="humanized_output_v5_1.txt", mime="text/plain", key="download_button_v5_1")

st.markdown("---")
st.markdown("**Engine Version 5.1 (Disruptor Mode)**")
st.markdown("""
<div class='features-grid'>
    <div class='feature'>
        <strong>⚠️ Aggressive De-Optimization:</strong><br>
        Actively disrupts AI polish and predictability for a more raw, human feel.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🗣️ "Average Student" Voice:</strong><br>
        Mimics the cadence and minor imperfections of typical student writing.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🎲 Increased Randomness:</strong><br>
        Aims for less predictable word choices and sentence structures.
    </div>
</div>

<div class='features-grid' style='margin-top:1rem;'>
    <div class='comment' style='width: 45%;'>
        <em>"Feels less 'perfect' and more like something I'd actually turn in."</em><br><strong>- Student A</strong>
    </div>
    <div class='vertical-divider'></div>
    <div class='comment' style='width: 45%;'>
        <em>"The 'student voice' is noticeable. Hope this tricks the detectors better!"</em><br><strong>- Student B</strong>
    </div>
</div>
""", unsafe_allow_html=True)