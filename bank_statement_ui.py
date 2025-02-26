"""
Bank Statement Analyzer UI Integration
This module integrates the bank statement analyzer with the tax assistant UI.
"""

import streamlit as st
import pandas as pd
import os
import tempfile
from bank_statement_analyzer import BankStatementAnalyzer

def bank_statement_analysis_ui():
    """Display the bank statement analysis UI in Streamlit"""
    st.header("Bank Statement Analysis for Tax Deductions")
    st.write("""
    Upload your bank statement to identify potential tax deductions. 
    This feature helps analyze your expenses and identify transactions that may qualify for tax deductions.
    """)
    
    # Initialize bank statement analyzer
    if 'bank_analyzer' not in st.session_state:
        st.session_state.bank_analyzer = BankStatementAnalyzer()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload bank statement (CSV, Excel format)", 
                                     type=["csv", "xlsx", "xls"])
    
    if uploaded_file:
        try:
            # Save uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Load the bank statement
            df = st.session_state.bank_analyzer.load_statement(tmp_path)
            
            # Remove the temporary file
            os.unlink(tmp_path)
            
            # Display basic info
            st.subheader("Statement Overview")
            st.write(f"Total Transactions: {len(df)}")
            st.write(f"Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
            st.write(f"Total Debits (Expenses): {len(df[df['is_debit']])} transactions")
            
            # Display sample of data
            st.subheader("Sample Transactions")
            st.dataframe(df.head(5))
            
            # Analyze button
            if st.button("Analyze for Tax Deductions"):
                with st.spinner("Analyzing bank statement..."):
                    analysis_results = st.session_state.bank_analyzer.analyze_transactions(df)
                
                # Save results to session state
                st.session_state.analysis_results = analysis_results
                
                # Display results
                display_analysis_results(analysis_results)
        
        except Exception as e:
            st.error(f"Error processing bank statement: {str(e)}")
    
    # Display previous analysis results if available
    if 'analysis_results' in st.session_state and not uploaded_file:
        display_analysis_results(st.session_state.analysis_results)

def display_analysis_results(results):
    """Display analysis results in a user-friendly format"""
    st.subheader("Analysis Results")
    
    # Display summary
    st.markdown("### Summary")
    st.text(results["summary"])
    
    # Display deductions by category
    st.markdown("### Potential Deductions by Category")
    
    categories_df = pd.DataFrame({
        "Category": list(results["total_by_category"].keys()),
        "Amount": list(results["total_by_category"].values())
    })
    categories_df = categories_df[categories_df["Amount"] > 0].sort_values("Amount", ascending=False)
    
    st.bar_chart(categories_df.set_index("Category"))
    
    for category, transactions in results["identified_deductions"].items():
        if not transactions:
            continue
        
        with st.expander(f"{category} - ₹{results['total_by_category'][category]:,.2f}"):
            # Create a DataFrame for display
            tx_df = pd.DataFrame(transactions)
            if not tx_df.empty:
                tx_df = tx_df[["date", "description", "amount"]]
                st.dataframe(tx_df)
    
    # Option to generate detailed report
    if st.button("Generate Detailed Deduction Report"):
        report = st.session_state.bank_analyzer.generate_deduction_report()
        st.download_button(
            label="Download Deduction Report",
            data=report,
            file_name="tax_deduction_report.txt",
            mime="text/plain"
        )
        st.text_area("Deduction Report", report, height=400)