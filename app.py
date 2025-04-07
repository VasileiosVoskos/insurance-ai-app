import streamlit as st
import pandas as pd
from openai import OpenAI
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Dummy ERP Data (Simulated!)
erp_data = pd.DataFrame({
    "Policy_ID": range(1, 101),
    "Region": ["Καρδίτσα"] * 40 + ["Αθήνα"] * 30 + ["Θεσσαλονίκη"] * 30,
    "Coverage_Type": ["Φυσικές Καταστροφές"] * 60 + ["Κλοπή"] * 40,
    "Active": [True] * 100
})

# Simulated external event
external_event = {
    "Disaster_Type": "Πλημμύρα",
    "Location": "Καρδίτσα"
}


# OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="AI Decision Support System", layout="wide")
st.title("🚗 AI Decision Support System για Ασφαλιστικές")
st.markdown("Ανέβασε Excel, ρώτησε το AI, πάρε business insights!")

# ✅ SendGrid function με Streamlit Secrets
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
        response = sg.send(message)
        st.success("📧 Email alert εστάλη με επιτυχία μέσω SendGrid!")
    except Exception as e:
        st.error(f"⚠️ Σφάλμα κατά την αποστολή email: {e}")

# Upload Excel
uploaded_file = st.file_uploader("📂 Ανέβασε το Excel αρχείο σου", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Διαβάζουμε το αρχείο
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📊 Τα δεδομένα σου:")
        st.dataframe(df)
        st.subheader("🌍 Εξωτερικά Γεγονότα & Εκτίμηση Ρίσκου")

st.markdown(f"""
- **Εξωτερικό Γεγονός:** {external_event['Disaster_Type']} στην {external_event['Location']}
- Αναλύουμε δεδομένα ERP για πιθανή έκθεση...
""")

# Φιλτράρουμε ERP data για την περιοχή και την κάλυψη
affected_policies = erp_data[
    (erp_data["Region"] == external_event["Location"]) &
    (erp_data["Coverage_Type"] == "Φυσικές Καταστροφές") &
    (erp_data["Active"])
]

num_affected = affected_policies.shape[0]

if num_affected > 0:
    st.error(f"🚨 Υπάρχουν {num_affected} ενεργά συμβόλαια με κάλυψη φυσικών καταστροφών στην {external_event['Location']}!")
    st.dataframe(affected_policies)

    # Μπορούμε να στείλουμε και email αν θέλεις!
    subject = f"🚨 Προειδοποίηση: {external_event['Disaster_Type']} στην {external_event['Location']}"
    body = f"Υπάρχουν {num_affected} συμβόλαια με κάλυψη φυσικών καταστροφών στην {external_event['Location']}.\nΠιθανή έκθεση: {num_affected} οχήματα."
    send_email_alert(subject, body)

else:
    st.success(f"✅ Δεν υπάρχουν ενεργά συμβόλαια με κάλυψη φυσικών καταστροφών στην {external_event['Location']}!")


        # 🧩 Executive Summary
        st.subheader("🧩 Executive Summary")

        total_claims = df["Amount_EUR"].sum()
        average_claim = df["Amount_EUR"].mean()
        max_claim = df["Amount_EUR"].max()
        min_claim = df["Amount_EUR"].min()
        top_region = df.groupby("Region")["Amount_EUR"].sum().idxmax()

        st.markdown(f"""
        - **Σύνολο αποζημιώσεων:** {total_claims} €
        - **Μέση αποζημίωση:** {average_claim:.2f} €
        - **Μέγιστη αποζημίωση:** {max_claim} €
        - **Ελάχιστη αποζημίωση:** {min_claim} €
        - **Περιοχή με τις μεγαλύτερες αποζημιώσεις:** {top_region}
        """)

        # 🎨 Γραφήματα αποζημιώσεων ανά περιοχή
        st.subheader("📊 Ανάλυση Δεδομένων:")
        region_sum = df.groupby("Region")["Amount_EUR"].sum()

        fig, ax = plt.subplots()
        region_sum.plot(kind='bar', ax=ax)
        ax.set_ylabel("Σύνολο Αποζημιώσεων (€)")
        ax.set_title("Σύνολο Αποζημιώσεων ανά Περιοχή")
        st.pyplot(fig)

        # 🚨 Live Alerts με dynamic threshold
        st.subheader("🚨 Damage Control Alerts")

        alert_threshold = st.slider("🚦 Όρισε το όριο alert αποζημίωσης (€):", min_value=500, max_value=10000, value=3000, step=500)

        high_claims = df[df["Amount_EUR"] > alert_threshold]

        if not high_claims.empty:
            st.error(f"⚠️ Προσοχή! Υπάρχουν {len(high_claims)} αποζημιώσεις πάνω από {alert_threshold}€:")
            st.dataframe(high_claims)

            # ✅ Στέλνουμε και email alert μέσω SendGrid!
            subject = "🚨 Damage Control Alert: Υψηλές Αποζημιώσεις!"
            body = f"Υπάρχουν {len(high_claims)} αποζημιώσεις πάνω από {alert_threshold}€.\n\nΛεπτομέρειες:\n{high_claims.to_string(index=False)}"
            send_email_alert(subject, body)

        else:
            st.success(f"✅ Καμία αποζημίωση δεν ξεπερνά το όριο των {alert_threshold}€!")

        # 🤖 AI Σύμβουλος
        user_question = st.text_input("✍️ Κάνε την ερώτησή σου στο AI:")

        if user_question:
            with st.spinner('🧠 Το AI σκέφτεται...'):
                prompt = f"""
                Είσαι ένας έμπειρος σύμβουλος για ασφαλιστικές εταιρείες.
                Σου δίνω τα εξής δεδομένα:
                {df.to_string(index=False)}

                Ερώτηση:
                {user_question}
                """
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Είσαι ένας ειδικός σύμβουλος ασφαλιστικών εταιρειών."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.success("✅ Ο AI Σύμβουλός σου απαντά:")
                st.write(response.choices[0].message.content)

                # 📄 PDF Export Button
                if st.button("📄 Κατέβασε PDF Report"):

                    # Χρησιμοποιούμε το τοπικό αρχείο γραμματοσειράς από το repo
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    font_path = os.path.join(current_dir, "DejaVuSans.ttf")

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.add_font('DejaVu', '', font_path, uni=True)
                    pdf.set_font("DejaVu", size=12)

                    pdf.multi_cell(0, 10, "AI Decision Support Report\n", align='C')
                    pdf.multi_cell(0, 10, "Ερώτηση:", align='L')
                    pdf.multi_cell(0, 10, user_question, align='L')
                    pdf.multi_cell(0, 10, "\nΑπάντηση AI:", align='L')
                    pdf.multi_cell(0, 10, response.choices[0].message.content, align='L')

                    pdf.multi_cell(0, 10, "\nΣύνοψη Δεδομένων:", align='L')
                    for index, row in df.iterrows():
                        pdf.multi_cell(0, 10, f"ID: {row['Claim_ID']}, Amount: {row['Amount_EUR']}€, Type: {row['Damage_Type']}, Region: {row['Region']}", align='L')

                    pdf.output("report.pdf")

                    with open("report.pdf", "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                    href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="report.pdf">📥 Κατέβασε το PDF Report</a>'
                    st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚨 Προέκυψε πρόβλημα με το αρχείο: {e}")

else:
    st.info("💡 Ανέβασε ένα Excel για να ξεκινήσεις.")
