import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ---------------------------------------------------------
# Page Configuration & Global Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="PakFinance Pro | SBP & Shariah Compliant Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Financial Portal Look
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .badge-pass { background-color: #dcfce7; color: #15803d; }
    .badge-warn { background-color: #fef9c3; color: #a16207; }
    .badge-fail { background-color: #fee2e2; color: #b91c1c; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Financial Formula Helpers (Standard Reducing Balance)
# ---------------------------------------------------------
def calculate_reducing_emi(principal: float, annual_rate_pct: float, tenure_years: int) -> float:
    """Calculates standard reducing balance monthly installment (Amortization formula)."""
    if principal <= 0 or tenure_years <= 0:
        return 0.0
    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    num_months = tenure_years * 12
    if monthly_rate == 0:
        return principal / num_months
    emi = principal * (monthly_rate * (1 + monthly_rate)**num_months) / ((1 + monthly_rate)**num_months - 1)
    return emi

# ---------------------------------------------------------
# Sidebar Navigation & Benchmark Settings
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏛️ **PakFinance Engine**")
    st.caption("State Bank Consumer Regulations & Shariah Desk")
    st.markdown("---")

    page = st.radio(
        "Navigation Menu",
        [
            "📊 Eligibility & KIBOR Comparison",
            "🏢 Bank Directory & Product Rules",
            "📅 Amortization Matrix (Reducing)",
            "📖 Shariah vs Conventional Framework"
        ]
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Benchmark Assumptions")
    base_kibor = st.number_input("1-Year KIBOR Benchmark (%)", min_value=5.0, max_value=30.0, value=14.5, step=0.25)
    islamic_spread = st.slider("Islamic Bank Spread (%)", 1.0, 6.0, 2.5, step=0.25)
    conv_spread = st.slider("Conventional Spread (%)", 1.0, 6.0, 3.5, step=0.25)
    
    st.caption(f"• **Islamic APR:** {base_kibor + islamic_spread:.2f}%\n• **Conventional APR:** {base_kibor + conv_spread:.2f}%")

# ==============================================================================
# PAGE 1: ELIGIBILITY & KIBOR COMPARISON
# ==============================================================================
if page == "📊 Eligibility & KIBOR Comparison":
    st.title("Loan Eligibility & Financing Assessment")
    st.caption("Real-world reducing balance calculations complying with SBP Consumer Prudential Regulations.")
    st.markdown("---")

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.subheader("1. Applicant Income & Existing Liabilities")
        monthly_income = st.number_input("Monthly Net Take-Home Salary (PKR)", min_value=25000, value=150000, step=5000)
        existing_debt = st.number_input(
            "Existing Monthly Debt / Credit Card Minimums (PKR)",
            min_value=0,
            value=15000,
            step=2500,
            help="Total monthly installments you currently pay across all Pakistani banks."
        )

        c_a1, c_a2 = st.columns(2)
        with c_a1:
            age = st.number_input("Age (Years)", 18, 65, 31)
            job_type = st.selectbox(
                "Employment Category",
                ["Government Service", "Permanent Private Job", "Business Owner / Self-Employed", "Contractual / Freelancer"]
            )
        with c_a2:
            credit_record = st.selectbox(
                "e-CIB / Credit Bureau History",
                ["Excellent / No Overdues", "Good / Minor Late Settlement", "Average / Recent Delinquencies", "Defaulter / Write-off"]
            )
            facility_type = st.selectbox(
                "Facility Category",
                ["Car Financing (Ijarah)", "Housing Facility (Diminishing Musharakah)", "Personal Loan"]
            )

        st.subheader("2. Financing Details")
        asset_price = st.number_input("Total Asset Value / Vehicle Price (PKR)", min_value=100000, value=3000000, step=100000)
        
        # SBP Floor Enforcement
        min_equity = 15 if facility_type == "Car Financing (Ijarah)" else (10 if facility_type == "Housing Facility (Diminishing Musharakah)" else 0)
        down_payment_pct = st.slider(f"Down Payment / Advance Equity (%) [Min SBP: {min_equity}%]", min_equity, 80, max(20, min_equity), step=5)
        
        down_payment_amt = asset_price * (down_payment_pct / 100.0)
        principal_borrowed = asset_price - down_payment_amt

        # SBP Max Tenure Floor Enforcement (e.g. 5 yrs max on auto)
        max_allowed_tenure = 5 if facility_type == "Car Financing (Ijarah)" else 20
        tenure_years = st.slider(f"Tenure (Years) [Max SBP: {max_allowed_tenure}]", 1, max_allowed_tenure, min(3, max_allowed_tenure), step=1)

        takaful_annual_pct = st.slider("Annual Takaful / Insurance Rate (%)", 1.0, 3.5, 2.0, step=0.1)

    # -----------------------------
    # Calculation Logic
    # -----------------------------
    # 1. Scoring
    score = 0
    if monthly_income >= 150000:
        score += 30
    elif monthly_income >= 80000:
        score += 20
    elif monthly_income >= 40000:
        score += 10

    score += 20 if 25 <= age <= 50 else 10
    
    job_scores = {"Government Service": 25, "Permanent Private Job": 20, "Business Owner / Self-Employed": 15, "Contractual / Freelancer": 5}
    score += job_scores.get(job_type, 0)

    cred_scores = {"Excellent / No Overdues": 25, "Good / Minor Late Settlement": 15, "Average / Recent Delinquencies": 5, "Defaulter / Write-off": 0}
    score += cred_scores.get(credit_record, 0)
    score = min(score, 96)

    # 2. Reducing Balance Installments
    islamic_effective_rate = base_kibor + islamic_spread
    conv_effective_rate = base_kibor + conv_spread

    islamic_base_emi = calculate_reducing_emi(principal_borrowed, islamic_effective_rate, tenure_years)
    conv_base_emi = calculate_reducing_emi(principal_borrowed, conv_effective_rate, tenure_years)

    # Monthly Takaful addition
    monthly_takaful = (asset_price * (takaful_annual_pct / 100.0)) / 12.0
    islamic_total_monthly = islamic_base_emi + monthly_takaful
    conv_total_monthly = conv_base_emi + monthly_takaful

    # SBP Total Debt Burden Ratio (DBR) including existing debt
    total_monthly_obligations = islamic_total_monthly + existing_debt
    dbr_pct = (total_monthly_obligations / monthly_income) * 100.0 if monthly_income > 0 else 100.0

    # -----------------------------
    # Outputs Section
    # -----------------------------
    with col_out:
        st.subheader("3. Regulatory & Repayment Assessment")

        # Metric Tiles
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Approval Score", f"{score}/100")
        with m2:
            st.metric("Total DBR", f"{dbr_pct:.1f}%")
        with m3:
            st.metric("Monthly Takaful", f"PKR {monthly_takaful:,.0f}")

        # Status Verdict
        if score >= 70 and dbr_pct <= 45:
            st.markdown('<span class="status-badge badge-pass">🟢 APPROVED / STRONG CANDIDATE</span>', unsafe_allow_html=True)
            st.success("Applicant satisfies SBP Consumer DBR ceilings (≤ 45%) and displays high creditworthiness.")
        elif score >= 50 and dbr_pct <= 50:
            st.markdown('<span class="status-badge badge-warn">🟠 CONDITIONAL APPROVAL</span>', unsafe_allow_html=True)
            st.warning("DBR is between 45% and 50%. The bank may mandate a co-borrower or reduce the principal.")
        else:
            st.markdown('<span class="status-badge badge-fail">🔴 REGULATORY REJECTION RISK</span>', unsafe_allow_html=True)
            st.error("Total debt obligations exceed 50% of verified net income. Increase tenure or payoff existing liabilities first.")

        # Gauge Chart
        fig_score = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0284c7"},
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 70], "color": "#fef3c7"},
                    {"range": [70, 100], "color": "#dcfce7"}
                ],
            }
        ))
        fig_score.update_layout(height=210, margin=dict(l=15, r=15, t=10, b=10))
        st.plotly_chart(fig_score, use_container_width=True)

        # Tabbed Output
        t1, t2 = st.tabs(["📊 Installment Comparison", "💡 DBR Capacity Breakdown"])
        
        with t1:
            comp_table = pd.DataFrame({
                "Parameter": [
                    "Principal Financed",
                    "Pure Financial EMI",
                    "Mandatory Takaful / Insurance",
                    "Total Outflow per Month",
                    "Total 3-Year Markup / Profit"
                ],
                "Islamic Banking": [
                    f"PKR {principal_borrowed:,.0f}",
                    f"PKR {islamic_base_emi:,.0f}",
                    f"PKR {monthly_takaful:,.0f}",
                    f"PKR {islamic_total_monthly:,.0f}",
                    f"PKR {(islamic_base_emi * tenure_years * 12 - principal_borrowed):,.0f}"
                ],
                "Conventional Banking": [
                    f"PKR {principal_borrowed:,.0f}",
                    f"PKR {conv_base_emi:,.0f}",
                    f"PKR {monthly_takaful:,.0f}",
                    f"PKR {conv_total_monthly:,.0f}",
                    f"PKR {(conv_base_emi * tenure_years * 12 - principal_borrowed):,.0f}"
                ]
            })
            st.dataframe(comp_table, hide_index=True, use_container_width=True)

        with t2:
            safe_dbr_cap = monthly_income * 0.45
            unencumbered_income = max(0.0, monthly_income - total_monthly_obligations)
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Existing Debt', 'New Loan Installment', 'Remaining Disposable Income'],
                values=[existing_debt, islamic_total_monthly, unencumbered_income],
                hole=.45,
                marker_colors=['#f87171', '#38bdf8', '#4ade80']
            )])
            fig_pie.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            st.caption(f"SBP Safe Debt Limit (45%): **PKR {safe_dbr_cap:,.0f}/mo** | Current Load: **PKR {total_monthly_obligations:,.0f}/mo**")

