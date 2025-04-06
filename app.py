import streamlit as st
import pandas as pd
from openai import OpenAI
from io import StringIO

# OpenAI client - το API key θα το βάλουμε με Streamlit secrets για ασφάλεια
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Page settings
st.set_page_config(page_title="AI Decision Support System", layout="wide")
st.title("🚗 AI Decision Support System για Ασφαλιστικές")
st.markdown("Ανέβασε Excel, ρώτησε το AI, πάρε business insights!")

# File uploader
uploaded_file = st.file_uploader("📂 Ανέβασε το Excel αρχείο σου", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Διαβάζουμε το αρχείο
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Εμφάνιση δεδομένων
        st.subheader("📊 Τα δεδομένα σου:")
        st.dataframe(df)
        st.subheader("📊 Τα δεδομένα σου:")
st.dataframe(df)

# -------------------------------
# 🎨 ΝΕΟ: Γραφήματα αποζημιώσεων ανά περιοχή
import matplotlib.pyplot as plt

st.subheader("📊 Ανάλυση Δεδομένων:")

# Σύνολο αποζημιώσεων ανά περιοχή
region_sum = df.groupby("Region")["Amount_EUR"].sum()

fig, ax = plt.subplots()
region_sum.plot(kind='bar', ax=ax)
ax.set_ylabel("Σύνολο Αποζημιώσεων (€)")
ax.set_title("Σύνολο Αποζημιώσεων ανά Περιοχή")
st.pyplot(fig)
# -------------------------------

# Υπάρχει ήδη παρακάτω το input για την ερώτηση στο AI, άστο ως έχει ✅
user_question = st.text_input("✍️ Κάνε την ερώτησή σου στο AI:")


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

    except Exception as e:
        st.error(f"🚨 Προέκυψε πρόβλημα με το αρχείο: {e}")

else:
    st.info("💡 Ανέβασε ένα Excel για να ξεκινήσεις.")
