import streamlit as st
import pandas as pd
from fpdf import FPDF
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

st.title("📑 Αναφορές και Daily Report")

# Δημιουργία dummy δεδομένων για την αναφορά
data = {
    "Ημερομηνία": ["2025-04-08"],
    "Σύνολο Αποζημιώσεων (€)": [15200],
    "Μέση Αποζημίωση (€)": [3040],
    "Περιοχή με τις Μεγαλύτερες Αποζημιώσεις": ["Καρδίτσα"]
}
df = pd.DataFrame(data)

st.subheader("📊 Στοιχεία Αναφοράς")
st.table(df)

def create_pdf_report(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Ημερήσια Αναφορά Αποζημιώσεων", ln=True, align='C')
    pdf.ln(10)

    for col in dataframe.columns:
        pdf.cell(60, 10, col, border=1)
    pdf.ln()

    for index, row in dataframe.iterrows():
        for item in row:
            pdf.cell(60, 10, str(item), border=1)
        pdf.ln()

    pdf_file = "daily_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

def send_email_with_report(file_path):
    sendgrid_api_key = st.secrets["SENDGRID_API_KEY"]
    sender_email = st.secrets["SENDGRID_SENDER_EMAIL"]
    receiver_email = st.secrets["SENDGRID_RECEIVER_EMAIL"]

    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject="📊 Ημερήσια Αναφορά Αποζημιώσεων",
        plain_text_content="Σας επισυνάπτουμε την ημερήσια αναφορά αποζημιώσεων.",
    )

    try:
        with open(file_path, "rb") as f:
            message.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="daily_report.pdf"
            )

        sg = SendGridAPIClient(sendgrid_api_key)
        sg.send(message)
        st.success("📧 Το daily report εστάλη επιτυχώς μέσω email!")
    except Exception as e:
        st.error(f"⚠️ Σφάλμα κατά την αποστολή email: {e}")

if st.button("📤 Κατέβασε το PDF Report"):
    pdf_file = create_pdf_report(df)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="📥 Κατέβασε το Daily Report PDF",
            data=f,
            file_name="daily_report.pdf",
            mime="application/pdf"
        )

if st.button("📧 Στείλε Daily Report μέσω Email"):
    pdf_file = create_pdf_report(df)
    send_email_with_report(pdf_file)
