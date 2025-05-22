from flask import Flask, render_template_string, request, jsonify
import os
from openai import OpenAI
from datetime import datetime

app = Flask(__name__)

# Initialize OpenAI for advanced chatbot capabilities
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Johns Hopkins Stroke Risk Scoring System
def calculate_stroke_risk(data):
    score = 0
    details = []
    
    # Stroke Symptoms (2 points each)
    if data.get('facial_droop') == 'yes':
        score += 2
        details.append("Facial droop detected (+2)")
    if data.get('arm_weakness') == 'yes':
        score += 2
        details.append("Arm weakness detected (+2)")
    if data.get('speech_difficulty') == 'yes':
        score += 2
        details.append("Speech difficulty detected (+2)")
    
    # Time Since Onset (1 point if >3 hours)
    try:
        onset = int(data.get('onset_time', 0))
        if onset > 3:
            score += 1
            details.append("Symptom onset > 3 hrs (+1)")
    except:
        pass
    
    # Age (1 point if >60)
    age = int(data.get('age', 0))
    if age > 60:
        score += 1
        details.append("Age > 60 (+1)")
    
    # Medical History (1 point each)
    if data.get('history') == 'yes':
        score += 1
        details.append("History of stroke or TIA (+1)")
    if data.get('hypertension') == 'yes':
        score += 1
        details.append("Hypertension (+1)")
    if data.get('diabetes') == 'yes':
        score += 1
        details.append("Diabetes (+1)")
    if data.get('smoker') == 'yes':
        score += 1
        details.append("Smoker (+1)")
    
    # Determine Risk Level
    if score <= 2:
        risk = "Low"
    elif score <= 4:
        risk = "Moderate"
    else:
        risk = "High"
    
    return {"risk": risk, "score": score, "details": details}

# Routes
@app.route("/")
def index():
    return render_template_string(page_template)

@app.route("/assess", methods=["POST"])
def assess():
    data = request.json
    result = calculate_stroke_risk(data)
    return jsonify(result)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional medical assistant. Provide accurate, helpful information about stroke symptoms, prevention, and treatment."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        reply = response.choices[0].message['content']
    except Exception as e:
        reply = f"Sorry, I encountered an error: {str(e)}"
    
    return jsonify({"reply": reply})

import os

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)

