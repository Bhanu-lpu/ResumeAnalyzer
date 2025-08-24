// Close welcome popup
function closePopup() {
  document.getElementById("welcomePopup").style.display = "none";
}

// Analyze Resume
async function analyzeResume() {
  let file = document.getElementById("resumeInput").files[0];
  let role = document.getElementById("roleInput").value.trim();

  if (!file || !role) {
    alert("Please upload a resume and enter a role.");
    return;
  }

  // Extract PDF text
  let text = await extractTextFromPDF(file);

  // Simple keyword matching
  let keywords = role.toLowerCase().split(" "); // basic keywords from role
  let matches = keywords.filter(kw => text.toLowerCase().includes(kw));

  let score = Math.round((matches.length / keywords.length) * 100);

  let output = `
    <h3>📊 Resume Analysis for Role: ${role}</h3>
    <p><b>Score:</b> ${score}% match</p>
    <p><b>Do’s:</b> Add more skills & projects relevant to <b>${role}</b>.</p>
    <p><b>Don’ts:</b> Avoid irrelevant details, keep resume concise.</p>
  `;

  document.getElementById("output").innerHTML = output;
}

// Extract text using PDF.js
async function extractTextFromPDF(file) {
  const pdfData = new Uint8Array(await file.arrayBuffer());
  const pdf = await pdfjsLib.getDocument(pdfData).promise;
  let text = "";

  for (let i = 1; i <= pdf.numPages; i++) {
    let page = await pdf.getPage(i);
    let content = await page.getTextContent();
    text += content.items.map(item => item.str).join(" ");
  }

  return text;
}
