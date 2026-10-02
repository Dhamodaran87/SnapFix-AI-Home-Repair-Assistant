import html
import json
import time
import textwrap

import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

try:
    from prompts import SUMMARY_REQUEST_PROMPT
except ImportError:
    from prompts import SUMMARY_PROMPT as SUMMARY_REQUEST_PROMPT


PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"


st.set_page_config(
    page_title="SnapFix",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# IMPORTANT:
# Streamlit treats a multiline Markdown string with 4+ leading spaces as
# a code block. The original UI strings were indented inside Python, so
# the HTML was being displayed as RAW TEXT.
#
# This helper removes Python indentation BEFORE Streamlit receives the HTML.
def render_html(markup):
    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


render_html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }

    body {
        overflow-x: hidden;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(249,115,22,.10), transparent 24%),
            radial-gradient(circle at 90% 5%, rgba(34,197,94,.08), transparent 23%),
            linear-gradient(180deg, #091015 0%, #060a0e 50%, #05080b 100%);
        color: #f8fafc;
    }

    [data-testid="stHeader"] {
        background: rgba(5, 9, 13, .72);
    }

    .block-container {
        max-width: 1400px;
        padding: 1.35rem 2rem 7rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1117 0%, #071016 100%);
        border-right: 1px solid rgba(255,255,255,.07);
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.05rem .9rem 1rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 4px 8px 27px;
    }

    .brand-icon {
        width: 48px;
        height: 48px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #ffab5c, #f97316);
        box-shadow: 0 12px 35px rgba(249,115,22,.22);
        font-size: 24px;
    }

    .brand-name {
        color: #f8fafc;
        font-size: 21px;
        font-weight: 800;
        letter-spacing: -.7px;
    }

    .brand-name span {
        color: #ff9f4b;
    }

    .brand-caption {
        color: #6e8190;
        font-size: 10px;
        margin-top: 3px;
    }

    .side-label {
        color: #5e7181;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.15px;
        margin: 21px 8px 8px;
        text-transform: uppercase;
    }

    .profile-card,
    .activity-card {
        background: rgba(15,26,33,.83);
        border: 1px solid rgba(255,255,255,.07);
        border-radius: 16px;
        padding: 13px;
        margin: 0 3px;
    }

    .profile-row {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .avatar {
        width: 39px;
        height: 39px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(249,115,22,.11);
        border: 1px solid rgba(249,115,22,.20);
        font-size: 17px;
    }

    .profile-name {
        color: #f8fafc;
        font-size: 13px;
        font-weight: 700;
    }

    .profile-contact {
        color: #6f8291;
        font-size: 10px;
        margin-top: 3px;
    }

    .side-number {
        color: #f8fafc;
        font-size: 25px;
        font-weight: 800;
    }

    .side-text {
        color: #667a89;
        font-size: 9px;
        line-height: 1.5;
    }

    .side-footer {
        margin: 31px 8px 0;
        padding-top: 21px;
        border-top: 1px solid rgba(255,255,255,.06);
        color: #6b7d8c;
        font-size: 10px;
        line-height: 1.65;
    }

    .page-title {
        color: #f8fafc;
        font-size: 31px;
        font-weight: 800;
        letter-spacing: -.9px;
        margin-top: 28px;
        margin-bottom: 0;
    }

    .page-title span {
        color: #ff9f4b;
    }

    .page-subtitle {
        color: #738595;
        font-size: 12px;
        line-height: 1.65;
        margin-top: 4px;
    }

    .online {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 8px 12px;
        border-radius: 999px;
        color: #84efae;
        background: rgba(34,197,94,.07);
        border: 1px solid rgba(34,197,94,.16);
        font-size: 10px;
        font-weight: 700;
        white-space: nowrap;
        margin-top: 28px;
    }

    .online-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #38e889;
        box-shadow: 0 0 12px rgba(56,232,137,.86);
    }

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 218px;
        padding: 29px 31px;
        margin-top: 20px;
        border-radius: 25px;
        border: 1px solid rgba(249,115,22,.21);
        background:
            radial-gradient(circle at 82% 42%, rgba(249,115,22,.15), transparent 21%),
            radial-gradient(circle at 8% 115%, rgba(34,197,94,.09), transparent 28%),
            linear-gradient(135deg, rgba(35,21,12,.92), rgba(15,24,30,.96));
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.03),
            0 23px 60px rgba(0,0,0,.20);
    }

    .hero-kicker {
        display: inline-block;
        padding: 7px 11px;
        border-radius: 999px;
        color: #ffb979;
        background: rgba(249,115,22,.08);
        border: 1px solid rgba(249,115,22,.18);
        font-size: 9px;
        font-weight: 700;
    }

    .hero-title {
        color: #f8fafc;
        font-size: 29px;
        line-height: 1.08;
        font-weight: 800;
        letter-spacing: -.9px;
        margin-top: 13px;
    }

    .hero-text {
        max-width: 720px;
        color: #a8b7c1;
        font-size: 11px;
        line-height: 1.72;
        margin-top: 9px;
    }

    .quick-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 17px;
    }

    .quick-chip {
        padding: 8px 11px;
        border-radius: 999px;
        background: rgba(5,13,18,.58);
        border: 1px solid rgba(255,255,255,.07);
        color: #dce7eb;
        font-size: 9px;
        font-weight: 600;
    }

    .hero-tool {
        position: absolute;
        top: 24px;
        right: 42px;
        width: 175px;
        height: 175px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(249,115,22,.20), transparent 58%);
        font-size: 88px;
        transform: rotate(-7deg);
    }

    .section-title {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 750;
        margin: 23px 0 4px;
    }

    .section-subtitle {
        color: #657888;
        font-size: 10px;
        line-height: 1.55;
        margin-bottom: 11px;
    }

    .stat-card {
        min-height: 108px;
        padding: 16px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,.07);
        background: linear-gradient(145deg, rgba(17,28,35,.90), rgba(9,17,23,.91));
        box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
    }

    .stat-top {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .stat-icon {
        width: 39px;
        height: 39px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(249,115,22,.10);
        border: 1px solid rgba(249,115,22,.17);
        font-size: 18px;
    }

    .stat-label {
        color: #7d91a0;
        font-size: 10px;
    }

    .stat-value {
        color: #f8fafc;
        font-size: 19px;
        font-weight: 800;
        margin-top: 2px;
    }

    .stat-note {
        color: #637686;
        font-size: 9px;
        margin-top: 8px;
    }

    .panel-heading {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 750;
    }

    .panel-caption {
        color: #677a8b;
        font-size: 10px;
        line-height: 1.6;
        margin-top: 4px;
    }

    .repair-tip {
        margin-top: 14px;
        padding: 14px;
        border-radius: 15px;
        background: rgba(249,115,22,.06);
        border: 1px solid rgba(249,115,22,.12);
        color: #becbd2;
        font-size: 9px;
        line-height: 1.65;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 21px;
        border-color: rgba(255,255,255,.08);
        background: linear-gradient(145deg, rgba(12,25,31,.90), rgba(7,15,21,.94));
    }

    div[data-testid="stFileUploader"] {
        margin-top: 10px;
        border-radius: 16px;
        background: rgba(6,17,23,.68);
        border: 1px dashed rgba(121,145,157,.42);
        padding: 9px;
    }

    div[data-testid="stFileUploader"] section {
        padding: 0;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: transparent;
        border: none;
    }

    div[data-testid="stForm"] {
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,.08);
        background: rgba(7,16,21,.88);
        padding: 19px 20px 17px;
    }

    div[data-baseweb="input"],
    textarea {
        border-radius: 12px !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 42px;
        border-radius: 12px;
        font-weight: 650;
        border: 1px solid rgba(255,255,255,.09);
    }

    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #ff8b2c, #ffb65d);
        color: #1c1007;
        border: none;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 17px;
        border: 1px solid rgba(255,255,255,.05);
        background: rgba(13,22,28,.70);
        margin-bottom: 9px;
    }

    div[data-testid="stChatInput"] {
        border-radius: 17px;
    }

    .login-shell {
        max-width: 1150px;
        margin: 34px auto 0;
    }

    .login-hero {
        position: relative;
        overflow: hidden;
        min-height: 350px;
        border-radius: 29px;
        padding: 45px 48px;
        border: 1px solid rgba(249,115,22,.19);
        background:
            radial-gradient(circle at 82% 34%, rgba(249,115,22,.15), transparent 22%),
            radial-gradient(circle at 14% 112%, rgba(34,197,94,.08), transparent 28%),
            linear-gradient(135deg, #1d1109, #111a20 68%, #091216);
        box-shadow: 0 25px 65px rgba(0,0,0,.22);
    }

    .login-kicker {
        display: inline-block;
        padding: 8px 12px;
        border-radius: 999px;
        color: #ffba7b;
        border: 1px solid rgba(249,115,22,.21);
        background: rgba(249,115,22,.08);
        font-size: 9px;
        font-weight: 700;
    }

    .login-title {
        color: #f8fafc;
        font-size: 49px;
        line-height: 1;
        font-weight: 800;
        letter-spacing: -1.8px;
        margin-top: 18px;
    }

    .login-title span {
        color: #ff9c45;
    }

    .login-text {
        color: #97aab7;
        font-size: 12px;
        line-height: 1.75;
        max-width: 640px;
        margin-top: 16px;
    }

    .login-food {
        position: absolute;
        right: 65px;
        top: 56px;
        width: 220px;
        height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(249,115,22,.18), transparent 58%);
        font-size: 120px;
    }

    .form-heading {
        color: #f8fafc;
        font-size: 18px;
        font-weight: 750;
        margin-top: 16px;
    }

    .form-caption {
        color: #6e8190;
        font-size: 10px;
        margin-top: 4px;
        margin-bottom: 12px;
    }

    @media (max-width: 900px) {
        .hero-tool,
        .login-food {
            opacity: .22;
            right: 0;
        }
    }

    @media (max-width: 650px) {
        .block-container {
            padding: 1rem .8rem 6rem;
        }

        .page-title {
            font-size: 25px;
            margin-top: 12px;
        }

        .online {
            margin-top: 12px;
        }

        .hero {
            padding: 22px;
        }

        .hero-tool,
        .login-food {
            display: none;
        }

        .login-hero {
            padding: 29px 22px;
            min-height: 315px;
        }

        .login-title {
            font-size: 35px;
        }
    }
    </style>
    """
)


def get_secret(key):
    try:
        return str(st.secrets[key]).strip()
    except Exception:
        return ""


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

TWILIO_ACCOUNT_SID = get_secret("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_secret("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = get_secret("TWILIO_WHATSAPP_FROM")
TWILIO_CONTENT_SID = get_secret("TWILIO_CONTENT_SID")


WHATSAPP_ENABLED = all(
    [
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_WHATSAPP_FROM,
        TWILIO_CONTENT_SID,
    ]
)


@st.cache_resource
def get_gemini_client(api_key):
    if not api_key:
        return None

    retry_options = types.HttpRetryOptions(
        attempts=6,
        initial_delay=1,
        max_delay=30,
        exp_base=2,
        jitter=1,
        http_status_codes=[
            408,
            429,
            500,
            502,
            503,
            504,
        ],
    )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            retry_options=retry_options,
        ),
    )


@st.cache_resource
def get_twilio_client(account_sid, auth_token):
    if not account_sid or not auth_token:
        return None

    return TwilioClient(
        account_sid,
        auth_token,
    )


gemini_client = get_gemini_client(GEMINI_API_KEY)

twilio_client = get_twilio_client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)


if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if "name" not in st.session_state:
    st.session_state.name = ""

if "phone" not in st.session_state:
    st.session_state.phone = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = None

if "active_model" not in st.session_state:
    st.session_state.active_model = PRIMARY_MODEL

if "fallback_used" not in st.session_state:
    st.session_state.fallback_used = False

if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0


def create_chat(model, history=None):
    if gemini_client is None:
        return None

    return gemini_client.chats.create(
        model=model,
        history=history or [],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.35,
        ),
    )


def save_message(role, kind, content):
    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content,
        }
    )


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        else:
            st.image(
                message["content"],
                use_container_width=True,
            )


def temporary_error(error):
    text = str(error).upper()

    codes = [
        "503",
        "UNAVAILABLE",
        "429",
        "RESOURCE_EXHAUSTED",
        "500",
        "502",
        "504",
    ]

    return any(code in text for code in codes)


def ask_ai(parts):
    if gemini_client is None:
        return (
            "Gemini is not configured yet.\n\n"
            "Please add GEMINI_API_KEY to .streamlit/secrets.toml."
        )

    if st.session_state.chat is None:
        st.session_state.chat = create_chat(PRIMARY_MODEL)

    if st.session_state.chat is None:
        return "Unable to start the Gemini chat."

    try:
        response = st.session_state.chat.send_message(parts)

        st.session_state.active_model = PRIMARY_MODEL
        st.session_state.fallback_used = False

        return response.text

    except Exception as primary_error:

        if not temporary_error(primary_error):
            return (
                "SnapFix could not complete that request.\n\n"
                f"{primary_error}"
            )

        try:
            time.sleep(1)

            history = st.session_state.chat.get_history()

            fallback_chat = create_chat(
                FALLBACK_MODEL,
                history=history,
            )

            if fallback_chat is None:
                return "Unable to start the fallback Gemini chat."

            response = fallback_chat.send_message(parts)

            st.session_state.chat = fallback_chat
            st.session_state.active_model = FALLBACK_MODEL
            st.session_state.fallback_used = True

            return response.text

        except Exception:

            return (
                "SnapFix is temporarily busy because the AI service is "
                "experiencing high traffic.\n\n"
                "Please try again in a few seconds."
            )


def clean_whatsapp_text(text):
    text = " ".join((text or "").split())

    if not text:
        return "No repair summary available."

    if len(text) > 1400:
        return text[:1400] + "..."

    return text


def send_whatsapp(phone, name, summary):
    if not WHATSAPP_ENABLED:
        return (
            False,
            "WhatsApp is not configured. Add the Twilio secrets first.",
        )

    if twilio_client is None:
        return False, "Twilio client could not be initialized."

    try:
        sender = TWILIO_WHATSAPP_FROM.strip()

        if not sender.startswith("whatsapp:"):
            sender = f"whatsapp:{sender}"

        destination = phone.strip()

        if not destination.startswith("whatsapp:"):
            destination = f"whatsapp:{destination}"

        content_variables = json.dumps(
            {
                "1": name,
                "2": clean_whatsapp_text(summary),
            },
            ensure_ascii=False,
        )

        message = twilio_client.messages.create(
            from_=sender,
            to=destination,
            content_sid=TWILIO_CONTENT_SID,
            content_variables=content_variables,
        )

        return True, message.sid

    except Exception as error:
        return False, str(error)


def generate_summary():
    if st.session_state.chat is None:
        return "No repair conversation is available yet."

    try:
        history = st.session_state.chat.get_history()

        summary_chat = create_chat(
            st.session_state.active_model,
            history=history,
        )

        if summary_chat is None:
            return "Unable to create the summary."

        response = summary_chat.send_message(
            SUMMARY_REQUEST_PROMPT
        )

        return response.text

    except Exception as error:

        return (
            "Could not create the repair summary.\n\n"
            f"{error}"
        )


def reset_workspace():
    keys = [
        "onboarded",
        "name",
        "phone",
        "messages",
        "chat",
        "active_model",
        "fallback_used",
        "analysis_count",
    ]

    for key in keys:
        st.session_state.pop(key, None)

    st.rerun()


def repair_prompt():
    return """
