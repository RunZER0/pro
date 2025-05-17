import streamlit as st
import openai
# import random # Not currently used, can be removed if not planned
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

# === NEW HUMANIZER ENGINE v5.2 - "Authentic Student Cadence" ===

GPT_MODEL = "gpt-4o"

def call_gpt_humanizer_v5_2(system_message, user_prompt, temperature=0.4, max_tokens_ratio=2.0): # Lowered default temp
    num_input_words = len(user_prompt.split())
    estimated_max_tokens = int(num_input_words * max_tokens_ratio) + 250 # Slightly increased buffer
    if estimated_max_tokens > 7500: # Increased cap slightly for gpt-4o
        estimated_max_tokens = 7500
    if estimated_max_tokens < 300: # Minimum tokens
        estimated_max_tokens = 300


    try:
        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=estimated_max_tokens,
            # top_p=0.9 # Consider experimenting with top_p as well
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        print(f"OpenAI API Error: {e}")
        return None

def stage1_core_extraction_and_radical_simplification(text_input):
    st.write("🚀 Stage 1: Core Idea Extraction & Radical Simplification...")
    system_message = (
        "You are an expert in deconstructing text. Your task is to break down the provided text into its most fundamental, "
        "individual factual statements or claims. You must aggressively simplify vocabulary and sentence structure."
    )
    prompt = (
        f"Analyze the following text. Your goal is to extract every distinct piece of information and rewrite it as a separate, "
        f"very short, simple, declarative sentence using basic, common English vocabulary. Avoid all academic jargon, complex phrasing, and transitional words. "
        f"If an original sentence contains multiple ideas, break it into multiple distinct simple sentences.\n\n"
        f"Strict Instructions:\n"
        f"1.  **Isolate Facts:** Identify each core fact, observation, or argument.\n"
        f"2.  **Ultra-Simple Sentences:** Rewrite each isolated fact as its own sentence. Sentences should ideally be 5-10 words long. Some can be shorter.\n"
        f"3.  **Basic Vocabulary:** Replace ALL complex, formal, or academic words with their simplest, most common equivalents (e.g., 'demonstrates' -> 'shows', 'significant' -> 'big' or 'important', 'utilize' -> 'use').\n"
        f"4.  **No Transitions/Conjunctions (Initially):** Do not use words like 'however,' 'therefore,' 'furthermore,' or even complex conjunctions like 'although' at this stage. Just list the simple facts.\n"
        f"5.  **Active Voice:** Use active voice predominantly.\n"
        f"6.  **Preserve All Core Meaning:** Every piece of original information must be retained, just broken down and simplified.\n\n"
        f"Original Text:\n\"\"\"\n{text_input}\n\"\"\"\n\n"
        f"Output (a series of very short, simple, factual sentences, each on a new line for clarity if it helps, or just spaced out):\n"
    )
    output = call_gpt_humanizer_v5_2(system_message, prompt, temperature=0.2, max_tokens_ratio=1.8) # Very low temp for precision
    if output: st.write("✅ Stage 1 Complete.")
    return output

