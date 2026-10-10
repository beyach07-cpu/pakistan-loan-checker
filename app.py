import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Pakistan Bank Loan & Shariah Checker Pro",
    page_icon="🇵🇰",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🇵🇰 Pakistan Loan Eligibility & Bank Comparison Pro")
st.caption("State Bank guidelines aur Shariah usoolon ke mutabiq apni loan eligibility aur monthly qist check karein.")

st.write("---")

col_in, col_out = st.columns([1, 1], gap="large")

# ---------------------------------------------
# Input Section
# ---------------------------------------------
with col_in:
    st.subheader("👤 Applicant Profile")
    
    income = st.slider("💵 Monthly Net Salary / Income (PKR)", 20000, 1000000, 85000, step=5000)
    age = st.slider("🎂 Age (Years)", 18, 65, 29, step=1)
    
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        job_type = st.selectbox(
            "💼 Employment Type",
            ["Government Job", "Private Job - Permanent", "Business Owner", "Freelancer / Contract"]
        )
    with col_sub2:
        credit_history = st.selectbox(
            "📈 e-CIB / Credit History",
            ["Excellent", "Good", "Average", "Poor"]
        )

    st.subheader("🚗 Loan / Financing Details")
    loan_type = st.selectbox(
        "Facility Type",
        ["Car Loan / Ijarah", "Home Financing", "Personal Loan", "SME / Business Loan"]
    )

    total_price = st.number_input("💰 Total Asset / Required Price (PKR)", min_value=100000, value=1500000, step=50000)
    
    down_payment_pct = st.slider("📉 Down Payment / Advance (%)", min_value=0, max_value=70, value=20, step=5)
    down_payment_val = total_price * (down_payment_pct / 100)
    loan_amount = total_price - down_payment_val
    
    st.caption(f"📌 **Advance Raqam:** PKR {down_payment_val:,.0f} | **Asal Financing Amount:** PKR {loan_amount:,.0f}")

    duration_years = st.slider("⏳ Tenure / Muddat (Years)", 1, 7, 3, step=1)

# ---------------------------------------------
# Scoring & Calculation Logic
# ---------------------------------------------
# 1. Eligibility Score
score = 0
if income >= 120000:
    score += 30
elif income >= 60000:
    score += 20
elif income >= 35000:
    score += 10

if 25 <= age <= 50:
    score += 20
else:
    score += 10

job_pts = {"Government Job": 25, "Private Job - Permanent": 20, "Business Owner": 15, "Freelancer / Contract": 5}
score += job_pts.get(job_type, 0)

cred_pts = {"Excellent": 25, "Good": 15, "Average": 10, "Poor": 0}
score += cred_pts.get(credit_history, 0)
score = min(score, 96)

# 2. Monthly Installments (Indicative Rates)
months = duration_years * 12
islamic_rate = 0.205     # 20.5% Flat
conventional_rate = 0.235 # 23.5% Flat

islamic_monthly = (loan_amount + (loan_amount * islamic_rate * duration_years)) / months
conv_monthly = (loan_amount + (loan_amount * conventional_rate * duration_years)) / months

# 3. Debt-to-Burden Ratio (DBR / SBP Standard is ~40-50%)
dbr_ratio = (islamic_monthly / income) * 100

# Status Evaluation
if score >= 70 and dbr_ratio <= 45:
    status_text = "ELIGIBLE (High Approval)"
    status_color = "#10B981"
    note = "Shandaar profile! State Bank limits ke mutabiq aapki approval ke imkanaat bohat zyada hain."
elif score >= 50 or dbr_ratio <= 50:
    status_text = "BORDERLINE / CONDITIONAL"
    status_color = "#F59E0B"
    note = "Approval mil sakti hai lekin bank guarantor ya advance payment barhane ka keh sakta hai."
else:
    status_text = "LOW CHANCE"
    status_color = "#EF4444"
    note = "Qist aapki aamdani ke hisab se zyada hai ya score kam hai. Muddat (Tenure) barhain ya loan amount kam karein."

# ---------------------------------------------
# Output Section
# ---------------------------------------------
with col_out:
    st.subheader("📊 Eligibility Assessment")

    # Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100"},
        title={"text": f"<b>Score: {status_text}</b>", "font": {"size": 16, "color": status_color}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": status_color},
            "steps": [
                {"range": [0, 50], "color": "#fee2e2"},
                {"range": [50, 70], "color": "#fef3c7"},
                {"range": [70, 100], "color": "#d1fae5"}
            ],
        }
    ))
    fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # DBR Metric Box
    if dbr_ratio > 50:
        st.error(f"⚠️ **SBP Alert:** Monthly Qist aapki aamdani ka **{dbr_ratio:.1f}%** hai (SBP safe limit: 40-50%).")
    else:
        st.success(f"✅ **SBP Compliance:** Monthly Qist aapki aamdani ka **{dbr_ratio:.1f}%** hai (Safe zone).")

    st.info(note)

    # Bank Comparison Table
    st.markdown("### 🏦 Multi-Bank Monthly Qist Comparison")
    
    st.markdown(f"""
| Bank Name | Category | Approx. Monthly Qist | Model |
| :--- | :--- | :--- | :--- |
| **Meezan Bank** | Islamic | **PKR {islamic_monthly:,.0f}** | *Ijarah (Asset-backed)* |
| **BankIslami** | Islamic | **PKR {(islamic_monthly * 1.01):,.0f}** | *Diminishing Musharakah* |
| **HBL Bank** | Conventional | **PKR {conv_monthly:,.0f}** | *KIBOR + Markup Loan* |
| **Bank Alfalah** | Conventional | **PKR {(conv_monthly * 0.99):,.0f}** | *Fixed/Floating Interest* |
    """)

    # Donut Chart: Principal vs Profit
    total_islamic_profit = (islamic_monthly * months) - loan_amount
    fig_donut = go.Figure(data=[go.Pie(
        labels=['Asal Raqam (Principal)', 'Bank Markup / Profit'],
        values=[loan_amount, total_islamic_profit],
        hole=.5,
        marker_colors=['#059669', '#cbd5e1']
    )])
    fig_donut.update_layout(
        title_text="Total Payment Breakdown (Islamic)",
        height=220,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    savings_total = (conv_monthly - islamic_monthly) * months
    st.markdown(f"> 💡 Puri muddat me Islamic financing par taqreeban **PKR {savings_total:,.0f}** ki bachat mutawaqa hai.")