Analyze this home repair issue carefully.

Return a practical response with these sections:

### What I can see
Describe only what is actually visible.

### Possible issue
Explain the most likely possible issue or causes.
Do not present a guess as a confirmed diagnosis.

### What to check
Give the safest useful checks the user can perform.

### Troubleshooting
Give simple step-by-step troubleshooting instructions.

### Repair checklist
Give a short checklist of useful repair tasks.

### Tools / parts
List likely tools or replacement parts only when relevant.

### Safety
Explain any important safety concern and when the user should contact
a qualified professional.

### Follow-up question
Ask one useful question if more information is needed.

Keep the answer practical and beginner-friendly.
"""


# -------------------------------------------------------------------
# ONBOARDING / LOGIN
# -------------------------------------------------------------------

if not st.session_state.onboarded:

    render_html(
        """
        <div class="login-shell">
            
        </div>
        """
    )

    left, right = st.columns(
        [1.2, 0.8],
        gap="large",
    )

    with left:

        render_html(
            """
            <div class="form-heading">Create your workspace</div>
            <div class="form-caption">
                Enter your name and an optional WhatsApp number to begin.
            </div>
            """
        )

        with st.form("snapfix_onboarding"):

            name = st.text_input(
                "Your name",
                placeholder="Enter your name",
            )

            phone = st.text_input(
                "WhatsApp number",
                placeholder="+91XXXXXXXXXX",
                help="Include country code if you want WhatsApp summaries.",
            )

            submitted = st.form_submit_button(
                "Enter SnapFix  →",
                use_container_width=True,
            )

    with right:

        render_html(
            """
            <div style="height:20px;"></div>

            <div class="stat-card">
                <div class="stat-top">
                    <div class="stat-icon">📷</div>
                    <div>
                        <div class="stat-label">Vision analysis</div>
                        <div class="stat-value">Photo → Problem</div>
                    </div>
                </div>
                <div class="stat-note">
                    Inspect visible damage and identify possible issues.
                </div>
            </div>

            <div style="height:10px;"></div>

            <div class="stat-card">
                <div class="stat-top">
                    <div class="stat-icon">🧰</div>
                    <div>
                        <div class="stat-label">Repair planning</div>
                        <div class="stat-value">Steps + Parts</div>
                    </div>
                </div>
                <div class="stat-note">
                    Create troubleshooting steps, checklists and tools lists.
                </div>
            </div>

            <div class="repair-tip">
                <b>Safety first</b><br>
                SnapFix distinguishes visible observations from possibilities
                and warns when a qualified professional should handle the work.
            </div>
            """
        )

    if submitted:

        if not name.strip():

            st.warning("Please enter your name.")

        else:

            st.session_state.name = name.strip()
            st.session_state.phone = phone.strip()

            st.session_state.chat = create_chat(
                PRIMARY_MODEL
            )

            st.session_state.messages = []

            st.session_state.active_model = PRIMARY_MODEL
            st.session_state.fallback_used = False
            st.session_state.analysis_count = 0

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# -------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------

with st.sidebar:

    render_html(
        """
        <div class="brand">
            <div class="brand-icon">🔧</div>
            <div>
                <div class="brand-name">
                    Snap<span>Fix</span>
                </div>
                <div class="brand-caption">
                    AI Home Repair Assistant
                </div>
            </div>
        </div>
        """
    )

    render_html(
        '<div class="side-label">PROFILE</div>'
    )

    safe_name = html.escape(st.session_state.name)
    safe_phone = html.escape(
        st.session_state.phone
        if st.session_state.phone
        else "WhatsApp optional"
    )

    render_html(
        f"""
        <div class="profile-card">
            <div class="profile-row">
                <div class="avatar">🧰</div>
                <div>
                    <div class="profile-name">{safe_name}</div>
                    <div class="profile-contact">{safe_phone}</div>
                </div>
            </div>
        </div>
        """
    )

    render_html(
        '<div class="side-label">WORKSPACE</div>'
    )

    if st.button(
        "⌂  Home",
        use_container_width=True,
    ):
        st.toast("SnapFix home is active.")

    if st.button(
        "📷  Analyze Repair",
        use_container_width=True,
    ):
        st.toast("Use the Analyze your repair section.")

    if st.button(
        "◷  Conversation",
        use_container_width=True,
    ):
        st.toast("Your repair conversation is below.")

    render_html(
        '<div class="side-label">ACTIVITY</div>'
    )

    render_html(
        f"""
        <div class="activity-card">
            <div class="side-number">
                {st.session_state.analysis_count}
            </div>
            <div class="side-text">
                Repair analyses in this workspace
            </div>
        </div>
        """
    )

    st.write("")

    if st.button(
        "＋  New Workspace",
        use_container_width=True,
    ):
        reset_workspace()

    render_html(
        """
        <div class="side-footer">
            🧰 Inspect carefully.<br>
            🔍 Troubleshoot safely.<br>
            ✅ Know when to call a pro.
        </div>
        """
    )


# -------------------------------------------------------------------
# MAIN HEADER
# -------------------------------------------------------------------

header_left, header_right = st.columns(
    [4, 1],
    vertical_alignment="center",
)

with header_left:

    safe_name = html.escape(st.session_state.name)

    render_html(
        f"""
        <div class="page-title">
            Good to see you, {safe_name} 👋
        </div>

        <div class="page-subtitle">
            Diagnose the visible issue, ask follow-up questions,
            and build a practical repair plan.
        </div>
        """
    )


with header_right:

    render_html(
        """
        <div style="text-align:right;">
            <span class="online">
                <span class="online-dot"></span>
                SnapFix Online
            </span>
        </div>
        """
    )


# -------------------------------------------------------------------
# HERO
# -------------------------------------------------------------------

# render_html(
#     """
#     <div class="hero">
#         <div class="hero-kicker">
#             ✦ YOUR AI REPAIR ASSISTANT
#         </div>

