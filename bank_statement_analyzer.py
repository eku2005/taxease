"""
Bank Statement Analyzer Module - Process and analyze bank statements for tax deductions
"""

import pandas as pd
import re
from datetime import datetime
import os

class BankStatementAnalyzer:
    def __init__(self):
        # Dictionary of deduction categories and associated keywords
        self.deduction_categories = {
            "Medical": ["hospital", "clinic", "doctor", "pharmacy", "medical", "health", "medicine", "healthcare", "dental"],
            "Education": ["school", "college", "university", "tuition", "education", "course", "training", "books", "stationery"],
            "Housing": ["rent", "housing", "accommodation", "property tax", "maintenance", "repair", "home loan", "mortgage"],
            "Insurance": ["insurance", "premium", "policy", "life", "health", "medical insurance", "vehicle insurance"],
            "Investments": ["mutual fund", "fixed deposit", "FD", "PPF", "NPS", "ELSS", "shares", "stocks", "investment"],
            "Charity": ["donation", "charitable", "charity", "relief fund", "donations", "ngo"],
            "Business Expenses": ["office", "supplies", "utilities", "internet", "phone", "mobile", "broadband", "business", "professional"]
        }
        
        # Deduction scheme mapping
        self.deduction_schemes = {
            "Medical": ["80D", "80DD", "80DDB", "80U"],
            "Education": ["80E"],
            "Housing": ["80EE", "80EEA", "80G", "24(b)"],
            "Insurance": ["80C", "80D"],
            "Investments": ["80C", "80CCC", "80CCD"],
            "Charity": ["80G"],
            "Business Expenses": ["Business Income Deductions"]
        }
        
        # Annual deduction limits
        self.deduction_limits = {
            "80C": 150000,  # ₹1.5 lakh limit
            "80D": 100000,  # ₹1 lakh (senior citizens)
            "80E": None,    # No limit for education loan interest
            "80G": None,    # Depends on the organization
            "24(b)": 200000 # ₹2 lakh for home loan interest
        }
        
        # Keywords to exclude from deduction analysis (common irrelevant transactions)
        self.exclude_keywords = ["salary", "income", "dividend", "interest received", "cash deposit", "atm", "transfer"] 
        
        # Results of the analysis
        self.analysis_results = {
            "identified_deductions": {},
            "total_by_category": {},
            "potential_savings": 0,
            "summary": "",
            "uncertain_transactions": []
        }
    
    def load_statement(self, file_path):
        """
        Load bank statement from various file formats
        Supports CSV, Excel (.xlsx, .xls), OFX/QFX
        Returns DataFrame with standardized columns
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path, skiprows=self._find_header_row(file_path, ','))
            elif file_ext in ['.xlsx', '.xls']:
                # Try to find where the actual table starts by looking for header row
                header_row = self._find_header_row(file_path)
                df = pd.read_excel(file_path, skiprows=header_row)
            elif file_ext in ['.ofx', '.qfx']:
                # For OFX files, would need specialized library like 'ofxparse'
                # This is a placeholder implementation
                raise NotImplementedError("OFX/QFX format support not implemented")
            elif file_ext == '.pdf':
                # PDF parsing would require additional libraries like 'tabula-py' or 'pdfplumber'
                raise NotImplementedError("PDF format support not implemented")
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            return self._standardize_dataframe(df)
            
        except Exception as e:
            raise Exception(f"Error loading bank statement: {str(e)}")
    
    def _find_header_row(self, file_path, delimiter=None):
     """
    Find the row index where the table header is located"""
     try:
            if file_path.endswith(('.xlsx', '.xls')):
                xl = pd.ExcelFile(file_path)
            # Read first 20 rows to find headers
                sample = pd.read_excel(xl, sheet_name=0, nrows=20)
            else:
            # For CSV files
                sample = pd.read_csv(file_path, nrows=20, delimiter=delimiter)

        # Look for rows that contain our expected headers
            expected_headers = ['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Withdrawal Amt.', 'Deposit Amt.', 'Closing Balance']
            for i in range(len(sample)):
                row = sample.iloc[i].astype(str)
                if all(header in row.values for header in expected_headers):
                    return i

        # If we can't find it
            return 0
     except Exception as e:
            print(f"Error finding header row: {str(e)}")
            return 0  

    
    def _standardize_dataframe(self, df):
        """
        Standardize the DataFrame columns to a common format
        Modified to handle the specific Excel format with columns:
        Date, Narration, Chq./Ref.No., Value Dt, Withdrawal Amt., Deposit Amt., Closing Balance
        """
        # Create a new standardized DataFrame
        standardized_df = pd.DataFrame()
        
        # Make column names case-insensitive
        df.columns = [col.strip() for col in df.columns]
        column_mapping = {col.lower(): col for col in df.columns}
        
        # Find date column
        date_col = None
        date_patterns = ["date", "txn date", "transaction date", "value dt"]
        for pattern in date_patterns:
            if pattern in column_mapping:
                date_col = column_mapping[pattern]
                break
        
        if date_col:
            try:
                # Try with dayfirst=True for DD/MM/YYYY format
                standardized_df["date"] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
            except:
                standardized_df["date"] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Find description/narration column
        desc_col = None
        desc_patterns = ["narration", "description", "particulars", "details"]
        for pattern in desc_patterns:
            if pattern in column_mapping:
                desc_col = column_mapping[pattern]
                break
        
        if desc_col:
            standardized_df["description"] = df[desc_col].astype(str)
        else:
            # Use first text column as fallback
            for col in df.columns:
                if df[col].dtype == object and col != date_col:
                    standardized_df["description"] = df[col].astype(str)
                    break
        
        # Look for withdrawal/deposit columns
        withdrawal_col = None
        deposit_col = None
        
        withdrawal_patterns = ["withdrawal amt.", "withdrawal", "debit", "dr", "debit amount"]
        for pattern in withdrawal_patterns:
            if pattern in column_mapping:
                withdrawal_col = column_mapping[pattern]
                break
                
        deposit_patterns = ["deposit amt.", "deposit", "credit", "cr", "credit amount"]
        for pattern in deposit_patterns:
            if pattern in column_mapping:
                deposit_col = column_mapping[pattern]
                break
        
        # Process withdrawal and deposit amounts
        if withdrawal_col and deposit_col:
            # Convert to numeric values
            withdrawal_values = pd.to_numeric(df[withdrawal_col], errors='coerce').fillna(0)
            deposit_values = pd.to_numeric(df[deposit_col], errors='coerce').fillna(0)
            
            # A transaction is a debit if withdrawal amount is non-zero
            standardized_df["is_debit"] = withdrawal_values > 0
            
            # Set the amount (either withdrawal or deposit)
            standardized_df["amount"] = withdrawal_values.where(withdrawal_values > 0, deposit_values)
        else:
            # Fallback if we can't find proper columns
            amount_col = next((col for col in df.columns if 'amount' in col.lower()), None)
            if amount_col:
                standardized_df["amount"] = pd.to_numeric(df[amount_col], errors='coerce').abs()
                
                # Try to determine debit/credit from type indicators
                indicator_col = next((col for col in df.columns if any(x in col.lower() for x in ['type', 'indicator', 'dr/cr'])), None)
                if indicator_col:
                    standardized_df["is_debit"] = df[indicator_col].astype(str).str.lower().apply(
                        lambda x: 'dr' in x or 'debit' in x or 'withdrawal' in x or '-' in x
                    )
                else:
                    # Default: everything is a debit
                    standardized_df["is_debit"] = True
            else:
                # Create empty columns if we can't find anything
                standardized_df["amount"] = 0
                standardized_df["is_debit"] = True
        
        # Add reference number if available
        ref_patterns = ["chq./ref.no.", "ref no", "reference", "cheque no"]
        for pattern in ref_patterns:
            if pattern in column_mapping:
                standardized_df["reference"] = df[column_mapping[pattern]]
                break
        
        # Fill NA values and ensure proper types
        standardized_df["amount"] = standardized_df["amount"].fillna(0)
        standardized_df["is_debit"] = standardized_df["is_debit"].fillna(True)
        standardized_df["description"] = standardized_df["description"].fillna("")
        
        # Drop rows with missing dates
        standardized_df = standardized_df.dropna(subset=["date"])
        
        return standardized_df
    
    def analyze_transactions(self, df):
        """
        Analyze transactions for potential tax deductions
        """
        # Reset previous analysis results
        self.analysis_results = {
            "identified_deductions": {},
            "total_by_category": {},
            "potential_savings": 0,
            "summary": "",
            "uncertain_transactions": []
        }
        
        # Filter for debit transactions only (expenses)
        debit_transactions = df[df["is_debit"]]
        
        # Initialize category totals
        for category in self.deduction_categories:
            self.analysis_results["total_by_category"][category] = 0
            self.analysis_results["identified_deductions"][category] = []
        
        # Analyze each transaction
        for _, transaction in debit_transactions.iterrows():
            desc = str(transaction["description"]).lower()
            amount = float(transaction["amount"])
            date = transaction["date"]
            
            # Skip if contains exclude keywords
            if any(keyword in desc for keyword in self.exclude_keywords):
                continue
            
            # Check for matches in deduction categories
            matched = False
            for category, keywords in self.deduction_categories.items():
                if any(keyword.lower() in desc for keyword in keywords):
                    self.analysis_results["total_by_category"][category] += amount
                    self.analysis_results["identified_deductions"][category].append({
                        "date": date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date),
                        "description": transaction["description"],
                        "amount": amount,
                        "matched_keywords": [kw for kw in keywords if kw.lower() in desc]
                    })
                    matched = True
                    break
            
            # Add to uncertain transactions if no clear match and amount is significant
            if not matched and amount > 1000:
                self.analysis_results["uncertain_transactions"].append({
                    "date": date.strftime("%Y-%m-%d") if hasattr(date, "strftime") else str(date),
                    "description": transaction["description"],
                    "amount": amount
                })
        
        # Calculate potential tax savings based on identified deductions
        self._calculate_potential_savings()
        
        # Generate summary
        self._generate_summary()
        
        return self.analysis_results
    
    def _calculate_potential_savings(self):
        """
        Calculate potential tax savings based on identified deductions
        This is a simplified calculation and should not be considered tax advice
        """
        # Simplified tax rate assumption (30% for highest bracket)
        tax_rate = 0.30
        
        # Calculate for each deduction scheme
        total_savings = 0
        for category, schemes in self.deduction_schemes.items():
            category_amount = self.analysis_results["total_by_category"][category]
            
            if category_amount <= 0:
                continue
                
            # Apply relevant limits
            applicable_amount = 0
            for scheme in schemes:
                limit = self.deduction_limits.get(scheme, None)
                
                if limit is None:
                    # No limit or special calculation needed
                    applicable_amount = category_amount
                else:
                    # Apply the limit
                    applicable_amount = min(category_amount, limit)
                    
                # Calculate tax savings
                savings = applicable_amount * tax_rate
                total_savings += savings
                
                # don't double count
                break
        
        self.analysis_results["potential_savings"] = total_savings
    
    def _generate_summary(self):
        """Generate a summary of the analysis"""
        summary = "Bank Statement Analysis Summary\n"
        summary += "================================\n\n"
        
        summary += "Potentially Deductible Expenses by Category:\n"
        for category, total in self.analysis_results["total_by_category"].items():
            if total > 0:
                applicable_schemes = ", ".join(self.deduction_schemes[category])
                summary += f"- {category}: ₹{total:,.2f} (Applicable Sections: {applicable_schemes})\n"
        
        summary += f"\nEstimated Potential Tax Savings: ₹{self.analysis_results['potential_savings']:,.2f}\n"
        
        summary += "\nImportant Notes:\n"
        summary += "1. This analysis is based on keyword matching and may not be 100% accurate\n"
        summary += "2. Not all identified expenses may qualify for tax deductions\n"
        summary += "3. Some deductions are only available in the old tax regime\n"
        summary += "4. Please consult a tax professional for accurate advice\n"
        
        self.analysis_results["summary"] = summary
        
    def generate_deduction_report(self):
        """Generate a detailed report of potential deductions"""
        if not self.analysis_results["identified_deductions"]:
            return "No analysis results available. Please analyze a bank statement first."
            
        report = "POTENTIAL TAX DEDUCTION REPORT\n"
        report += "==============================\n\n"
        
        # Add summary section
        report += self.analysis_results["summary"]
        report += "\n\n"
        
        # Detailed breakdown by category
        report += "DETAILED EXPENSE BREAKDOWN\n"
        report += "==========================\n\n"
        
        for category, transactions in self.analysis_results["identified_deductions"].items():
            if not transactions:
                continue
                
            report += f"{category} Expenses (Applicable Sections: {', '.join(self.deduction_schemes[category])})\n"
            report += "-" * 80 + "\n"
            
            # Sort by date
            sorted_transactions = sorted(transactions, key=lambda x: x["date"])
            
            for idx, tx in enumerate(sorted_transactions, 1):
                report += f"{idx}. Date: {tx['date']}\n"
                report += f"   Description: {tx['description']}\n"
                report += f"   Amount: ₹{tx['amount']:,.2f}\n"
                report += f"   Matched Keywords: {', '.join(tx['matched_keywords'])}\n\n"
            
            category_total = sum(tx["amount"] for tx in transactions)
            report += f"Total {category} Expenses: ₹{category_total:,.2f}\n\n"
        
        # Uncertain transactions
        if self.analysis_results["uncertain_transactions"]:
            report += "UNCERTAIN TRANSACTIONS\n"
            report += "=====================\n\n"
            report += "The following transactions could not be categorized but may be eligible for deductions:\n\n"
            
            sorted_uncertain = sorted(self.analysis_results["uncertain_transactions"], key=lambda x: x["date"])
            
            for idx, tx in enumerate(sorted_uncertain, 1):
                report += f"{idx}. Date: {tx['date']}\n"
                report += f"   Description: {tx['description']}\n"
                report += f"   Amount: ₹{tx['amount']:,.2f}\n\n"
        
        report += "DISCLAIMER\n"
        report += "==========\n"
        report += "This report is generated through automated analysis and keyword matching. "
        report += "Not all identified expenses may qualify for tax deductions. "
        report += "Most deductions are only available under the old tax regime. "
        report += "Please consult a tax professional for accurate tax advice.\n"
        
        return report