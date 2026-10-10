import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Pakistan Bank Financing & Shariah Portal",
    page_icon="🏦",
    layout="wide"
)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "1. Loan Eligibility & Comparison",
        "2. Bank Directory & Products",
        "3. Amortization Schedule",
        "4. Shariah vs Conventional Guide"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Pakistan Banking Compliance:**\n"
    "- Rates are indicative flat estimates based on prevailing KIBOR spreads.\n"
    "- Debt Burden Ratio follows State Bank of Pakistan (SBP) consumer regulations."
)

# ==============================================================================
# PAGE 1: LOAN ELIGIBILITY & COMPARISON
# ==============================================================================
if page == "1. Loan Eligibility & Comparison":
    st.title("Loan Eligibility & Financing Comparison")
    st.write("Assess your borrowing profile against SBP benchmarks and compare Islamic vs Conventional repayment schedules.")
    st.markdown("---")

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.subheader("Applicant Profile")
        monthly_income = st.slider("Monthly Gross Income (PKR)", 25000, 1000000, 120000, step=5000)
        age = st.slider("Applicant Age (Years)", 18, 65, 30, step=1)
        job_type = st.selectbox(
            "Employment Category",
            ["Government Job", "Private Job - Permanent", "Business Owner", "Freelancer / Contractual"]
        )
        credit_history = st.selectbox(
            "Credit History (e-CIB Rating)",
            ["Excellent", "Good", "Average", "Poor"],
            index=1
        )

        st.subheader("Financing Details")
        loan_type = st.selectbox(
            "Financing Category",
            ["Auto Financing (Car Ijarah)", "Home Financing (Diminishing Musharakah)", "Personal Loan", "SME / Business Loan"]
        )
        asset_price = st.number_input("Total Asset Value / Facility Amount (PKR)", min_value=100000, value=2000000, step=100000)
        down_payment_pct = st.slider("Down Payment (%)", 0, 80, 20, step=5)
        
        down_payment_amt = asset_price * (down_payment_pct / 100)
        loan_amount = asset_price - down_payment_amt
        tenure_years = st.slider("Tenure (Years)", 1, 7, 3, step=1)

        st.caption(f"**Equity Paid:** PKR {down_payment_amt:,.0f} | **Principal Financed:** PKR {loan_amount:,.0f}")

    # Calculations
    score = 0
    if monthly_income >= 120000:
        score += 30
    elif monthly_income >= 60000:
        score += 20
    elif monthly_income >= 35000:
        score += 10

    score += 20 if 25 <= age <= 50 else 10

    job_weights = {"Government Job": 25, "Private Job - Permanent": 20, "Business Owner": 15, "Freelancer / Contractual": 5}
    score += job_weights.get(job_type, 0)

    credit_weights = {"Excellent": 25, "Good": 15, "Average": 10, "Poor": 0}
    score += credit_weights.get(credit_history, 0)
    score = min(score, 96)

    # Rates: Indicative Flat Models
    islamic_flat_rate = 0.205
    conv_flat_rate = 0.235
    months = tenure_years * 12

    islamic_total_markup = loan_amount * islamic_flat_rate * tenure_years
    conv_total_interest = loan_amount * conv_flat_rate * tenure_years

    islamic_monthly = (loan_amount + islamic_total_markup) / months
    conv_monthly = (loan_amount + conv_total_interest) / months

    dbr_pct = (islamic_monthly / monthly_income) * 100

    with col_out:
        st.subheader("Assessment Results")

        if score >= 70 and dbr_pct <= 45:
            status_title = "Eligible"
            status_color = "#10B981"
            status_msg = "Strong profile. Low default risk under SBP Consumer Prudential Regulations."
        elif score >= 50 or dbr_pct <= 50:
            status_title = "Conditional Approval"
            status_color = "#F59E0B"
            status_msg = "Borderline assessment. May require additional co-borrowers or collateral."
        else:
            status_title = "High Risk / Ineligible"
            status_color = "#EF4444"
            status_msg = "Debt ratio exceeds policy thresholds or credit history requires seasoning."

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100"},
            title={"text": f"<b>{status_title}</b>", "font": {"size": 18, "color": status_color}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": status_color},
                "steps": [
                    {"range": [0, 50], "color": "#FEE2E2"},
                    {"range": [50, 70], "color": "#FEF3C7"},
                    {"range": [70, 100], "color": "#D1FAE5"}
                ],
            }
        ))
        fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

        if dbr_pct > 50:
            st.error(f"**DBR Warning:** Monthly debt accounts for **{dbr_pct:.1f}%** of income (SBP recommended cap: 40-50%).")
        else:
            st.success(f"**DBR Compliant:** Debt represents **{dbr_pct:.1f}%** of net disposable income.")

        st.info(status_msg)

        # Comparison Table
        st.markdown("### Cost Breakdown")
        comp_df = pd.DataFrame({
            "Metric": ["Principal Borrowed", "Monthly Installment", "Total Markup / Cost", "Total Repayment"],
            "Islamic Banking (Meezan/BankIslami)": [f"PKR {loan_amount:,.0f}", f"PKR {islamic_monthly:,.0f}", f"PKR {islamic_total_markup:,.0f}", f"PKR {(loan_amount + islamic_total_markup):,.0f}"],
            "Conventional Banking (HBL/UBL)": [f"PKR {loan_amount:,.0f}", f"PKR {conv_monthly:,.0f}", f"PKR {conv_total_interest:,.0f}", f"PKR {(loan_amount + conv_total_interest):,.0f}"]
        })
        st.table(comp_df)


