import streamlit as st
from PIL import Image
import pandas as pd
import time
from openai import OpenAI
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# === SETTINGS ===
st.set_page_config(page_title="brain4 - Insurance AI System", layout="wide")

# === CUSTOM CSS ===
def set_background():
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(135deg, #ffffff, #f0f0f0);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main {
            background-color: rgba(255, 255, 255, 0.6);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        #MainMenu, footer, header {
            visibility: hidden;
        }
        button {
            border-radius: 8px;
            border: none;
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            transition-duration: 0.4s;
            cursor: pointer;
        }
        button:hover {
            background-color: white;
            color: black;
            border: 2px solid #4CAF50;
        }
        .css-1aumxhk {
            padding: 2rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.6);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# === LOGO ===
logo = Image.open("assets/logo.png")
st.image(logo, width=150)

# === LOGIN SCREEN ===
if "login" not in st.session_state:
    st.session_state["login"] = False

def login_page():
    st.markdown("## Καλώς ήρθατε στο brain4 - AI Insurance Advisor")
    st.markdown("### Παρακαλώ συνδεθείτε για να συνεχίσετε.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember me")

    if st.button("Login"):
        if username == "admin" and password == "admin":  # Temporary login for demo
            st.session_state["login"] = True
            st.success("Σύνδεση επιτυχής! Καλωσορίσατε.")
            time.sleep(1)
            st.experimental_rerun()
        else:
            st.error("Λάθος στοιχεία. Προσπαθήστε ξανά.")

if not st.session_state["login"]:
    login_page()
    st.stop()

# === SIDEBAR MENU ===
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Μετάβαση σε:",
    ["Dashboard", "Upload & Analysis", "AI Advisor", "Financial Insights", "Reports", "Settings"]
)

# === PAGES ===
if menu == "Dashboard":
    st.title("Dashboard")
    st.write("Καλωσορίσατε στο premium dashboard του brain4!")
    st.info("Εδώ θα βλέπετε συνοπτικές πληροφορίες για την επιχείρησή σας.")
    # Placeholder metrics
    st.metric("Αποζημιώσεις σήμερα", "12")
    st.metric("Συνολική αξία αποζημιώσεων", "34.500 €")
    st.metric("Open AI Συμβουλές", "Ενεργό")

elif menu == "Upload & Analysis":
    st.title("Upload & Analysis")
    uploaded_file = st.file_uploader("Ανεβάστε το Excel σας", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("Το αρχείο ανέβηκε επιτυχώς!")
            st.dataframe(df)

            st.markdown("### Βασικά Στατιστικά")
            st.write(df.describe())

        except Exception as e:
            st.error(f"Προέκυψε πρόβλημα με το αρχείο: {e}")

elif menu == "AI Advisor":
    st.title("AI Insurance Advisor")

    prompt = st.text_area("Γράψτε την ερώτησή σας προς τον AI σύμβουλο:")

    if st.button("Ρώτησε τον AI"):
        if prompt:
            with st.spinner("Ο AI αναλύει τα δεδομένα σας..."):
                client = OpenAI(api_key=st.secrets["openai_api_key"])
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Είσαι ένας έμπειρος σύμβουλος για ασφαλιστικές εταιρείες."},
                        {"role": "user", "content": prompt}
                    ]
                )
                ai_response = response.choices[0].message.content
                st.success("Απάντηση AI:")
                st.write(ai_response)
        else:
            st.warning("Παρακαλώ εισάγετε μια ερώτηση.")

elif menu == "Financial Insights":
    st.title("📈 Financial Insights")
    st.markdown("Αυτό το section θα συνδέεται με ERP και οικονομικά sites.")
    st.info("Εδώ θα βλέπετε οικονομικές αναλύσεις και επενδυτικές προτάσεις.")
    st.markdown("**Coming soon: Συνδέσεις με ERP, Yahoo Finance, Reuters και AI προβλέψεις!**")

elif menu == "Reports":
    st.title("Reports & Alerts")
    st.markdown("Αποστολή ημερήσιου report μέσω email.")

    if st.button("Αποστολή ημερήσιου Report"):
        try:
            message = Mail(
                from_email=st.secrets["SENDGRID_SENDER_EMAIL"],
                to_emails=st.secrets["SENDGRID_RECEIVER_EMAIL"],
                subject="brain4 - Ημερήσιο Report",
                plain_text_content="Αγαπητό στέλεχος, επισυνάπτεται το ημερήσιο report του brain4."
            )
            sg = SendGridAPIClient(st.secrets["SENDGRID_API_KEY"])
            response = sg.send(message)
            st.success("Το ημερήσιο report στάλθηκε επιτυχώς!")
        except Exception as e:
            st.error(f"Σφάλμα κατά την αποστολή email: {e}")

elif menu == "Settings":
    st.title("Ρυθμίσεις")
    st.markdown("Εδώ μπορείτε να ρυθμίσετε τα API keys και τις παραμέτρους της εφαρμογής σας.")
    st.info("Για αλλαγές στα API keys, χρησιμοποιήστε το Streamlit Cloud secrets.")

