import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# Load data
df = pd.read_csv("data/employee_data.csv")

# -----------------------------
# ENGAGEMENT INDEX
# -----------------------------

engagement_cols = [
    "JobInvolvement",
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction"
]

scaler = MinMaxScaler()
df[engagement_cols] = scaler.fit_transform(df[engagement_cols])

df["EngagementIndex"] = df[engagement_cols].mean(axis=1)

st.metric("Average Work-Life Balance", round(filtered["WorkLifeBalance"].mean(), 2))

# -----------------------------
# BURNOUT RISK
# -----------------------------

def burnout(row):
    if row["OverTime"] == "Yes" and row["WorkLifeBalance"] <= 2:
        return "High"
    elif row["OverTime"] == "Yes":
        return "Medium"
    else:
        return "Low"

df["BurnoutRisk"] = df.apply(burnout, axis=1)

# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title("Employee Engagement & Burnout Dashboard")

# Department Filter
department = st.selectbox("Select Department", df["Department"].unique())
filtered = df[df["Department"] == department]

overtime_filter = st.selectbox("Overtime", ["All", "Yes", "No"])

if overtime_filter != "All":
    filtered = filtered[filtered["OverTime"] == overtime_filter]

# Metrics
st.subheader("Key Metrics")

st.metric("Average Engagement Score", round(filtered["EngagementIndex"].mean(), 2))
st.metric("High Burnout Employees", filtered[filtered["BurnoutRisk"] == "High"].shape[0])


st.subheader("Burnout Risk Distribution")

burnout_counts = filtered["BurnoutRisk"].value_counts().reset_index()
burnout_counts.columns = ["BurnoutRisk", "Count"]

fig = px.bar(
    burnout_counts,
    x="BurnoutRisk",
    y="Count",
    title="Burnout Risk Levels"
)

st.plotly_chart(fig)

st.subheader("Engagement vs Attrition")

attrition_engagement = (
    filtered.groupby("Attrition")["EngagementIndex"]
    .mean()
    .reset_index()
)

attrition_engagement["Attrition"] = attrition_engagement["Attrition"].map({0: "Stayed", 1: "Left"})

fig2 = px.bar(
    attrition_engagement,
    x="Attrition",
    y="EngagementIndex",
    title="Average Engagement: Stayed vs Left"
)

st.plotly_chart(fig2)

# Show Data
st.subheader("Employee Data")
st.dataframe(filtered)

threshold = st.slider("Select Engagement Alert Threshold", 0.0, 1.0, 0.4)

low_engagement = filtered[filtered["EngagementIndex"] < threshold]


st.metric("Low Engagement Employees", low_engagement.shape[0])

st.subheader("Low Engagement Employees")

st.dataframe(low_engagement)