# ==============================================================================
# PAGE 2: BANK DIRECTORY & PRODUCTS
# ==============================================================================
elif page == "2. Bank Directory & Products":
    st.title("Pakistani Banks Directory & Financing Schemes")
    st.write("Overview of consumer financing schemes available across leading financial institutions.")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Islamic Financial Institutions", "Conventional Financial Institutions"])

    with tab1:
        st.subheader("Shariah-Compliant Banks")
        st.markdown("""
        * **Meezan Bank Ltd:**
          * Products: *Car Ijarah*, *Easy Home*, *Consumer Musharakah*
          * Typical Benchmark: 1Y KIBOR + Bank Spread
          * Late Payment Policy: Charity pool allocations (strictly non-interest)
        * **BankIslami Pakistan:**
          * Products: *Muskun Home Financing*, *Auto Ijarah*
          * Focus: Fast-track digital approvals and verified asset procurement
        * **Faysal Bank (Barkat Islamic):**
          * Products: Complete full-conversion Islamic banking suite
        """)

    with tab2:
        st.subheader("Conventional Commercial Banks")
        st.markdown("""
        * **Habib Bank Limited (HBL):**
          * Products: *HBL CarLoan*, *HBL Home Finance*, *Personal Loans*
          * Model: Variable/fixed loan interest tied to 3M/1Y KIBOR
        * **United Bank Limited (UBL):**
          * Products: *UBL Drive*, *UBL Address*
        * **Bank Alfalah:**
          * Products: Flexible tenure personal installment loans
        """)

    st.markdown("---")
    st.subheader("General Document Requirements")
    st.markdown("""
    - **Salaried Individuals:** Valid CNIC, last 3 to 6 months' salary slips, salary bank statement (6 months), employment certificate.
    - **Self-Employed / Business:** Proof of business registration, NTN certificate, audited/active bank statements (12 months).
    """)


# ==============================================================================
# PAGE 3: AMORTIZATION SCHEDULE
# ==============================================================================
elif page == "3. Amortization Schedule":
    st.title("Annual Repayment Schedule")
    st.write("Examine how principal and profit distribute across the lifetime of the facility.")
    st.markdown("---")

    loan_p = st.number_input("Enter Loan Capital (PKR)", value=1000000, step=50000)
    tenure_y = st.slider("Select Duration (Years)", 1, 10, 5)
    rate_pct = st.slider("Indicative Flat Rate (% per annum)", 10.0, 35.0, 21.0, step=0.5)

    annual_profit = loan_p * (rate_pct / 100)
    annual_principal = loan_p / tenure_y
    annual_payment = annual_principal + annual_profit

    remaining = loan_p
    schedule = []

    for year in range(1, tenure_y + 1):
        remaining -= annual_principal
        schedule.append({
            "Year": f"Year {year}",
            "Opening Balance (PKR)": f"{remaining + annual_principal:,.0f}",
            "Principal Repaid (PKR)": f"{annual_principal:,.0f}",
            "Profit / Markup Paid (PKR)": f"{annual_profit:,.0f}",
            "Total Annual Payment (PKR)": f"{annual_payment:,.0f}",
            "Ending Balance (PKR)": f"{max(0, remaining):,.0f}"
        })

    schedule_df = pd.DataFrame(schedule)
    st.dataframe(schedule_df, use_container_width=True)

    csv_data = schedule_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Schedule as CSV",
        data=csv_data,
        file_name="loan_repayment_schedule.csv",
        mime="text/csv"
    )


# ==============================================================================
# PAGE 4: SHARIAH VS CONVENTIONAL GUIDE
# ==============================================================================
elif page == "4. Shariah vs Conventional Guide":
    st.title("Understanding Islamic vs Conventional Finance")
    st.write("A structured overview of core operational and structural differences.")
    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Islamic Banking Structure")
        st.markdown("""
        * **Asset-Backed Transactions:** Money cannot earn money directly. The transaction must involve physical goods, services, or assets.
        * **Risk-Sharing:** Both parties share equity or lease risks through contracts like *Musharakah* or *Ijarah*.
        * **No Riba (Interest):** No interest penalty charged for cash delays; penalty payments go exclusively to registered Shariah-compliant charities.
        * **Governance:** Audited by internal Shariah boards and governed by the SBP Islamic Banking Department.
        """)

    with col_b:
        st.subheader("Conventional Banking Structure")
        st.markdown("""
        * **Debtor-Creditor Relationship:** The bank lends funds and receives interest on the underlying capital.
        * **Compounding Charges:** Delinquency or default often triggers compounding interest penalties.
        * **Pure Financial Lending:** Does not necessarily involve buying, selling, or leasing the underlying asset.
        * **Governance:** Subject to standard commercial and monetary regulatory frameworks.
        """)

    st.markdown("---")
    st.subheader("Common Shariah Terminology")
    st.markdown("""
    | Arabic / Islamic Term | Meaning | Typical Use Case |
    | :--- | :--- | :--- |
    | **Murabaha** | Cost-plus sales transaction | Raw materials, short-term equipment purchase |
    | **Ijarah** | Shariah-compliant lease agreement | Automobile financing |
    | **Diminishing Musharakah** | Gradual ownership transfer partnership | Home purchasing and construction |
    | **Takaful** | Cooperative risk-sharing insurance | Vehicle and property coverage |
    """)