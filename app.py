import streamlit as st
import pandas as pd
from openai import OpenAI
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# ✅ Streamlit secrets
client = OpenAI(api_key=st.secrets["openai_api_key"])

# ✅ Dummy ERP Data (Simulated!)
erp_data = pd.DataFrame({
    "Policy_ID": range(1, 101),
    "Region": ["Καρδίτσα"] * 40 + ["Αθήνα"] * 30 + ["Θεσσαλονίκη"] * 30,
    "Coverage_Type": ["Φυσικές Καταστροφές"] * 60 + ["Κλοπή"] * 40,
    "Active": [True] * 100
})

# ✅ Simulated external event
external_event = {
    "Disaster_Type": "Πλημμύρα",
    "Location": "Καρδίτσα"
}

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

# ✅ Streamlit setup
st.set_page_config(page_title="AI Decision Support System", layout="wide")
st.title("🚗 AI Decision Support System για Ασφαλιστικές")
st.markdown("Ανέβασε Excel, δες ανάλυση, λάβε alerts και προτάσεις!")

# ✅ File upload
uploaded_file = st.file_uploader("📂 Ανέβασε το Excel αρχείο σου", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📊 Τα δεδομένα σου:")
        st.dataframe(df)

        # ✅ Executive Summary
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

        # ✅ Γράφημα
        st.subheader("📊 Ανάλυση Δεδομένων:")
        region_sum = df.groupby("Region")["Amount_EUR"].sum()

        fig, ax = plt.subplots()
        region_sum.plot(kind='bar', ax=ax)
        ax.set_ylabel("Σύνολο Αποζημιώσεων (€)")
        ax.set_title("Σύνολο Αποζημιώσεων ανά Περιοχή")
        st.pyplot(fig)

        # ✅ Damage Control Alerts
        st.subheader("🚨 Damage Control Alerts")

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

        # ✅ Simulation εξωτερικών γεγονότων
        st.subheader("🌍 Εξωτερικά Γεγονότα & Εκτίμηση Ρίσκου")

        st.markdown(f"""
        - **Εξωτερικό Γεγονός:** {external_event['Disaster_Type']} στην {external_event['Location']}
        - Αναλύουμε δεδομένα ERP για πιθανή έκθεση...
        """)

        affected_policies = erp_data[
            (erp_data["Region"] == external_event["Location"]) &
            (erp_data["Coverage_Type"] == "Φυσικές Καταστροφές") &
            (erp_data["Active"])
        ]

        num_affected = affected_policies.shape[0]

        if num_affected > 0:
            st.error(f"🚨 Υπάρχουν {num_affected} ενεργά συμβόλαια με κάλυψη φυσικών καταστροφών στην {external_event['Location']}!")
            st.dataframe(affected_policies)

        else:
            st.success(f"✅ Δεν υπάρχουν ενεργά συμβόλαια με κάλυψη φυσικών καταστροφών στην {external_event['Location']}!")

        # ✅ Εκτίμηση πιθανής συνολικής αποζημίωσης (Impact Analysis)

        average_payout = df["Amount_EUR"].mean()
        estimated_total_exposure = num_affected * average_payout

        if num_affected > 0:
            st.warning(f"💰 Εκτιμώμενη Οικονομική Έκθεση: περίπου {estimated_total_exposure:,.2f} €")
        else:
            st.success("✅ Δεν υπάρχει εκτιμώμενη οικονομική έκθεση για το τρέχον γεγονός.")

        if num_affected > 0:
            subject = f"🚨 Προειδοποίηση: {external_event['Disaster_Type']} στην {external_event['Location']}"
            body = f"""
Εξωτερικό γεγονός: {external_event['Disaster_Type']} στην {external_event['Location']}.
Υπάρχουν {num_affected} ενεργά συμβόλαια με κάλυψη φυσικών καταστροφών.

💰 Εκτιμώμενη Οικονομική Έκθεση: περίπου {estimated_total_exposure:,.2f} €

Λεπτομέρειες συμβολαίων:
{affected_policies.to_string(index=False)}
"""
            send_email_alert(subject, body)

        # ✅ AI Σύμβουλος
        user_question = st.text_input("✍️ Κάνε την ερώτησή σου στο AI:")

        if user_question:
            with st.spinner('🧠 Το AI σκέφτεται...'):
                prompt = f"""
                Είσαι ένας έμπειρος σύμβουλος για ασφαλιστικές εταιρείες.
                Σου δίνω τα εξής δεδομένα claims:
                {df.to_string(index=False)}

                Σου δίνω και δεδομένα ERP συμβολαίων:
                {erp_data.to_string(index=False)}

                Και το εξωτερικό γεγονός:
                {external_event['Disaster_Type']} στην {external_event['Location']}

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

        # ✅ Daily Report Button
        st.subheader("📧 Daily Report")

        if st.button("📤 Στείλε Daily Report"):
            subject = "📊 Daily Insurance Report"
            body = f"""
Daily Insurance Summary:

- Σύνολο αποζημιώσεων: {total_claims} €
- Μέση αποζημίωση: {average_claim:.2f} €
- Μέγιστη αποζημίωση: {max_claim} €
- Ελάχιστη αποζημίωση: {min_claim} €
- Περιοχή με τις μεγαλύτερες αποζημιώσεις: {top_region}

Εξωτερικό γεγονός: {external_event['Disaster_Type']} στην {external_event['Location']}
Ενεργά συμβόλαια στην περιοχή: {num_affected}
Εκτιμώμενη οικονομική έκθεση: περίπου {estimated_total_exposure:,.2f} €
"""
            send_email_alert(subject, body)

    except Exception as e:
        st.error(f"🚨 Προέκυψε πρόβλημα με το αρχείο: {e}")

else:
    st.info("💡 Ανέβασε ένα Excel για να ξεκινήσεις.")