def stage2_reaggregation_with_student_cadence(text_from_stage1, original_subject_hint="The text discusses"):
    st.write("🚀 Stage 2: Re-aggregating with 'Student Cadence' & Repetition...")
    system_message = (
        "You are a writing assistant that reconstructs lists of simple facts into paragraphs that sound like they were written by an "
        "average college student. This student is clear but not overly polished, and their writing has a direct, somewhat repetitive cadence when discussing the same topic. "
        "They use simple language and sentence structures."
    )
    prompt = (
        f"Take the following list of simple, factual statements (derived from a more complex text). Your task is to weave them into coherent paragraphs that "
        f"sound like an average college student wrote them. The student often repeats the main subject when starting new sentences about that subject.\n\n"
        f"List of Simplified Facts:\n\"\"\"\n{text_from_stage1}\n\"\"\"\n\n"
        f"Guidelines for 'Average College Student' Style:\n"
        f"1.  **Paragraphing:** Group related facts into short paragraphs.\n"
        f"2.  **Subject Repetition:** When discussing the same main entity or concept (e.g., a person's name, a specific theory, 'the study') over several sentences, frequently start those sentences by restating that subject. For example: 'BigXThePlug does X. BigXThePlug also looks for Y. His choices help him with Z.' Avoid excessive pronoun use if direct subject repetition fits this style.\n"
        f"3.  **Sentence Structure:** Keep most sentences short and declarative (Subject-Verb-Object). Occasionally, a slightly longer sentence (max 15-20 words) can be formed by joining two very closely related simple ideas with 'and,' 'but,' or 'so.'\n"
        f"4.  **Simple Transitions:** Use only very basic transitions IF ABSOLUTELY NEEDED (e.g., 'Also,', 'Then,', 'But,', 'So,'). Often, no transition is needed between closely related sentences that repeat the subject.\n"
        f"5.  **Vocabulary:** Maintain simple, common vocabulary. If any complex words remain from the input, simplify them.\n"
        f"6.  **Tone:** Direct, informative, like a student explaining what they've learned. Not elegant, not conversational with fillers, not overly academic or fluent.\n"
        f"7.  **Preserve All Information:** Ensure every fact from the input list is incorporated into the paragraphs.\n\n"
        f"Reconstructed Paragraphs (Student Cadence):\n"
    )
    # Temperature slightly higher to allow for some natural sentence joining
    output = call_gpt_humanizer_v5_2(system_message, prompt, temperature=0.45, max_tokens_ratio=2.2)
    if output: st.write("✅ Stage 2 Complete.")
    return output

def stage3_final_authenticity_pass(text_from_stage2):
    st.write("🚀 Stage 3: Final Authenticity Pass (Subtle Imperfections & Flow)...")
    system_message = (
        "You are a final-pass editor. Your task is to review text written in an 'average college student' style and ensure it doesn't "
        "accidentally sound too polished or AI-like. You should make it sound even more authentically unrefined, without introducing actual errors."
    )
    prompt = (
        f"Review the following text, which is already written to mimic an average college student. Your goal is to make subtle adjustments "
        f"to enhance its 'unrefined' human authenticity and reduce any remaining AI-like smoothness or predictability. "
        f"Preserve ALL original ideas and details.\n\n"
        f"Text for Final Review:\n\"\"\"\n{text_from_stage2}\n\"\"\"\n\n"
        f"Apply these subtle checks and adjustments IF NEEDED:\n"
        f"1.  **Sentence Flow & Choppiness:** Ensure there's a good mix of short, declarative sentences. If some sentences became too long or complex in the previous stage, break them down again. The text should feel direct and somewhat staccato in places, reflecting focused but not highly skilled writing.\n"
        f"2.  **Vocabulary Check:** One last check for any words that sound too sophisticated for an 'average student' and replace them with simpler alternatives.\n"
        f"3.  **Subject Repetition Check:** Confirm that the main subject is appropriately repeated in consecutive related sentences, reinforcing the direct, slightly unvaried style. If pronouns were overused, consider reverting to subject repetition.\n"
        f"4.  **Avoid Over-Polishing:** If any phrasing sounds too 'perfect,' 'elegant,' or 'fluent,' simplify it or make it slightly more blunt. For example, a smooth transition might be removed if simple juxtaposition works.\n"
        f"5.  **Slight Awkwardness (Highly Subtle):** ONLY if the text is still too smooth: consider one very minor rephrasing that introduces a tiny, natural-sounding awkwardness that isn't ungrammatical but just less 'optimized'. This could be a slightly less common but still understandable way to phrase something simple. Be extremely cautious with this.\n"
        f"The goal is a text that is clear, conveys all information, but has the hallmarks of genuine student effort rather than AI perfection. "
        f"Output ONLY the finally adjusted text.\n\n"
        f"Final Adjusted Text:\n"
    )
    output = call_gpt_humanizer_v5_2(system_message, prompt, temperature=0.3, max_tokens_ratio=1.5)
    if output: st.write("✅ Stage 3 Complete.")
    return output