#         <div class="hero-title">
#             See the problem. Understand the fix.
#         </div>

#         <div class="hero-text">
#             Upload a photo of a broken household item or describe the issue.
#             SnapFix helps identify what is visible, explain possible causes,
#             guide safe checks, and organize the next steps.
#         </div>

#         <div class="quick-row">
#             <span class="quick-chip">📷 Visual inspection</span>
#             <span class="quick-chip">🔍 Possible causes</span>
#             <span class="quick-chip">🧰 Repair checklist</span>
#             <span class="quick-chip">🛒 Tools & parts</span>
#             <span class="quick-chip">📲 WhatsApp summary</span>
#         </div>

#         <div class="hero-tool">🔧</div>
#     </div>
#     """
# )


# -------------------------------------------------------------------
# WORKSPACE OVERVIEW
# -------------------------------------------------------------------

render_html(
    '<div class="section-title">Workspace overview</div>'
)

render_html(
    """
    <div class="section-subtitle">
        A quick look at your current repair session.
    </div>
    """
)


stat1, stat2, stat3 = st.columns(3)


with stat1:

    render_html(
        f"""
        <div class="stat-card">
            <div class="stat-top">
                <div class="stat-icon">📷</div>
                <div>
                    <div class="stat-label">
                        Repair analyses
                    </div>
                    <div class="stat-value">
                        {st.session_state.analysis_count}
                    </div>
                </div>
            </div>

            <div class="stat-note">
                Photos and repair descriptions analyzed
            </div>
        </div>
        """
    )


