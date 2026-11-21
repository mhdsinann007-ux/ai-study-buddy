import json
import time
import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

st.set_page_config(page_title="AI Study Buddy", page_icon="📚", layout="wide")
st.title("📚 AI Study Buddy")
st.write("Turn your study notes into summaries, practice quizzes, and key-term explanations.")

with st.sidebar:
    st.header("Settings")
    saved_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    entered_key = st.text_input("Google Gemini API key", type="password",
                                help="Paste a valid key from Google AI Studio. Never share it publicly.")
    api_key = entered_key.strip() or str(saved_key).strip()
    model = st.selectbox("Gemini model", ["gemini-3.8-flash"])
    st.markdown("[Create or check your API key in Google AI Studio](https://aistudio.google.com/apikey)")
    st.caption("You can enter the key here, or save GEMINI_API_KEY in Streamlit app Secrets.")

method = st.radio("Add your study material", ["Paste notes", "Upload PDF"], horizontal=True)
notes = ""
if method == "Paste notes":
    notes = st.text_area("Paste your notes here", height=240)
else:
    file = st.file_uploader("Upload a text-based PDF", type=["pdf"])
    if file:
        try:
            reader = PdfReader(file)
            notes = "\n".join(page.extract_text() or "" for page in reader.pages)
            st.success(f"Loaded {len(reader.pages)} page(s).")
        except Exception as exc:
            st.error(f"Could not read PDF: {exc}")

if st.button("✨ Generate my study pack", type="primary", use_container_width=True):
    if not api_key.strip():
        st.error("Enter your Gemini API key in the sidebar.")
    elif len(notes.strip()) < 50:
        st.error("Please provide at least a few sentences of notes.")
    else:
        prompt = """
Use ONLY the notes below. Return valid JSON with:
- summary: 5 or 6 short bullet points
- quiz: 5 multiple-choice questions, each with four options, correct_answer, and explanation
- key_terms: 3 terms, each with a simple meaning
Do not invent facts not supported by the notes.
JSON format:
{"summary":["..."],"quiz":[{"question":"...","options":["A","B","C","D"],"correct_answer":"A","explanation":"..."}],"key_terms":[{"term":"...","meaning":"..."}]}
NOTES:
""" + notes[:30000]
        try:
            with st.spinner("Preparing your study pack..."):
                client = genai.Client(api_key=api_key.strip())
                response = None
                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model=model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.3,
                                response_mime_type="application/json"
                            )
                        )
                        break
                    except Exception as api_error:
                        error_text = str(api_error)
                        is_temporary = "503" in error_text or "UNAVAILABLE" in error_text
                        if not is_temporary or attempt == 2:
                            raise
                        wait_seconds = 3 * (2 ** attempt)
                        st.warning(f"Gemini is busy. Retrying in {wait_seconds} seconds...")
                        time.sleep(wait_seconds)

                st.session_state["pack"] = json.loads(response.text)
        except Exception as exc:
            error_text = str(exc)
            if "API_KEY_INVALID" in error_text or "API key not valid" in error_text:
                st.error("Your Gemini API key is invalid. Open Google AI Studio, create or copy a valid API key, then paste it into the API key box in the sidebar. Check that there are no extra spaces. Do not paste your key into GitHub or this chat.")
                st.markdown("[Open Google AI Studio API keys](https://aistudio.google.com/apikey)")
            else:
                st.error(f"Could not generate the study pack: {exc}")

pack = st.session_state.get("pack")
if pack:
    st.divider()
    summary_tab, quiz_tab, terms_tab = st.tabs(["📝 Summary", "🎯 Quiz", "📖 Key Terms"])
    with summary_tab:
        st.subheader("Quick summary")
        summary = pack.get("summary", [])
        for number, point in enumerate(summary, 1):
            st.markdown(f"**{number}.** {point}")
        st.download_button("Download summary", "\n".join(summary),
                           file_name="study_summary.txt", mime="text/plain")
    with quiz_tab:
        st.subheader("Test your understanding")
        quiz = pack.get("quiz", [])
        for i, question in enumerate(quiz):
            st.markdown(f"**Q{i+1}. {question.get('question', '')}**")
            st.radio("Choose an answer", question.get("options", []),
                     key=f"answer_{i}", index=None, label_visibility="collapsed")
        if st.button("Check answers"):
            score = 0
            for i, question in enumerate(quiz):
                chosen = st.session_state.get(f"answer_{i}")
                correct = question.get("correct_answer")
                if chosen == correct:
                    score += 1
                    st.success(f"Q{i+1}: Correct! {question.get('explanation', '')}")
                else:
                    st.info(f"Q{i+1}: Correct answer: {correct}. {question.get('explanation', '')}")
            st.metric("Your score", f"{score} / {len(quiz)}")
    with terms_tab:
        st.subheader("Important terms")
        for item in pack.get("key_terms", []):
            with st.container(border=True):
                st.markdown(f"**{item.get('term', 'Term')}**")
                st.write(item.get("meaning", ""))

st.caption("Built with Streamlit and Google Gemini. Always verify AI-generated answers with your class notes.")
