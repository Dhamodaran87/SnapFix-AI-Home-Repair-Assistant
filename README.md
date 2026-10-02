SnapFix 🔧 – AI Home Repair Assistant

SnapFix is an AI-powered home repair assistant that helps users understand household repair problems using photos and text descriptions. It uses Gemini to analyze visible issues, explain possible causes, provide troubleshooting steps, suggest tools or parts, and create practical repair guidance.

Features
📷 AI-powered repair photo analysis
🔍 Identification of visible problems
🧠 Possible-cause analysis
🛠️ Step-by-step troubleshooting guidance
✅ Repair checklists
🧰 Suggested tools and replacement parts
💬 Follow-up repair conversation with context
📝 Repair summary generation
📲 Optional WhatsApp summary sharing through Twilio
🔄 Gemini fallback model handling for temporary API errors
🌙 Dark professional Streamlit interface
Tech Stack
Python
Streamlit
Google Gemini API
Google GenAI Python SDK
Twilio WhatsApp API — optional
HTML/CSS for UI customization
Project Structure
SnapFix/
│
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
│
└── .streamlit/
    └── secrets.toml
Requirements

Before running SnapFix, install:

Python 3.10 or newer
A Google Gemini API key
Twilio credentials if WhatsApp functionality is required
Installation
1. Clone the project
git clone <your-github-repository-url>
cd SnapFix
2. Create a virtual environment

Windows:

python -m venv venv

Activate it:

venv\Scripts\activate

Mac/Linux:

python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
Configure API Keys

Create the following file:

.streamlit/secrets.toml
Gemini only
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
Gemini + WhatsApp
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_WHATSAPP_FROM = "whatsapp:+YOUR_TWILIO_NUMBER"
TWILIO_CONTENT_SID = "YOUR_TWILIO_CONTENT_SID"

Keep secrets.toml private and do not upload it to GitHub.

Configure prompts.py

The application imports its AI instructions from prompts.py.

The file should provide:

SYSTEM_PROMPT
WELCOME_MESSAGE_TEMPLATE
SUMMARY_REQUEST_PROMPT

Example structure:

SYSTEM_PROMPT = """Your SnapFix system prompt here."""

WELCOME_MESSAGE_TEMPLATE = (
    "Hey {name}! I'm SnapFix 🔧 - your AI home repair assistant."
)

SUMMARY_REQUEST_PROMPT = """
Summarize the repair conversation...
"""
Run the Application

Start Streamlit with:

streamlit run app.py

You should see output similar to:

Local URL: http://localhost:8501
Network URL: http://YOUR-IP:8501

Open the local URL in your browser.

How to Use
1. Create your workspace

Enter your name on the SnapFix welcome screen.

A WhatsApp number can be provided when WhatsApp summary sharing is configured.

2. Upload a repair photo

Upload an image such as:

leaking tap
broken hinge
loose fixture
damaged furniture
cracked wall
appliance issue

Supported image formats:

JPG
JPEG
PNG
WEBP
3. Describe the problem

Add a description such as:

Water is leaking from the bottom of my kitchen tap
when I turn it on.
4. Analyze the repair

Click:

🔎 Analyze repair

SnapFix sends the image and description to Gemini and returns repair guidance.

5. Ask follow-up questions

Use the repair conversation to ask questions such as:

What should I check next?
What tools do I need?
Could this part need replacement?
Is this safe to repair myself?
6. Generate a repair summary

After an analysis, use:

📝 Generate repair summary

to create a compact repair action plan.

7. WhatsApp sharing

When Twilio credentials are configured, SnapFix can send the repair summary to WhatsApp.

Without Twilio configuration, the rest of the SnapFix application continues to work and WhatsApp remains optional.

AI Model Configuration

The application currently defines:

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"

If the primary model encounters a temporary service-related error, SnapFix attempts to use the fallback model.

Safety

SnapFix provides AI-assisted guidance based on the information and images supplied by the user.

The application is designed to avoid recommending dangerous work such as:

Working on live electrical wiring
Bypassing safety devices
Opening gas connections
Dangerous improvised repairs
High-risk electrical, gas, structural, or similar work

For potentially dangerous repairs, users should consult a qualified professional.

Troubleshooting
ModuleNotFoundError: No module named 'prompts'

Make sure:

app.py
prompts.py

are in the same project directory.

Run Streamlit from that directory:

cd C:\Users\dell\SnapFix
streamlit run app.py
Gemini API key error

Check:

.streamlit/secrets.toml

and make sure:

GEMINI_API_KEY = "YOUR_KEY"

is present.

HTML is displayed as code

The application uses a Markdown/HTML rendering fix to remove accidental indentation from custom HTML blocks. Restart Streamlit after updating app.py:

Ctrl+C
streamlit run app.py
WhatsApp is not working

Check that all four Twilio secrets are configured:

TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_FROM
TWILIO_CONTENT_SID

WhatsApp functionality is optional.

GitHub .gitignore

Use a .gitignore similar to:

venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
.env
.DS_Store
License

This project can be distributed under the license chosen by the project owner.

Quick Start
git clone <your-github-repository-url>
cd SnapFix
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Create:

.streamlit/secrets.toml

Add:

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

Then run:

streamlit run app.py