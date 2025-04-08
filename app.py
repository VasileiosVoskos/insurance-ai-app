import streamlit as st
from PIL import Image

# Sidebar logo
logo = Image.open("assets/logo.png")
st.sidebar.image(logo, use_column_width=True)

# Sidebar navigation
st.sidebar.title("Μενού Πλοήγησης")
page = st.sidebar.radio("Πήγαινε σε:", ["Dashboard", "Upload & Analysis", "AI Σύμβουλος", "Reports", "Settings"])

# Page routing
if page == "Dashboard":
    exec(open("pages/1_Dashboard.py").read())
elif page == "Upload & Analysis":
    exec(open("pages/2_Upload_and_Analysis.py").read())
elif page == "AI Σύμβουλος":
    exec(open("pages/3_AI_Advisor.py").read())
elif page == "Reports":
    exec(open("pages/4_Reports.py").read())
elif page == "Settings":
    exec(open("pages/5_Settings.py").read())
