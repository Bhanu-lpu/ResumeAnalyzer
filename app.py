from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import PyPDF2
import os
import google.generativeai as genai
from pdf2image import convert_from_bytes
import pytesseract

import json
import requests
from dotenv import load_dotenv
load_dotenv()  # ✅ this will load your .env file


app = Flask(__name__, template_folder="backend/templates", static_folder="backend/static")

CORS(app)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # put your key in .env file
# Homepage route
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/privacypolicy")
def privacypolicy():
    return render_template("privacypolicy.html")
from flask import Response

@app.route("/robots.txt")
def robots_txt():
    return Response("User-agent: *\nAllow: /", mimetype="text/plain")

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_pdf(file):
    """Extract text from uploaded PDF with fallback OCR for scanned PDFs"""
    file.seek(0)
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""

    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        file.seek(0)
        images = convert_from_bytes(file.read())
        for img in images:
            ocr_text = pytesseract.image_to_string(img)
            text += ocr_text + "\n"

    return text

# ------------------------------
# ✅ ATS Analyzer Function
# ------------------------------
def ats_analyze_resume(resume_text, role="Software Engineer"):
    score = 0
    feedback = []

    # ✅ 1. Check for key resume sections
    sections = ["Education", "Skills", "Experience", "Projects"]
    for section in sections:
        if section.lower() in resume_text.lower():
            score += 10
        else:
            feedback.append(f"Missing section: {section}")

    # ✅ 2. Keyword check (example role-specific keywords)
    job_keywords = {
        "Software Engineer": ["Python", "Java", "SQL", "API", "Machine Learning"],
        "Data Scientist": ["Python", "Statistics", "Machine Learning", "Pandas", "Deep Learning"],
        "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"]
    }

    keywords = job_keywords.get(role, ["Teamwork", "Communication", "Problem Solving"])
    missing_keywords = [kw for kw in keywords if kw.lower() not in resume_text.lower()]

    if missing_keywords:
        feedback.append(f"Missing keywords: {', '.join(missing_keywords)}")
    else:
        score += 20

    # ✅ 3. Formatting checks (avoid images/tables)
    if len(resume_text.split()) < 200:
        feedback.append("Your resume seems too short. Add more details.")
    else:
        score += 10

    # ✅ Final score capped at 100
    final_score = min(score, 100)

    return {
        "score": final_score,
        "feedback": feedback
    }


@app.route("/analyze", methods=["POST"])
def analyze():
    role = request.form.get("role", "Software Engineer")
    file = request.files.get("resume")

    if not file:
        return jsonify({"analysis": "❌ No file uploaded!"})

    resume_text = extract_text_from_pdf(file)
    if not resume_text.strip():
        return jsonify({"analysis": "❌ No text found in PDF!"})

    prompt = f"""
You are a career coach. Analyze this resume for the role of {role}.
Resume:
{resume_text}

Give feedback in 3 sections (concise, max 3 bullet points per section):
1. Strengths
2. Weaknesses
3. Suggestions (Do's & Don'ts)
Use short sentences or bullet points suitable for students.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Return raw text (no escaping)
        return jsonify({"analysis": response.text})

    except Exception as e:
        return jsonify({"analysis": f"❌ Error generating feedback: {str(e)}"})
    

@app.route("/ats", methods=["POST"])
def ats():
    role = request.form.get("role", "Software Engineer")
    file = request.files.get("resume")

    if not file:
        return jsonify({"error": "❌ No file uploaded!"})

    resume_text = extract_text_from_pdf(file)
    if not resume_text.strip():
        return jsonify({"error": "❌ No text found in PDF!"})

    result = ats_analyze_resume(resume_text, role)

    return jsonify(result)

    
@app.route("/api/announcements")
def api_announcements():
    try:
        with open("backend/announcements.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify([])

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json["message"]

    # Create model instance
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Generate reply
    response = model.generate_content(user_msg)

    return jsonify({"reply": response.text})
@app.route("/faq")
def faq():
    return render_template("faq.html")
@app.route("/blog")
def blog():
    return render_template("blog.html")




@app.route("/test", methods=["POST"])
def test():
    return jsonify({"message": "✅ POST request received successfully!"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
