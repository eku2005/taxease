import streamlit as st

from tax_assistant_base import IndianTaxAssistant
from tax_rules import TAX_FAQ, IndianTaxRules
from bank_statement_ui import bank_statement_analysis_ui
import pandas as pd
from datetime import datetime

# Add the missing method to IndianTaxRules
def initialize_tax_rules():
    """Add any missing methods to IndianTaxRules class if they don't exist"""
    if not hasattr(IndianTaxRules, 'get_cess_rate'):
        setattr(IndianTaxRules, 'get_cess_rate', lambda: 0.04)

def initialize_tax_assistant():
    """Initialize the tax assistant and persist it in session state."""
    # Initialize tax rules first
    initialize_tax_rules()
    if 'tax_assistant' not in st.session_state:
        # Initialize IndianTaxAssistant without requiring an API key
        tax_assistant = IndianTaxAssistant(api_key=None)
        st.session_state.tax_assistant = tax_assistant
    return st.session_state.tax_assistant

def main():
    st.set_page_config(page_title="TaxEase - Smart Indian Tax Assistant", layout="wide", initial_sidebar_state="expanded")
    
    st.title("TaxEase - Your Financial Companion for FY 2024-25")
    st.write("Navigate the complexities of taxation with confidence under the new regime.")
    
    # Initialize tax assistant
    tax_assistant = initialize_tax_assistant()
    
    # Sidebar menu with refined options
    menu_choice = st.sidebar.radio(
        "Navigation Panel",
        [
            "Enter Your Tax Details",
            "Retrieve Saved Information",
            "Calculate Your Tax Liability",
            "Generate Comprehensive Report",
            "Analyze Bank Statements",
            "Tax FAQ & Knowledge Base",
            "Consult TaxEase"
        ]
    )
    
    if menu_choice == "Enter Your Tax Details":
        collect_user_data(tax_assistant)
    elif menu_choice == "Retrieve Saved Information":
        load_user_data(tax_assistant)
    elif menu_choice == "Calculate Your Tax Liability":
        calculate_tax(tax_assistant)
    elif menu_choice == "Generate Comprehensive Report":
        generate_tax_report(tax_assistant)
    elif menu_choice == "Analyze Bank Statements":
        bank_statement_analysis_ui()
    elif menu_choice == "Tax FAQ & Knowledge Base":
        view_tax_faq()
    elif menu_choice == "Consult TaxEase":
        ask_tax_question()