with stat2:

    render_html(
        f"""
        <div class="stat-card">
            <div class="stat-top">
                <div class="stat-icon">🤖</div>
                <div>
                    <div class="stat-label">
                        AI engine
                    </div>
                    <div class="stat-value">
                        Active
                    </div>
                </div>
            </div>

            <div class="stat-note">
                {html.escape(st.session_state.active_model)}
            </div>
        </div>
        """
    )


with stat3:

    whatsapp_status = (
        "Ready"
        if WHATSAPP_ENABLED
        else "Optional"
    )

    render_html(
        f"""
        <div class="stat-card">
            <div class="stat-top">
                <div class="stat-icon">📲</div>
                <div>
                    <div class="stat-label">
                        WhatsApp
                    </div>
                    <div class="stat-value">
                        {whatsapp_status}
                    </div>
                </div>
            </div>

            <div class="stat-note">
                Repair summary sharing
            </div>
        </div>
        """
    )


# -------------------------------------------------------------------
# ANALYZE REPAIR
# -------------------------------------------------------------------

render_html(
    '<div class="section-title">Analyze your repair</div>'
)

render_html(
    """
    <div class="section-subtitle">
        Attach a repair photo or describe the problem before analyzing it.
    </div>
    """
)


with st.container(border=True):

    render_html(
        '<div class="panel-heading">📷 Attach a repair photo</div>'
    )

    render_html(
        """
        <div class="panel-caption">
            Examples: leaking tap, broken hinge, damaged furniture,
            appliance exterior, cracked wall, loose fixture.
        </div>
        """
    )

    uploaded_photo = st.file_uploader(
        "Attach a repair photo",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp",
        ],
        key="repair_photo",
    )

    issue_description = st.text_area(
        "Describe the problem",
        placeholder=(
            "Example: Water is dripping from the bottom of the tap "
            "when I turn it on..."
        ),
        height=95,
    )

    analyze_col, clear_col = st.columns(
        [3, 1],
    )

    with analyze_col:

        analyze_clicked = st.button(
            "🔎 Analyze repair",
            use_container_width=True,
        )

    with clear_col:

        clear_clicked = st.button(
            "Clear",
            use_container_width=True,
        )

    if clear_clicked:

        st.session_state.pop(
            "repair_photo",
            None,
        )

        st.rerun()

    if uploaded_photo is not None:

        st.image(
            uploaded_photo,
            caption="Selected repair photo",
            use_container_width=True,
        )

    if analyze_clicked:

        if (
            uploaded_photo is None
            and not issue_description.strip()
        ):

            st.warning(
                "Attach a photo or describe the repair problem first."
            )

        else:

            parts = []

            if uploaded_photo is not None:

                photo_bytes = uploaded_photo.getvalue()

                save_message(
                    "user",
                    "image",
                    photo_bytes,
                )

                parts.append(
                    types.Part.from_bytes(
                        data=photo_bytes,
                        mime_type=uploaded_photo.type,
                    )
                )

            prompt = repair_prompt()

            if issue_description.strip():

                save_message(
                    "user",
                    "text",
                    issue_description.strip(),
                )

                prompt += (
                    "\n\nUser's additional description:\n"
                    + issue_description.strip()
                )

            parts.append(prompt)

            with st.spinner(
                "Inspecting the repair..."
            ):

                answer = ask_ai(parts)

            save_message(
                "assistant",
                "text",
                answer,
            )

            st.session_state.analysis_count += 1

            st.rerun()


