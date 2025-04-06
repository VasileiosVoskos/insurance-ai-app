import streamlit as st
import pandas as pd
from openai import OpenAI
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import os

# OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.set_page_config(page_title="AI Decision Support System", layout="wide")
st.title("🚗 AI Decision Support System για Ασφαλιστικές")
st.markdown("Ανέβασε Excel, ρώτησε το AI, πάρε business insights!")

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

        # 🚨 Live Alerts: High Claim Amounts with dynamic threshold
        st.subheader("🚨 Damage Control Alerts")

        # Ρυθμιζόμενο όριο αποζημίωσης από τον χρήστη!
        alert_threshold = st.slider("🚦 Όρισε το όριο alert αποζημίωσης (€):", min_value=500, max_value=10000, value=3000, step=500)

        high_claims = df[df["Amount_EUR"] > alert_threshold]

        if not high_claims.empty:
            st.error(f"⚠️ Προσοχή! Υπάρχουν {len(high_claims)} αποζημιώσεις πάνω από {alert_threshold}€:")
            st.dataframe(high_claims)
        else:
            st.success(f"✅ Καμία αποζημίωση δεν ξεπερνά το όριο των {alert_threshold}€!")

        # Ερώτηση στον AI
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

                # 📝 PDF Export Button
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
