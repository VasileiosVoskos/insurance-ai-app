import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai_api_key"])

st.title("🧠 AI Σύμβουλος")

user_question = st.text_input("✍️ Κάνε την ερώτησή σου στο AI:")

if user_question:
    with st.spinner('🧠 Το AI σκέφτεται...'):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Είσαι ένας ειδικός σύμβουλος ασφαλιστικών εταιρειών."},
                {"role": "user", "content": user_question}
            ]
        )
        st.success("✅ Ο AI Σύμβουλός σου απαντά:")
        st.write(response.choices[0].message.content)