# -------------------------------------------------------------------
# REPAIR CONVERSATION
# -------------------------------------------------------------------

render_html(
    '<div class="section-title">Repair conversation</div>'
)

render_html(
    """
    <div class="section-subtitle">
        Ask follow-up questions and keep the repair context in one conversation.
    </div>
    """
)


if st.session_state.fallback_used:

    st.info(
        "The primary AI model was busy, so SnapFix switched to the backup model."
    )


if not st.session_state.messages:

    welcome = WELCOME_MESSAGE_TEMPLATE.format(
        name=st.session_state.name
    )

    save_message(
        "assistant",
        "text",
        welcome,
    )


for message in st.session_state.messages:

    render_message(message)


chat_input = st.chat_input(
    "Ask SnapFix about the repair or attach another photo...",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
)


if chat_input:

    photo = (
        chat_input.files[0]
        if chat_input.files
        else None
    )

    text = chat_input.text

    parts = []

    if photo is not None:

        photo_bytes = photo.getvalue()

        save_message(
            "user",
            "image",
            photo_bytes,
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:

        save_message(
            "user",
            "text",
            text,
        )

        parts.append(text)

    elif photo is not None:

        parts.append(
            """
Analyze this new repair photo in the context of our current
conversation.

Explain:
What is newly visible,
whether it changes the likely cause,
what should be checked next,
and any important safety concern.
"""
        )

    if parts:

        with st.spinner(
            "Thinking through the repair..."
        ):

            answer = ask_ai(parts)

        save_message(
            "assistant",
            "text",
            answer,
        )

    st.rerun()


# -------------------------------------------------------------------
# REPAIR SUMMARY
# -------------------------------------------------------------------

if st.session_state.analysis_count > 0:

    render_html(
        '<div class="section-title">Repair summary</div>'
    )

    render_html(
        """
        <div class="section-subtitle">
            Turn your current repair conversation into a compact action plan.
        </div>
        """
    )

    summary_col, whatsapp_col = st.columns(
        [1.2, 1],
        gap="large",
    )

    with summary_col:

        if st.button(
            "📝 Generate repair summary",
            use_container_width=True,
        ):

            with st.spinner(
                "Creating your repair summary..."
            ):

                summary = generate_summary()

            st.markdown(summary)

    with whatsapp_col:

        if WHATSAPP_ENABLED:

            if st.button(
                "📲 Send summary to WhatsApp",
                use_container_width=True,
            ):

                with st.spinner(
                    "Preparing WhatsApp summary..."
                ):

                    summary = generate_summary()

                success, info = send_whatsapp(
                    st.session_state.phone,
                    st.session_state.name,
                    summary,
                )

                if success:

                    st.success(
                        "Repair summary sent to WhatsApp."
                    )

                else:

                    st.error(
                        f"Couldn't send summary: {info}"
                    )

        else:

            st.info(
                "WhatsApp is optional. Add "
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
                "TWILIO_WHATSAPP_FROM and TWILIO_CONTENT_SID "
                "to enable it."
            )