# ==============================================================================
# PAGE 2: BANK DIRECTORY & PRODUCT RULES
# ==============================================================================
elif page == "🏢 Bank Directory & Product Rules":
    st.title("Pakistani Banks: Regulatory & Product Constraints")
    st.write("Current consumer financing standards observed across leading domestic scheduled banks.")
    st.markdown("---")

    t_is, t_co = st.tabs(["Islamic Windows & Full Banks", "Conventional Scheduled Banks"])

    with t_is:
        st.markdown("""
        #### 1. Meezan Bank Limited
        * **Car Ijarah:** Minimum 20% down payment required on local assemblers; maximum tenure capped at 5 years.
        * **Easy Home (Diminishing Musharakah):** Unit purchase co-ownership; maximum tenure 20 years.
        * **Late Charges:** Fines do not accrue as income; pooled directly into verified charity accounts.

        #### 2. BankIslami Pakistan
        * **Muskun Home Financing & Auto Ijarah:** Periodic rent adjustments tied to 1-Year KIBOR revisions.
        """)

    with t_co:
        st.markdown("""
        #### 1. Habib Bank Limited (HBL) & United Bank Limited (UBL)
        * **Retail Car Loans:** Floating rate reset annually on the customer agreement anniversary.
        * **Default Mechanism:** Late compounding penalties are capitalized into the principal debt.
        * **Consumer Personal Loans:** SBP mandates maximum clean personal financing exposure is capped at PKR 5 Million per individual.
        """)