def collect_user_data(tax_assistant):
    st.header("Personal Profile")
    st.write("Let us understand your financial situation to provide tailored tax calculations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name (As per PAN Card)")
        pan = st.text_input("PAN Number (Your Tax Identity)")
        dob = st.date_input("Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.now())
    
    with col2:
        gender = st.selectbox("Gender", ["M", "F", "O"])
        mobile = st.text_input("Mobile Number (For Important Updates)")
        email = st.text_input("Email Address (For Notifications)")
    
    address = st.text_area("Residential Address (Complete)")
    
    st.header("Income Details")
    st.write("Provide accurate information for precise tax calculations.")
    
    salary = st.number_input("Salary Income (Annual)", min_value=0.0)
    business = st.number_input("Business Income (Net Profit)", min_value=0.0)
    capital_gains = st.number_input("Capital Gains (Realized Profits)", min_value=0.0)
    other_income = st.number_input("Other Income (Interest, Dividends, etc.)", min_value=0.0)
    
    if st.button("Save Information"):
        # Save user data to session state and the assistant
        tax_assistant.user_data = {
            "personal": {
                "name": name,
                "pan": pan,
                "dob": dob.strftime("%d/%m/%Y"),
                "gender": gender,
                "mobile": mobile,
                "email": email,
                "address": address
            },
            "income": {
                "salary": {"total": salary},
                "business": {"total": business},
                "capital_gains": {"short_term": capital_gains, "long_term": 0},
                "other": {"total": other_income}
            }
        }
        
        # Persist user data in session state
        st.session_state.user_data = tax_assistant.user_data
        tax_assistant.save_user_data()
        st.success("Your information has been saved successfully. You're now ready for tax calculations.")

def ask_tax_question():
    """Allow users to ask a question about taxes."""
    st.header("Consult TaxEase")
    st.write("Have a specific tax question? Our advanced tax intelligence is at your service.")
    
    # Prompt for Gemini API key only in this section
    api_key = st.text_input("Enter your Gemini API key (Required for consultation):", type="password")
    
    if not api_key:
        st.warning("Please enter your Gemini API key to access TaxEase consultation services.")
        return
    
    # Initialize IndianTaxAssistant with the provided API key
    ai_tax_assistant = IndianTaxAssistant(api_key)
    
    question = st.text_input("What would you like to know about Indian taxation?")
    
    if question and st.button("Submit Question"):
        with st.spinner("TaxEase is analyzing your query..."):
            answer = ai_tax_assistant.ask_tax_question(question)
            if answer:
                st.subheader("TaxEase Response:")
                st.write(answer)
            else:
                st.error("We encountered an issue processing your query. Please verify your API setup and try again.")

def load_user_data(tax_assistant):
    """Load existing user data."""
    st.header("Retrieve Your Tax Profile")
    st.write("Access your previously saved tax information for continued analysis.")
    
    pan = st.text_input("Enter your PAN number to retrieve your data:")
    
    if st.button("Retrieve Data"):
        with st.spinner("Searching for your tax profile..."):
            if tax_assistant.load_user_data(pan):
                # Save loaded data to session state
                st.session_state.user_data = tax_assistant.user_data
                st.success(f"Welcome back. We've successfully retrieved your data for PAN {pan}")
                display_user_data(st.session_state.user_data)
            else:
                st.error("We couldn't locate your data. Please verify your PAN number or create a new profile.")

def calculate_tax(tax_assistant):
    """Calculate and display tax details."""
    # Ensure user data exists in session state
    if 'user_data' not in st.session_state or not st.session_state.user_data:
        st.warning("We require your financial information first. Please enter your details or load your existing profile.")
        return
    
    st.header("Tax Calculation Results")
    st.write("Here's a detailed breakdown of your tax liability under the new regime:")
    
    # Sync user data with session state
    tax_assistant.user_data = st.session_state.user_data
    
    with st.spinner("Calculating your tax liability..."):
        result = tax_assistant.calculate_tax()
    
    # Display results in a structured way
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Income Breakdown")
        for key, value in result.items():
            if key.endswith("_income"):
                label = key.replace("_", " ").title()
                value_formatted = f"₹{value:,.2f}"
                st.write(f"{label}: {value_formatted}")
    
    with col2:
        st.subheader("Tax Calculation")
        for key, value in result.items():
            if key in ["tax_before_rebate", "rebate", "tax_after_rebate", "cess", "total_tax"]:
                label = key.replace("_", " ").title()
                value_formatted = f"₹{value:,.2f}"
                st.write(f"{label}: {value_formatted}")
    
    # Add a visual indicator of tax burden
    st.subheader("Tax Burden Analysis")
    total_income = result.get("total_income", 0)
    total_tax = result.get("total_tax", 0)
    if total_income > 0:
        tax_percentage = (total_tax / total_income) * 100
        st.progress(min(tax_percentage / 30, 100))  # Scale to make it visible (max at 30%)
        st.write(f"Your effective tax rate: {tax_percentage:.2f}%")

def generate_tax_report(tax_assistant):
    st.header("Your Comprehensive Tax Report")
    st.write("Obtain a detailed analysis of your tax situation for your records.")
    
    # Ensure user data exists in session state
    if 'user_data' not in st.session_state or not st.session_state.user_data:
        st.warning("We require your financial information first. Please enter your details or load your existing profile.")
        return
    
    # Sync user data with session state
    tax_assistant.user_data = st.session_state.user_data
    
    with st.spinner("Generating your personalized tax report..."):
        report = tax_assistant.generate_tax_report()
    
    # Display and download report
    filename = f"tax_report_{st.session_state.user_data['personal']