# Modern, responsive, multi-lingual page template
page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Johns Hopkins Stroke Risk Assessment</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #3F72AF;
            --secondary-color: #00B4D8;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #f8fafc;
            color: #293241;
        }
        
        .hero {
            text-align: center;
            padding: 4rem 0;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }
        
        .section {
            background: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-select, .form-control {
            border-radius: 0.5rem;
            padding: 0.75rem;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
        }
        
        .chat-container {
            height: 400px;
            overflow-y: auto;
        }
        
        .chat-message {
            margin: 0.5rem 0;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        
        .user-message {
            background: #e7f5ff;
            margin-left: auto;
        }
        
        .bot-message {
            background: #f0f4c3;
        }
        
        .language-switcher {
            position: fixed;
            top: 1rem;
            right: 1rem;
        }
        
        .slider {
            width: 100%;
            height: 400px;
            overflow-x: auto;
            padding: 2rem 0;
        }
    </style>
</head>
<body>
    <div class="language-switcher">
        <select id="language" onchange="changeLanguage()">
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
        </select>
    </div>

    <div class="container">
        <div class="hero">
            <h1 class="display-4">Johns Hopkins Stroke Risk Assessment</h1>
            <p class="lead">A comprehensive tool for stroke risk evaluation and prevention</p>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="section">
                    <h2>Stroke Risk Assessment</h2>
                    <form id="assessmentForm">
                        <div class="form-group">
                            <label for="facial_droop">Facial Droop:</label>
                            <select class="form-select" id="facial_droop">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="arm_weakness">Arm Weakness:</label>
                            <select class="form-select" id="arm_weakness">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="speech_difficulty">Speech Difficulty:</label>
                            <select class="form-select" id="speech_difficulty">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="onset_time">Onset Time (hours ago):</label>
                            <input type="number" class="form-control" id="onset_time" value="1">
                        </div>

                        <div class="form-group">
                            <label for="age">Age:</label>
                            <input type="number" class="form-control" id="age" value="45">
                        </div>

                        <div class="form-group">
                            <label for="history">Previous Stroke/TIA History:</label>
                            <select class="form-select" id="history">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="hypertension">Hypertension:</label>
                            <select class="form-select" id="hypertension">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="diabetes">Diabetes:</label>
                            <select class="form-select" id="diabetes">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="smoker">Smoker:</label>
                            <select class="form-select" id="smoker">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </div>

                        <button type="button" class="btn btn-primary" onclick="submitForm()">Assess Risk</button>
                    </form>
                    
                    <div id="result" class="mt-3"></div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="section">
                    <h2>Medical Assistant</h2>
                    <div class="chat-container" id="chatContainer">
                        <div class="chat-message user">How can I help you today?</div>
                    </div>
                    <div class="mt-2">
                        <input type="text" id="userInput" class="form-control" placeholder="Ask your question...">
                        <button type="button" class="btn btn-primary mt-2" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="section mt-5">
            <h2>Stroke Knowledge Base</h2>
            <div class="slider">
                <div class="slide">
                    <h3>What is a Stroke?</h3>
                    <p>A stroke occurs when blood supply to part of your brain is interrupted or reduced.</p>
                </div>
                <div class="slide">
                    <h3>FAST Signs of Stroke</h3>
                    <ul>
                        <li>Face: Ask the person to smile. Does one side droop?</li>
                        <li>Arm: Ask the person to raise both arms. Does one arm drift downward?</li>
                        <li>Speech: Ask the person to repeat a simple sentence. Is their speech slurred or difficult to understand?</li>
                        <li>Time: Time is of the essence. Note when the symptoms began.</li>
                    </ul>
                </div>
                <div class="slide">
                    <h3>Prevention Tips</h3>
                    <ul>
                        <li>Control blood pressure</li>
                        <li>Maintain a healthy diet</li>
                        <li>Exercise regularly</li>
                        <li>Don't smoke</li>
                        <li>Limit alcohol</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentLanguage = 'en';
        
        function changeLanguage() {
            const langSelect = document.getElementById('language');
            currentLanguage = langSelect.value;
            // Add language-specific translations here
        }

        function submitForm() {
            const data = {
                facial_droop: document.getElementById('facial_droop').value,
                arm_weakness: document.getElementById('arm_weakness').value,
                speech_difficulty: document.getElementById('speech_difficulty').value,
                onset_time: document.getElementById('onset_time').value,
                age: document.getElementById('age').value,
                history: document.getElementById('history').value,
                hypertension: document.getElementById('hypertension').value,
                diabetes: document.getElementById('diabetes').value,
                smoker: document.getElementById('smoker').value
            };

            fetch('/assess', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(res => res.json()).then(res => {
                const resultElement = document.getElementById('result');
                let html = `
                    <div class="alert alert-${res.risk.toLowerCase()}">
                        <h4 class="alert-heading">${res.risk} Risk</h4>
                        <p class="mb-0">Total Score: ${res.score}</p>
                    </div>
                `;
                
                res.details.forEach(detail => {
                    html += `<div class="alert alert-info mt-2">${detail}</div>`;
                });
                
                resultElement.innerHTML = html;
            });
        }

        function sendMessage() {
            const userInput = document.getElementById('userInput');
            const chatContainer = document.getElementById('chatContainer');
            
            if (!userInput.value.trim()) return;
            
            chatContainer.innerHTML += `
                <div class="chat-message user mt-2">${userInput.value}</div>
            `;
            
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userInput.value })
            }).then(res => res.json()).then(res => {
                chatContainer.innerHTML += `
                    <div class="chat-message bot mt-2">${res.reply}</div>
                `;
                userInput.value = '';
                chatContainer.scrollTop = chatContainer.scrollHeight;
            });
        }
    </script>
</body>
</html>
"""
