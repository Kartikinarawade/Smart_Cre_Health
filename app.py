# train_model.py

import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Sample training data
data = {
    'age': [25, 30, 45, 50, 60],
    'gender': [0, 1, 0, 1, 0],  # 0 = Male, 1 = Female
    'bmi': [22.0, 28.5, 26.2, 31.0, 29.8],
    'children': [0, 2, 1, 3, 0],
    'smoker': [0, 1, 0, 1, 1],
    'premium': [3000, 10000, 5000, 15000, 12000]
}

df = pd.DataFrame(data)

# Features and target
X = df[['age', 'gender', 'bmi', 'children', 'smoker']]
y = df['premium']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model to a file
with open("model.pickle", "wb") as file:
    pickle.dump(model, file)

print("✅ Model saved as model.pickle")
# app.py

import streamlit as st
import pickle
import pandas as pd
from datetime import datetime
import os

# Load model with safety
@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model.pickle")
    with open(model_path, "rb") as file:
        return pickle.load(file)

# Set up Streamlit page
st.set_page_config(page_title="Smart Care Insurance App", layout="centered")

# Sidebar branding
with st.sidebar:
    st.image("https://img.lovepik.com/photo/50066/9634.jpg_wh860.jpg", width=140)
    st.markdown("## SmartCare Health")
    st.markdown("*Your Health. Our Priority.* 💙")

# Banner image
st.image("https://img.lovepik.com/photo/50066/9634.jpg_wh860.jpg", use_column_width=True, caption="Stay Covered. Stay Healthy.")
st.title("Smart Care Insurance App")
st.write("Predict your health insurance premium with this smart, AI-powered tool.")

# Theme toggle
theme = st.radio("Choose Theme", ["💡 Light", "🌙 Dark"], horizontal=True)
if theme == "🌙 Dark":
    st.markdown("""
        <style>
        body {background-color: #1e1e1e; color: white;}
        .stButton button {background-color: #444444; color: white;}
        </style>
        """, unsafe_allow_html=True)

# Inputs
st.subheader("Enter Your Details")
age = st.number_input("Age", min_value=0, max_value=120)
bmi = st.number_input("BMI (Body Mass Index)", min_value=0.0, max_value=100.0, step=0.1)

# BMI feedback
if bmi > 0:
    st.caption("BMI Category:")
    if bmi < 18.5:
        st.info("Underweight")
        bmi_status, color = "Underweight", "blue"
    elif 18.5 <= bmi < 25:
        st.success("Normal")
        bmi_status, color = "Normal", "green"
    elif 25 <= bmi < 30:
        st.warning("Overweight")
        bmi_status, color = "Overweight", "orange"
    else:
        st.error("Obese")
        bmi_status, color = "Obese", "red"

    st.markdown(f"""
        <div style='background-color:#eee; padding:5px; border-radius:10px;'>
            <strong>BMI Score:</strong> {bmi} ({bmi_status})<br>
            <progress value="{bmi}" max="40" style="width:100%; height:20px; color:{color}; background-color:#ddd;"></progress>
        </div>
        """, unsafe_allow_html=True)

children = st.number_input("Number of Children", min_value=0, max_value=10)
gender_input = st.radio("Gender", ["Male", "Female"], horizontal=True)
gender = 0 if gender_input == "Male" else 1
smoking_input = st.radio("Smoking Status", ["🚭 I do not smoke", "🚬 I am a smoker"])
smoker = 0 if "not" in smoking_input else 1

# Reset
if st.button("🔁 Reset Inputs"):
    st.experimental_rerun()

# Try loading model
try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# Prediction
if st.button("Predict Premium"):
    try:
        with st.spinner("Calculating your premium..."):
            input_data = [[age, gender, bmi, children, smoker]]
            prediction = model.predict(input_data)[0]
        now = datetime.now().strftime("%d %B %Y, %I:%M %p")
        st.success(f"Estimated Insurance Premium: ₹{prediction:.2f}")
        st.info(f"Prediction Date: {now}")

        risk_score = age * 0.2 + bmi * 0.3 + (smoker * 30)
        risk_level = "Low" if risk_score < 50 else "Medium" if risk_score < 100 else "High"
        st.metric("Estimated Risk Level", value=risk_level, delta=f"Score: {risk_score:.1f}")

        # Health advice
        st.subheader("Health Tips")
        tips = []
        if bmi_status == "Underweight":
            tips.append("• Consult a nutritionist for healthy weight gain.")
        elif bmi_status == "Overweight":
            tips.append("• Consider a calorie-controlled diet and exercise plan.")
        elif bmi_status == "Obese":
            tips.append("• Medical consultation is highly recommended.")
        if age > 50:
            tips.append("• Annual full-body checkups are advised.")
        if smoker:
            tips.append("• Enroll in a smoking cessation program.")
        if not tips:
            tips.append("• You're on the right track. Keep it up!")

        for tip in tips:
            st.markdown(f"✅ {tip}")

        # Report
        report = f"""
Smart Care Insurance Report

Date: {now}
Age: {age}
Gender: {gender_input}
BMI: {bmi} ({bmi_status})
Children: {children}
Smoker: {"Yes" if smoker else "No"}

Estimated Premium: ₹{prediction:.2f}
Risk Level: {risk_level} (Score: {risk_score:.1f})
"""
        st.download_button("Download Report", report, file_name="insurance_report.txt", mime="text/plain")

    except Exception as e:
        st.error(f"Prediction error: {e}")

# Mini health chatbot
st.subheader("🤖 Ask HealthBot")
question = st.text_input("Ask a question about health, BMI, smoking, or insurance.")
if question:
    q = question.lower()
    if "bmi" in q:
        st.write("BMI (Body Mass Index) measures body fat based on height and weight.")
    elif "smoking" in q:
        st.write("Smoking significantly increases health risks and premium costs.")
    elif "premium" in q:
        st.write("Premium is the periodic amount paid for your insurance policy.")
    else:
        st.write("This bot answers basic health-related queries. Try asking about BMI, smoking, or premiums.")
