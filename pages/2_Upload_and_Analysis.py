import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from PIL import Image

# Dummy ERP Data (simulated)
erp_data = pd.DataFrame({
    "Policy_ID": range(1, 101),
    "Region": ["Καρδίτσα"] * 40 + ["Αθήνα"] * 30 + ["Θεσσαλονίκη"] * 30,
    "Coverage_Type": ["Φυσικές Καταστροφές"] * 60 + ["Κλοπή"] * 40,
    "Active": [True] * 100
})

external_event = {
    "Disaster_Type": "Πλημμύρα",
    "Location": "Καρδίτσα"
}

client = OpenAI(api_key=st.secrets["openai_api_key"])

def send_email_alert(subject, body):
    sendgrid_api_key = st.secrets["SENDGRID_API_KEY"]
    sender_email = st.secrets["SENDGRID_SENDER_EMAIL"]
    receiver_email = st.secrets["SENDGRID_RECEIVER_EMAIL"]

    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        sg.send(message)
        st.success("📧 Email alert εστάλη με επιτυχία μέσω SendGrid!")
    except Exception as e:
        st.error(f"⚠️ Σφάλμα κατά την αποστολή email: {e}")

st.title("📂 Ανέβασε το Excel αρχείο σου")

uploaded_file = st.file_uploader("Επέλεξε αρχείο Excel", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📊 Τα δεδομένα σου:")
        st.dataframe(df)

        total_claims = df["Amount_EUR"].sum()
        average_claim = df["Amount_EUR"].mean()
        top_region = df.groupby("Region")["Amount_EUR"].sum().idxmax()

        st.markdown(f"""
        - **Σύνολο αποζημιώσεων:** {total_claims} €
        - **Μέση αποζημίωση:** {average_claim:.2f} €
        - **Περιοχή με τις μεγαλύτερες αποζημιώσεις:** {top_region}
        """)

        region_sum = df.groupby("Region")["Amount_EUR"].sum()
        fig, ax = plt.subplots()
        region_sum.plot(kind='bar', ax=ax)
        ax.set_ylabel("Σύνολο Αποζημιώσεων (€)")
        ax.set_title("Σύνολο Αποζημιώσεων ανά Περιοχή")
        st.pyplot(fig)

        alert_threshold = st.slider("🚦 Όρισε το όριο alert αποζημίωσης (€):", min_value=500, max_value=10000, value=3000, step=500)
        high_claims = df[df["Amount_EUR"] > alert_threshold]

        if not high_claims.empty:
            st.error(f"⚠️ Υπάρχουν {len(high_claims)} αποζημιώσεις πάνω από {alert_threshold}€:")
            st.dataframe(high_claims)

            subject = "🚨 Damage Control Alert: Υψηλές Αποζημιώσεις!"
            body = f"Υπάρχουν {len(high_claims)} αποζημιώσεις πάνω από {alert_threshold}€.\n\nΛεπτομέρειες:\n{high_claims.to_string(index=False)}"
            send_email_alert(subject, body)
        else:
            st.success(f"✅ Καμία αποζημίωση δεν ξεπερνά το όριο των {alert_threshold}€!")

    except Exception as e:
        st.error(f"🚨 Προέκυψε πρόβλημα με το αρχείο: {e}")

else:
    st.info("💡 Ανέβασε ένα Excel για να ξεκινήσεις.")
