# AI Study Buddy 📚

A simple AI-powered study assistant built for the Notes-to-Quiz assignment.

## Features
- Paste notes or upload a text-based PDF.
- Generate a 5–6 point summary.
- Create five multiple-choice questions with answers and explanations.
- Explain three important terms in simple language.
- Download the summary as a text file.

## Tech stack
- Python
- Streamlit
- Google Gemini API
- pypdf

## Run locally
1. Install Python 3.10 or newer.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`
4. Enter your Gemini API key in the app sidebar. Get a key at https://aistudio.google.com/apikey.

## Keep your API key safe
- Do not paste your API key into `app.py`.
- Do not upload `.streamlit/secrets.toml` or `.env` to GitHub.
- `.gitignore` excludes the real secrets file.
- For Streamlit Community Cloud, add secrets through the app's Settings → Secrets page if you configure the app to read Streamlit secrets.

## Note
AI output can contain mistakes. Check generated answers against your original class notes.
