from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# ✅ Add homepage route here
@app.route("/", methods=["GET"])
def home():
    return "Resume Analyzer Backend (Gemini) is running 🚀"

# ✅ Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(file):
    """Extract text from uploaded PDF"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

@app.route("/analyze", methods=["POST"])
def analyze():
    role = request.form.get("role", "Software Engineer")
    file = request.files.get("resume")

    if not file:
        return jsonify({"analysis": "No file uploaded!"})

    resume_text = extract_text_from_pdf(file)

    prompt = f"""
You are a career coach. Analyze this resume for the role of {role}.
Resume:
{resume_text}

Give feedback in 3 sections (keep it very concise, 3 bullet points max per section):
1. Strengths
2. Weaknesses
3. Suggestions (Do's & Don'ts)
Use short sentences or bullet points suitable for students.
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # ✅ Make JSON-safe
    safe_text = response.text.replace("\n", "\\n").replace('"', '\\"')
    return jsonify({"analysis": safe_text})


@app.route("/test", methods=["POST"])
def test():
    return jsonify({"message": "POST request received successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
