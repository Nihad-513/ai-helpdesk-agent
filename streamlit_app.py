"""Bean & Brew customer support application."""

import streamlit as st
from app.auth import show_auth
from app.dashboard import show_dashboard
from app.staff_auth import show_staff_login
from app.staff_dashboard import show_admin_dashboard,show_agent_dashboard
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Bean & Brew | Customer Support",
    page_icon="♨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# GLOBAL STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    /* ==========================================
       GLOBAL APPLICATION
       Base font size is raised to 18px. Streamlit sizes most
       things in rem, so this enlarges the whole app evenly.
    ========================================== */

    html, body {
        font-size: 18px !important;
    }

    :root,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        color-scheme: light !important;
    }

    .stApp {
        background: #F7F3EC;
        color: #30251F;
        font-family: 'DM Sans', sans-serif;
        font-size: 18px;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1450px;
    }

    .stApp .stMarkdown p,
    .stApp .stMarkdown li {
        color: #30251F;
        font-size: 18px;
        line-height: 1.75;
    }

    /* ==========================================
       DARK TEXT ON LIGHT BACKGROUNDS
       (Streamlit follows the device dark mode and turns text white,
       so all text on light surfaces is forced dark here.)
    ========================================== */

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    [data-testid="stHeading"] h1,
    [data-testid="stHeading"] h2,
    [data-testid="stHeading"] h3,
    [data-testid="stHeading"] h4 {
        color: #30251F !important;
    }

    .stApp h1 { font-size: 2.6rem !important; }
    .stApp h2 { font-size: 2.1rem !important; }
    .stApp h3 { font-size: 1.7rem !important; }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] strong {
        color: #30251F !important;
    }

    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    [data-testid="stWidgetLabel"] label {
        color: #30251F !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label p,
    [data-testid="stRadio"] label span,
    [data-testid="stRadio"] [role="radiogroup"] label div,
    div[role="radiogroup"] label,
    div[role="radiogroup"] label p {
        color: #30251F !important;
        font-weight: 500;
        font-size: 18px !important;
    }

    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] label p,
    [data-testid="stCheckbox"] label span,
    [data-testid="stToggle"] label p {
        color: #30251F !important;
        font-size: 18px !important;
    }

    /* Input boxes */

    [data-baseweb="input"],
    [data-baseweb="base-input"],
    [data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-baseweb="input"] input {
        color: #211A16 !important;
        -webkit-text-fill-color: #211A16 !important;
        background-color: #FFFFFF !important;
    }

    .stTextInput button,
    [data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
        min-height: auto !important;
        padding: 4px 8px !important;
    }

    .stTextInput button svg,
    [data-testid="stTextInput"] button svg {
        color: #553B2D !important;
        fill: #553B2D !important;
    }

    /* Select boxes and dropdown lists */

    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBBBA9 !important;
        border-radius: 10px !important;
        color: #211A16 !important;
        min-height: 52px;
    }

    [data-baseweb="select"] span,
    [data-baseweb="select"] div,
    [data-baseweb="select"] input {
        color: #211A16 !important;
        -webkit-text-fill-color: #211A16 !important;
        font-size: 18px !important;
    }

    [data-baseweb="popover"] ul,
    [data-baseweb="menu"],
    [role="listbox"] {
        background-color: #FFFFFF !important;
    }

    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [role="option"],
    [role="option"] div {
        color: #211A16 !important;
        background-color: #FFFFFF !important;
        font-size: 17px !important;
    }

    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background-color: #F1E8DC !important;
    }

    /* Tables / dataframes */

    [data-testid="stTable"] td,
    [data-testid="stTable"] th,
    [data-testid="stTable"] td *,
    [data-testid="stTable"] th * {
        color: #30251F !important;
        font-size: 17px !important;
    }

    /* Tooltips and toasts */

    [data-testid="stTooltipContent"],
    [data-testid="stToast"],
    [data-testid="stToast"] * {
        color: #30251F !important;
        font-size: 16px !important;
    }

    [data-testid="stToast"] {
        background: #FFFDFA !important;
        border: 1px solid #E6DCD0 !important;
    }

    /* ==========================================
       BRANDING (white text on the dark brown circle)
    ========================================== */

    .brand-header {
        text-align: center;
        margin: 0 auto 1.5rem auto;
    }

    .brand-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 75px;
        height: 75px;
        border-radius: 50%;
        background: #553B2D;
        font-family: 'Playfair Display', serif;
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .stApp .brand-icon,
    .stApp .brand-icon * {
        color: #FFF9F1 !important;
        -webkit-text-fill-color: #FFF9F1 !important;
    }

    .brand-name {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 3px;
        color: #513629 !important;
    }

    .brand-tagline {
        font-size: 0.9rem;
        letter-spacing: 3px;
        color: #806D5F !important;
        margin-top: 5px;
    }

    /* ==========================================
       AUTHENTICATION
    ========================================== */

    .auth-heading {
        text-align: center;
        margin: 2rem auto;
    }

    .auth-heading h1 {
        font-family: 'Playfair Display', serif;
        color: #30251F !important;
        font-size: clamp(2.3rem, 4.5vw, 3.4rem) !important;
        line-height: 1.2;
        margin-bottom: 0.7rem;
    }

    .auth-heading p {
        color: #66574D !important;
        font-size: 1.15rem;
    }

    /* ==========================================
       CARDS
    ========================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFDFA;
        border: 1px solid #EAE1D6;
        border-radius: 18px;
        box-shadow: 0 8px 25px rgba(67, 46, 32, 0.05);
        padding: 1.2rem;
    }

    [data-testid="stForm"] {
        border: none;
    }

    /* ==========================================
       TABS
    ========================================== */

    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 1px solid #EDE5DC;
    }

    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] p {
        color: #66574D !important;
        font-size: 18px !important;
        font-weight: 600;
        padding: 12px 18px;
    }

    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] p {
        color: #694632 !important;
    }

    /* ==========================================
       INPUT LABELS
    ========================================== */

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label {
        color: #30251F !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* ==========================================
       INPUT FIELDS
    ========================================== */

    .stTextInput > div > div,
    .stTextArea > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBBBA9 !important;
        border-radius: 10px !important;
        min-height: 58px;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        color: #211A16 !important;
        -webkit-text-fill-color: #211A16 !important;
        background-color: #FFFFFF !important;
        font-size: 19px !important;
        min-height: 54px;
        padding: 12px 14px !important;
        caret-color: #553B2D !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #817469 !important;
        -webkit-text-fill-color: #817469 !important;
        opacity: 1 !important;
    }

    /* ==========================================
       BUTTONS (white text on the dark brown buttons)
       Every nested element is covered so no label stays dark.
    ========================================== */

    .stButton button,
    .stDownloadButton button,
    .stLinkButton a,
    [data-testid="stFormSubmitButton"] button,
    [data-testid^="stBaseButton"] {
        background: #553B2D !important;
        border: none !important;
        border-radius: 10px;
        min-height: 52px;
        padding: 10px 22px;
        font-size: 18px !important;
        font-weight: 600;
        transition: 0.2s ease;
    }

    .stApp .stButton button,
    .stApp .stButton button *,
    .stApp .stDownloadButton button,
    .stApp .stDownloadButton button *,
    .stApp .stLinkButton a,
    .stApp .stLinkButton a *,
    .stApp [data-testid="stFormSubmitButton"] button,
    .stApp [data-testid="stFormSubmitButton"] button *,
    .stApp [data-testid^="stBaseButton"],
    .stApp [data-testid^="stBaseButton"] *,
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] .stButton button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 18px !important;
    }

    .stApp .stButton button svg,
    .stApp [data-testid^="stBaseButton"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    .stButton button:hover,
    .stDownloadButton button:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid^="stBaseButton"]:hover {
        background: #76543E !important;
    }

    /* Small password show/hide icon button must stay transparent */
    [data-testid="stTextInput"] button,
    [data-testid="stTextInput"] [data-testid^="stBaseButton"] {
        background: transparent !important;
        min-height: auto !important;
    }

    /* ==========================================
       SIDEBAR
    ========================================== */

    [data-testid="stSidebar"] {
        background: #EFE7DC !important;
        border-right: 1px solid #E0D4C6;
    }


    [data-testid="stSidebar"] {
    background: #EFE7DC !important;
    border-right: 1px solid #E0D4C6;
    min-width: 320px !important;
    width: 320px !important;
    display: block !important;
    visibility: visible !important;
    transform: none !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] label {
        color: #30251F !important;
    }

    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 18px !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 18px !important;
        padding: 8px 0;
    }

    /* ==========================================
       DASHBOARD WELCOME BANNER (white text on dark brown)
    ========================================== */

    .welcome-card {
        background: linear-gradient(120deg, #493126, #76523C);
        border-radius: 18px;
        padding: 2.8rem;
        margin: 1rem 0 1.5rem 0;
    }

    .stApp .welcome-card,
    .stApp .welcome-card *,
    .stApp .welcome-card h1,
    .stApp .welcome-card h2,
    .stApp .welcome-card h3,
    .stApp .welcome-card span,
    .stApp .welcome-card strong {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .stApp .welcome-card p,
    .stApp .welcome-card li {
        color: #F6EADF !important;
        -webkit-text-fill-color: #F6EADF !important;
        font-size: 1.2rem !important;
    }

    .welcome-card h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem !important;
    }

    /* Generic helper: put class "on-dark" on any dark-background
       element to keep its text light. */

    .stApp .on-dark,
    .stApp .on-dark * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    .section-title {
        font-family: 'Playfair Display', serif;
        color: #493126 !important;
        font-size: 1.8rem !important;
    }

    /* ==========================================
       CHAT MESSAGE CONTAINERS
    ========================================== */

    [data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1px solid #E6DCD0 !important;
        border-radius: 16px;
        padding: 22px 26px !important;
        margin-bottom: 18px;
        gap: 14px;
    }

    [data-testid="stChatMessage"] .stMarkdown p,
    [data-testid="stChatMessage"] .stMarkdown li,
    [data-testid="stChatMessage"] .stMarkdown strong,
    [data-testid="stChatMessage"] .stMarkdown em,
    [data-testid="stChatMessage"] .stMarkdown span {
        color: #211A16 !important;
        font-size: 19px !important;
        line-height: 1.8 !important;
    }

    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3 {
        color: #30251F !important;
    }

    [data-testid="stChatMessage"] code {
        font-size: 16px !important;
    }

    /* ==========================================
       CHAT INPUT
    ========================================== */

    [data-testid="stChatInput"] {
        background: #FFFFFF !important;
        border: 2px solid #CBBBA9 !important;
        border-radius: 16px !important;
        padding: 8px 12px !important;
        margin-top: 18px;
    }

    [data-testid="stChatInput"] textarea {
        color: #211A16 !important;
        -webkit-text-fill-color: #211A16 !important;
        background: #FFFFFF !important;
        font-size: 19px !important;
        line-height: 1.6 !important;
        min-height: 64px !important;
        padding: 14px !important;
        caret-color: #553B2D !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #817469 !important;
        -webkit-text-fill-color: #817469 !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] button {
        color: #553B2D !important;
    }

    /* ==========================================
       ALERTS
       RED   = errors (wrong email/password, failures)
       GREEN = success (ticket raised, saved, etc.)
       Both older and newer Streamlit markup are covered. The
       selectors start with .stApp so they beat the general
       "dark text" rules above.
    ========================================== */

    [data-testid="stAlert"] p,
    [data-testid="stAlertContainer"] p {
        font-size: 17px !important;
    }

    /* ----- ERROR (red) ----- */

    [data-testid="stAlert"][kind="error"],
    [data-testid="stAlertContainer"][kind="error"],
    [data-testid="stAlertContainer"][kind="negative"],
    [data-baseweb="notification"][kind="negative"],
    [data-testid="stAlert"]:has([kind="negative"]),
    [data-testid="stAlert"]:has([kind="error"]),
    [data-testid="stAlert"]:has([data-testid="stAlertContentError"]),
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {
        background: #FDECEC !important;
        border: 1px solid #E9A3A3 !important;
        border-radius: 10px !important;
    }

    .stApp [data-testid="stAlert"][kind="error"] *,
    .stApp [data-testid="stAlertContainer"][kind="error"] *,
    .stApp [data-testid="stAlertContainer"][kind="negative"] *,
    .stApp [data-baseweb="notification"][kind="negative"] *,
    .stApp [data-testid="stAlert"]:has([kind="negative"]) *,
    .stApp [data-testid="stAlert"]:has([kind="error"]) *,
    .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) *,
    .stApp [data-testid="stAlertContentError"] * {
        color: #B42318 !important;
        -webkit-text-fill-color: #B42318 !important;
        font-weight: 600 !important;
    }

    .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) svg,
    .stApp [data-testid="stAlert"]:has([kind="negative"]) svg,
    .stApp [data-testid="stAlert"]:has([kind="error"]) svg,
    .stApp [data-baseweb="notification"][kind="negative"] svg {
        fill: #B42318 !important;
        color: #B42318 !important;
    }

    /* ----- SUCCESS (green) ----- */

    [data-testid="stAlert"][kind="success"],
    [data-testid="stAlertContainer"][kind="success"],
    [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]),
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
        background: #EAF6EC !important;
        border: 1px solid #A7D7B0 !important;
        border-radius: 10px !important;
    }

    .stApp [data-testid="stAlert"][kind="success"] *,
    .stApp [data-testid="stAlertContainer"][kind="success"] *,
    .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) *,
    .stApp [data-testid="stAlertContentSuccess"] * {
        color: #176B35 !important;
        -webkit-text-fill-color: #176B35 !important;
        font-weight: 600 !important;
    }

    .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) svg,
    .stApp [data-testid="stAlert"][kind="success"] svg {
        fill: #176B35 !important;
        color: #176B35 !important;
    }

    /* ----- WARNING (amber) ----- */

    [data-testid="stAlert"][kind="warning"],
    [data-testid="stAlertContainer"][kind="warning"],
    [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]),
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
        background: #FFF4D6 !important;
        border: 1px solid #E9D18A !important;
        border-radius: 10px !important;
    }

    .stApp [data-testid="stAlert"][kind="warning"] *,
    .stApp [data-testid="stAlertContainer"][kind="warning"] *,
    .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) *,
    .stApp [data-testid="stAlertContentWarning"] * {
        color: #875600 !important;
        -webkit-text-fill-color: #875600 !important;
    }

    /* ----- INFO (blue) ----- */

    [data-testid="stAlert"][kind="info"],
    [data-testid="stAlertContainer"][kind="info"],
    [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]),
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
        background: #EAF2FA !important;
        border: 1px solid #B5CFE8 !important;
        border-radius: 10px !important;
    }

    .stApp [data-testid="stAlert"][kind="info"] *,
    .stApp [data-testid="stAlertContainer"][kind="info"] *,
    .stApp [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) *,
    .stApp [data-testid="stAlertContentInfo"] * {
        color: #174A75 !important;
        -webkit-text-fill-color: #174A75 !important;
    }

    /* ----- Custom message boxes (work in any Streamlit version) -----
       st.markdown('<div class="auth-error">Incorrect email or password.</div>',
                   unsafe_allow_html=True)
       st.markdown('<div class="auth-success">Ticket raised successfully.</div>',
                   unsafe_allow_html=True) */

    .stApp .auth-error,
    .stApp .auth-error * {
        color: #B42318 !important;
        -webkit-text-fill-color: #B42318 !important;
    }

    .auth-error {
        background: #FDECEC;
        border: 1px solid #E9A3A3;
        border-radius: 10px;
        font-size: 17px;
        font-weight: 600;
        padding: 14px 18px;
        margin: 0.5rem 0 1rem 0;
    }

    .stApp .auth-success,
    .stApp .auth-success * {
        color: #176B35 !important;
        -webkit-text-fill-color: #176B35 !important;
    }

    .auth-success {
        background: #EAF6EC;
        border: 1px solid #A7D7B0;
        border-radius: 10px;
        font-size: 17px;
        font-weight: 600;
        padding: 14px 18px;
        margin: 0.5rem 0 1rem 0;
    }

    /* ==========================================
       CAPTIONS
    ========================================== */

    [data-testid="stCaptionContainer"] p {
        color: #66574D !important;
        font-size: 16px !important;
    }

    /* ==========================================
       METRICS
    ========================================== */

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {
        color: #66574D !important;
        font-size: 17px !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: #30251F !important;
        font-size: 2.4rem !important;
    }

    /* ==========================================
       EXPANDERS
    ========================================== */

    [data-testid="stExpander"] {
        background: #FFFDFA;
        border: 1px solid #E6DCD0;
        border-radius: 12px;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: #30251F !important;
        font-size: 18px !important;
    }

    /* ==========================================
       FOOTER
    ========================================== */

    .auth-footer {
        text-align: center;
        color: #806D5F !important;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-top: 2.5rem;
    }

    /* ==========================================
       RESPONSIVE DESIGN
    ========================================== */

    @media (max-width: 768px) {

        html, body {
            font-size: 17px !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding: 1rem;
        }

        .auth-heading h1 {
            font-size: 2.2rem !important;
        }

        .welcome-card {
            padding: 1.5rem;
        }

        [data-testid="stChatMessage"] {
            padding: 14px 16px !important;
        }

        [data-testid="stChatMessage"] .stMarkdown p {
            font-size: 17px !important;
        }

        [data-testid="stChatInput"] textarea {
            font-size: 17px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "customer" not in st.session_state:
    st.session_state.customer = None

if "staff_authenticated" not in st.session_state:
    st.session_state.staff_authenticated = False

if "staff" not in st.session_state:
    st.session_state.staff = None

# --------------------------------------------------
# APPLICATION ROUTING
# --------------------------------------------------

# CUSTOMER PORTAL

if st.session_state.authenticated and not st.session_state.staff_authenticated:

    customer = st.session_state.customer

    if customer is not None:
        show_dashboard(customer)
    else:
        st.session_state.authenticated = False
        st.rerun()

# STAFF PORTAL
elif st.session_state.staff_authenticated:

    staff = st.session_state.staff

    if staff is not None:

        with st.sidebar:
            st.markdown("## ♨ Bean & Brew")
            st.caption("Staff Portal")
            st.divider()

            st.write(f"Signed in as **{staff['name']}**")
            st.write(f"Role: **{staff['role'].title()}**")

            if st.button("Sign out", use_container_width=True):
                st.session_state.staff_authenticated = False
                st.session_state.staff = None
                st.rerun()


        if staff["role"] == "admin":
          show_admin_dashboard(staff)

        else:
          show_agent_dashboard(staff)


    else:
        st.session_state.staff_authenticated = False
        st.rerun()

# LOGIN SELECTION
else:

    portal = st.radio(
        "Choose your portal",
        ["Customer Portal", "Staff Portal"],
        horizontal=True,
        key="login_portal",
    )

    if portal == "Customer Portal":
        show_auth()

    else:
        show_staff_login()