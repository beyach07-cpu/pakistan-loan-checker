import streamlit as st
import plotly.graph_objects as go

# Page Configuration (Mobile-friendly responsive layout)
st.set_page_config(
    page_title="Pakistan Islamic vs Conventional Loan Checker",
    page_icon="🇵🇰",
    layout="wide"
)

# Header
st.markdown("# 🇵🇰 Pakistan Bank Loan Eligibility Checker - Islamic vs Conventional")
st.caption(
    "Apni eligibility score check karein aur Pakistani Islamic Banks (Meezan waghera) "
    "aur Conventional Banks (HBL/UBL waghera) ki monthly Qist ka mawazna karein."
)

st.write("---")

# Layout: Do columns (Mobile par automatically stack ho jayeingay)
col_input, col_output = st.columns([1, 1], gap="large")

# ---------------------------------------------
# Left Column: Inputs
# ---------------------------------------------
with col_input:
    st.subheader("📝 Applicant Details")

    income = st.slider(
        "💵 Monthly Income (PKR)",
        min_value=20000,
        max_value=500000,
        value=70000,
        step=5000
    )

    age = st.slider(
        "🎂 Age",
        min_value=18,
        max_value=65,
        value=27,
        step=1
    )

    job_type = st.selectbox(
        "💼 Job Type",
        [
            "Government Job",
            "Private Job - Permanent",
            "Business Owner",
            "Freelancer / Contract"
        ],
        index=1
    )

    credit_history = st.radio(
        "📈 Credit History (e-CIB)",
        ["Excellent", "Good", "Average", "Poor"],
        index=1,
        horizontal=True
    )

    loan_amount = st.number_input(
        "💰 Loan Amount (PKR)",
        min_value=50000,
        value=800000,
        step=50000
    )

    loan_type = st.selectbox(
        "🚗 Loan Type",
        [
            "Car Loan (Ijarah)",
            "Personal Loan",
            "Home Loan",
            "Business Loan"
        ],
        index=0
    )

    duration_years = st.slider(
        "⏳ Duration (Years)",
        min_value=1,
        max_value=7,
        value=3,
        step=1
    )

    calculate_btn = st.button("🔍 Check Eligibility + Compare Banks", type="primary", use_container_width=True)

# ---------------------------------------------
# Logic & Calculations
# ---------------------------------------------
score = 0

# 1. Income points
if income >= 100000:
    score += 30
elif income >= 60000:
    score += 20
elif income >= 35000:
    score += 10

# 2. Age points
if 25 <= age <= 50:
    score += 20
else:
    score += 10

# 3. Job points
job_scores = {
    "Government Job": 25,
    "Private Job - Permanent": 20,
    "Business Owner": 15,
    "Freelancer / Contract": 5
}
score += job_scores.get(job_type, 0)

# 4. Credit points
credit_scores = {
    "Excellent": 25,
    "Good": 15,
    "Average": 10,
    "Poor": 0
}
score += credit_scores.get(credit_history, 0)

# Cap score at 96
score = min(score, 96)

# Status & Colors
if score >= 70:
    status_label = "🟢 ELIGIBLE"
    gauge_color = "#10B981"
    status_note = "Aapki profile strong hai! Banks aasani se loan approve kar sakte hain."
elif score >= 50:
    status_label = "🟠 MAYBE"
    gauge_color = "#F59E0B"
    status_note = "Aap borderline candidate hain. Bank guarantor ya barhi down payment maang sakta hai."
else:
    status_label = "🔴 LOW CHANCE"
    gauge_color = "#EF4444"
    status_note = "Loan approval ke imkanaat kam hain. Credit history behtar karein ya loan amount kam karein."

# Installment calculation
months = duration_years * 12
islamic_monthly = (loan_amount + loan_amount * 0.21 * duration_years) / months
conventional_monthly = (loan_amount + loan_amount * 0.23 * duration_years) / months

# Plotly Gauge Chart
fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 28}},
        title={"text": "<b>Eligibility Score</b>", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": gauge_color},
            "steps": [
                {"range": [0, 50], "color": "#FEE2E2"},
                {"range": [50, 70], "color": "#FEF3C7"},
                {"range": [70, 100], "color": "#D1FAE5"}
            ],
            "threshold": {
                "line": {"color": gauge_color, "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    )
)
fig.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))

# ---------------------------------------------
# Right Column: Outputs
# ---------------------------------------------
with col_output:
    st.subheader("📊 Results & Bank Comparison")
    
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"### Status: {status_label}")
    st.info(status_note)

    st.markdown(f"""
    **Loan Summary:**
    - **Category:** {loan_type}
    - **Financing:** PKR {loan_amount:,.0f}
    - **Duration:** {duration_years} Saal ({months} Months)
    """)

    # Comparison Table
    table_md = f"""
| Bank Type | Bank Example | Monthly Qist | Concept |
| :--- | :--- | :--- | :--- |
| **Islamic** | Meezan Islamic | **PKR {islamic_monthly:,.0f}** | *Ijarah / Diminishing Musharakah* (Rent/Shirkah, Interest-free) |
| **Conventional** | HBL / UBL Conventional | **PKR {conventional_monthly:,.0f}** | *Interest-based Lending* (KIBOR spread flat loan) |
    """
    st.markdown(table_md)

    monthly_saving = conventional_monthly - islamic_monthly
    st.success(f"💡 Islamic option me aap har mahine taqreeban **PKR {monthly_saving:,.0f}** bacha sakte hain.")