def humanize_text_engine_v5_2(text_input):
    if not text_input.strip():
        return ""

    s1_out = stage1_core_extraction_and_radical_simplification(text_input)
    if not s1_out: return "Error in Stage 1: No output received or API call failed."

    s2_out = stage2_reaggregation_with_student_cadence(s1_out)
    if not s2_out: return "Error in Stage 2: No output received or API call failed."
    
    s3_out = stage3_final_authenticity_pass(s2_out)
    if not s3_out: return "Error in Stage 3: No output received or API call failed."

    st.success("🎉 Humanization complete!")
    final_text = re.sub(r'\n{2,}', '\n', s3_out).strip() # Ensure single newlines between sentences if GPT adds more
    final_text = re.sub(r'\n \n', '\n\n', final_text) # Consolidate paragraph breaks
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

st.markdown('<div class="centered-container"><h1>🤖 InfiniAi-Humanizer v5.2</h1><p>Turn robotic AI text into authentic student writing (Cadence Mode).</p></div>', unsafe_allow_html=True)

input_text = st.text_area("Paste your AI-generated academic text below (Max: ~800 words / 5000 chars for stability):", height=280, max_chars=5000, key="input_text_area_v5_2")

input_char_count = len(input_text)
input_word_count = len(input_text.split())
st.markdown(f"**Input Stats: {input_word_count} Words, {input_char_count} Characters**")

if input_char_count > 5000: 
    st.warning("⚠️ Input is over 5000 characters. Processing may be slow, unstable, or hit token limits. Consider shortening.")

if st.button("🔁 Humanize Text", key="humanize_button_v5_2"):
    if input_text.strip():
        st.session_state.last_input_text = input_text
        with st.spinner("⚙️ Engaging Humanizer Engine v5.2... This requires careful thought..."):
            output = humanize_text_engine_v5_2(input_text)
        
        if output and not output.lower().startswith("error in stage"):
            st.session_state.human_output = output
        elif output and output.lower().startswith("error in stage"):
            st.error(f"An error occurred: {output}")
            st.session_state.human_output = ""
        else:
            st.error("Humanization failed or returned an empty result. Check API status, input text length, or try again.")
            st.session_state.human_output = ""
    else:
        st.warning("Please enter some text first.")

if st.session_state.human_output:
    st.markdown("---")
    st.markdown("### ✍️ Humanized Output")
    edited_output = st.text_area("Edit your result below:", value=st.session_state.human_output, height=300, key="edited_output_area_v5_2")
    
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
    st.download_button("💾 Download Output", data=st.session_state.human_output, file_name="humanized_output_v5_2.txt", mime="text/plain", key="download_button_v5_2")

st.markdown("---")
st.markdown("**Engine Version 5.2 (Authentic Student Cadence)**")
st.markdown("""
<div class='features-grid'>
    <div class='feature'>
        <strong>🧱 Deconstructed Flow:</strong><br>
        Mimics how students build arguments—direct, sometimes repetitive, less polished.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🗣️ True Student Voice:</strong><br>
        Cadence and word choice reflect genuine student effort, not AI perfection.
    </div>
    <div class='vertical-divider'></div>
    <div class='feature'>
        <strong>🎯 Detector Evasion Focus:</strong><br>
        Specifically targets patterns AI detectors look for by embracing 'unrefined' authenticity.
    </div>
</div>
<div class='features-grid' style='margin-top:1rem;'>
    <div class='comment' style='width: 45%;'>
        <em>"This is much closer to how I actually write my first drafts."</em><br><strong>- Alex P.</strong>
    </div>
    <div class='vertical-divider'></div>
    <div class='comment' style='width: 45%;'>
        <em>"The choppiness and directness feels more like me. Less robotic for sure."</em><br><strong>- Samira K.</strong>
    </div>
</div>
""", unsafe_allow_html=True)