# ==============================================================================
# PAGE 3: AMORTIZATION MATRIX (REDUCING BALANCE)
# ==============================================================================
elif page == "📅 Amortization Matrix (Reducing)":
    st.title("Month-by-Month Amortization Matrix")
    st.caption("True reducing balance schedule illustrating declining profit charges over time.")
    st.markdown("---")

    f1, f2, f3 = st.columns(3)
    with f1:
        p_val = st.number_input("Financed Capital (PKR)", value=2000000, step=100000)
    with f2:
        t_yrs = st.slider("Financing Duration (Years)", 1, 10, 3)
    with f3:
        apr = st.number_input("Effective APR / KIBOR+Spread (%)", value=17.0, step=0.25)

    emi = calculate_reducing_emi(p_val, apr, t_yrs)
    m_rate = (apr / 100.0) / 12.0
    total_m = t_yrs * 12

    schedule = []
    balance = p_val

    for m in range(1, total_m + 1):
        profit_charge = balance * m_rate
        principal_component = emi - profit_charge
        ending_balance = max(0.0, balance - principal_component)

        # Record yearly summary or display sampled output
        if m % 12 == 0 or m == total_m or m == 1:
            schedule.append({
                "Month": m,
                "Beginning Balance (PKR)": f"{balance:,.0f}",
                "Monthly Installment (PKR)": f"{emi:,.0f}",
                "Principal Paid (PKR)": f"{principal_component:,.0f}",
                "Profit Paid (PKR)": f"{profit_charge:,.0f}",
                "Ending Balance (PKR)": f"{ending_balance:,.0f}"
            })
        balance = ending_balance

    st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)
    st.info("Displaying annual benchmark intervals for compact viewing. Use CSV download for full 1–84 months detail.")

# ==============================================================================
# PAGE 4: SHARIAH VS CONVENTIONAL FRAMEWORK
# ==============================================================================
elif page == "📖 Shariah vs Conventional Framework":
    st.title("Operational & Regulatory Distinction")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🌙 Islamic Financing Operations")
        st.markdown("""
        * **Asset-Linked:** The bank cannot lend pure liquidity at interest; it must acquire title to the tangible asset first.
        * **Risk Bearing:** If an asset is completely destroyed during lease (*Ijarah*) without customer negligence, rent liability halts.
        * **Strict Penalties:** Penalty on late payments is fixed in advance and redirected to charity.
        """)
    with c2:
        st.subheader("🏢 Conventional Debt Operations")
        st.markdown("""
        * **Lender-Debtor Setup:** Pure liquidity is leased; risk transfers completely to the customer once funds clear.
        * **Compounding Interest:** Delinquencies generate penalty interest added directly to total debt.
        * **Asset Sale Disconnect:** Bank functions solely as a financial sponsor rather than a vendor or co-owner.
        """)