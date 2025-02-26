import os
import json
from datetime import datetime
import google.generativeai as genai
from tax_rules import IndianTaxRules

class IndianTaxAssistant:
    def __init__(self, api_key):
        self.api_key = api_key
        self.setup_gemini()
        self._user_data = {}

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, value):
        self._user_data = value
        
    def setup_gemini(self):
        """Initialize the Gemini API with the provided key"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("Gemini API initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini API: {str(e)}")
            self.model = None

    def ask_tax_question(self, question):
        """Use Gemini API to answer tax-related questions"""
        if not self.model:
            return "Gemini API is not initialized properly. Please check your API key."

        prompt = f"""
        You are an expert on Indian tax laws, specifically the new tax regime for FY 2024-25.
        Answer the following question concisely and accurately:
        {question}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
    def collect_user_data(self, ui=None):
        """Collect basic user information and income details with optional UI"""
        if ui is None:
            from tax_assistant_ui import TaxAssistantUI
            ui = TaxAssistantUI()
        
        ui.print_header()
        ui.print_section_header("PERSONAL INFORMATION")
        
        self.user_data["personal"] = {
            "name": ui.get_input("Full Name: "),
            "pan": ui.get_pan_input("PAN Number: "),
            "dob": ui.get_date_input("Date of Birth (DD/MM/YYYY): "),
            "gender": ui.get_input("Gender (M/F/O): "),
            "address": ui.get_input("Address: "),
            "mobile": ui.get_mobile_input("Mobile Number: "),
            "email": ui.get_email_input("Email Address: ")
        }
        
        self.user_data["income"] = {}
        
        # Salary Income
        ui.print_section_header("SALARY INCOME")
        has_salary = ui.get_yes_no_input("Do you have salary income?")
        if has_salary:
            self.user_data["income"]["salary"] = {
                "basic_salary": ui.get_numeric_input("Basic Salary: ₹", 0),
                "hra_received": ui.get_numeric_input("HRA Received: ₹", 0),
                "special_allowance": ui.get_numeric_input("Special Allowance: ₹", 0),
                "transport_allowance": ui.get_numeric_input("Transport Allowance: ₹", 0),
                "medical_allowance": ui.get_numeric_input("Medical Allowance: ₹", 0),
                "other_allowances": ui.get_numeric_input("Other Allowances: ₹", 0),
                "professional_tax": ui.get_numeric_input("Professional Tax Paid: ₹", 0)
            }
        else:
            self.user_data["income"]["salary"] = {"total": 0}
            
        # Business Income
        ui.print_section_header("BUSINESS INCOME")
        has_business = ui.get_yes_no_input("Do you have business income?")
        if has_business:
            self.user_data["income"]["business"] = {
                "gross_receipts": ui.get_numeric_input("Gross Receipts/Turnover: ₹", 0),
                "expenses": ui.get_numeric_input("Total Expenses: ₹", 0),
                "depreciation": ui.get_numeric_input("Depreciation: ₹", 0)
            }
        else:
            self.user_data["income"]["business"] = {"total": 0}
            
        # Capital Gains
        ui.print_section_header("CAPITAL GAINS")
        has_capital_gains = ui.get_yes_no_input("Do you have capital gains?")
        if has_capital_gains:
            self.user_data["income"]["capital_gains"] = {
                "short_term": ui.get_numeric_input("Short-term Capital Gains: ₹", 0),
                "long_term": ui.get_numeric_input("Long-term Capital Gains: ₹", 0)
            }
        else:
            self.user_data["income"]["capital_gains"] = {"short_term": 0, "long_term": 0}
        
        # Other Income
        ui.print_section_header("OTHER INCOME")
        has_other_income = ui.get_yes_no_input("Do you have other income?")
        if has_other_income:
            self.user_data["income"]["other"] = {
                "interest": ui.get_numeric_input("Interest Income: ₹", 0),
                "rental": ui.get_numeric_input("Rental Income: ₹", 0),
                "dividends": ui.get_numeric_input("Dividend Income: ₹", 0),
                "other": ui.get_numeric_input("Any Other Income: ₹", 0)
            }
        else:
            self.user_data["income"]["other"] = {"total": 0}
            
        self.save_user_data()
        print("\nUser data collected and saved successfully!")

        input("\nPress Enter to continue...")
        
    def save_user_data(self):
        """Save user data to a JSON file"""
        if not self.user_data or "personal" not in self.user_data or "pan" not in self.user_data["personal"]:
            print("No valid user data to save")
            return False
            
        filename = f"tax_data_{self.user_data['personal']['pan']}.json"
        try:
            with open(filename, 'w') as file:
                json.dump(self.user_data, file, indent=4)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False
        
    def load_user_data(self, pan_number):
        """Load user data from a JSON file"""
        filename = f"tax_data_{pan_number}.json"
        try:
            with open(filename, 'r') as file:
                self.user_data = json.load(file)
            print(f"Data loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"No data found for PAN {pan_number}")
            return False
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
            
    def calculate_total_income(self):
        """Calculate total income from all sources using the IndianTaxRules class"""
        if not self.user_data or "income" not in self.user_data:
            print("No valid income data to calculate")
            return 0
            
        total_income = 0
        
        # Salary Income
        if isinstance(self.user_data["income"].get("salary", {}), dict) and "total" not in self.user_data["income"]["salary"]:
            salary_income = (
                self.user_data["income"]["salary"].get("basic_salary", 0) +
                self.user_data["income"]["salary"].get("hra_received", 0) +
                self.user_data["income"]["salary"].get("special_allowance", 0) +
                self.user_data["income"]["salary"].get("transport_allowance", 0) +
                self.user_data["income"]["salary"].get("medical_allowance", 0) +
                self.user_data["income"]["salary"].get("other_allowances", 0) -
                self.user_data["income"]["salary"].get("professional_tax", 0)
            )
            self.tax_calculation["salary_income"] = salary_income
            total_income += salary_income
        elif isinstance(self.user_data["income"].get("salary", {}), dict) and "total" in self.user_data["income"]["salary"]:
            total_income += self.user_data["income"]["salary"].get("total", 0)
            self.tax_calculation["salary_income"] = self.user_data["income"]["salary"].get("total", 0)
            
        # Business Income
        if isinstance(self.user_data["income"].get("business", {}), dict) and "total" not in self.user_data["income"]["business"]:
            business_income = (
                self.user_data["income"]["business"].get("gross_receipts", 0) -
                self.user_data["income"]["business"].get("expenses", 0) -
                self.user_data["income"]["business"].get("depreciation", 0)
            )
            self.tax_calculation["business_income"] = business_income
            total_income += business_income
        elif isinstance(self.user_data["income"].get("business", {}), dict) and "total" in self.user_data["income"]["business"]:
            total_income += self.user_data["income"]["business"].get("total", 0)
            self.tax_calculation["business_income"] = self.user_data["income"]["business"].get("total", 0)
            
        # Capital Gains
        if isinstance(self.user_data["income"].get("capital_gains", {}), dict):
            capital_gains = (
                self.user_data["income"]["capital_gains"].get("short_term", 0) +
                self.user_data["income"]["capital_gains"].get("long_term", 0)
            )
            self.tax_calculation["capital_gains"] = capital_gains
            total_income += capital_gains
        
        # Other Income
        if isinstance(self.user_data["income"].get("other", {}), dict) and "total" not in self.user_data["income"]["other"]:
            other_income = (
                self.user_data["income"]["other"].get("interest", 0) +
                self.user_data["income"]["other"].get("rental", 0) +
                self.user_data["income"]["other"].get("dividends", 0) +
                self.user_data["income"]["other"].get("other", 0)
            )
            self.tax_calculation["other_income"] = other_income
            total_income += other_income
        elif isinstance(self.user_data["income"].get("other", {}), dict) and "total" in self.user_data["income"]["other"]:
            total_income += self.user_data["income"]["other"].get("total", 0)
            self.tax_calculation["other_income"] = self.user_data["income"]["other"].get("total", 0)
            
        # Standard Deduction (only for salaried individuals)
        standard_deduction = IndianTaxRules.get_standard_deduction() if self.tax_calculation.get("salary_income", 0) > 0 else 0
        self.tax_calculation["standard_deduction"] = standard_deduction
        total_income -= standard_deduction
        
        self.tax_calculation["total_income"] = max(0, total_income)
        return self.tax_calculation["total_income"]
    
    def calculate_tax(self):
        """Calculate tax based on the new tax regime using IndianTaxRules"""
        self.tax_calculation = {}

        # First calculate total income
        total_income = self.calculate_total_income()
        print(f"\nTotal Income: ₹{total_income:,.2f}")
        
        # Use the tax rules class for calculations
        tax_before_rebate = IndianTaxRules.calculate_tax(total_income)
        self.tax_calculation["tax_before_rebate"] = tax_before_rebate
        
        # Calculate rebate u/s 87A
        rebate = IndianTaxRules.calculate_rebate(total_income, tax_before_rebate)
        self.tax_calculation["rebate"] = rebate
        
        # Tax after rebate
        tax_after_rebate = max(0, tax_before_rebate - rebate)
        self.tax_calculation["tax_after_rebate"] = tax_after_rebate
        
        # Health and Education Cess @ 4%
        cess = IndianTaxRules.calculate_cess(tax_after_rebate)
        self.tax_calculation["cess"] = cess
        
        # Total tax liability
        total_tax = tax_after_rebate + cess
        self.tax_calculation["total_tax"] = total_tax
        
        # Calculate advance tax schedule if applicable
        if total_tax >= 10000:
            self.calculate_advance_tax()
        
        return self.tax_calculation
    
    def calculate_advance_tax(self):
        """Calculate advance tax schedule if total tax liability >= ₹10,000"""
        total_tax = self.tax_calculation.get("total_tax", 0)
        if total_tax < 10000:
            return
            
        advance_tax_deadlines = IndianTaxRules.get_advance_tax_deadlines()
        advance_tax_schedule = []
        
        for deadline in advance_tax_deadlines:
            cumulative_amount = total_tax * deadline["cumulative_percent"] / 100
            if len(advance_tax_schedule) > 0:
                installment_amount = cumulative_amount - advance_tax_schedule[-1]["cumulative_amount"]
            else:
                installment_amount = cumulative_amount
                
            advance_tax_schedule.append({
                "date": deadline["date"],
                "percentage": deadline["cumulative_percent"],
                "installment_amount": installment_amount,
                "cumulative_amount": cumulative_amount
            })
            
        self.tax_calculation["advance_tax_schedule"] = advance_tax_schedule
    
    def generate_tax_report(self):
        """Generate a detailed tax report"""
        if not self.tax_calculation:
            self.calculate_tax()
            
        # Get age for determining if senior citizen
        try:
            dob = datetime.strptime(self.user_data["personal"]["dob"], "%d/%m/%Y")
            age = datetime.now().year - dob.year
        except:
            age = 30  # Default age if format is incorrect
            
        report = f"""
=======================================
INDIAN TAX CALCULATION REPORT (FY 2024-25)
NEW TAX REGIME
=======================================

PERSONAL DETAILS:
Name: {self.user_data['personal'].get('name', 'N/A')}
PAN: {self.user_data['personal'].get('pan', 'N/A')}
Mobile: {self.user_data['personal'].get('mobile', 'N/A')}
Email: {self.user_data['personal'].get('email', 'N/A')}
Age: {age} years

INCOME DETAILS:
Salary Income: ₹{self.tax_calculation.get('salary_income', 0):,.2f}
Business Income: ₹{self.tax_calculation.get('business_income', 0):,.2f}
Capital Gains: ₹{self.tax_calculation.get('capital_gains', 0):,.2f}
Other Income: ₹{self.tax_calculation.get('other_income', 0):,.2f}
Standard Deduction: ₹{self.tax_calculation.get('standard_deduction', 0):,.2f}

TOTAL TAXABLE INCOME: ₹{self.tax_calculation.get('total_income', 0):,.2f}

TAX CALCULATION:
Tax Before Rebate: ₹{self.tax_calculation.get('tax_before_rebate', 0):,.2f}
Rebate u/s 87A: ₹{self.tax_calculation.get('rebate', 0):,.2f}
Tax After Rebate: ₹{self.tax_calculation.get('tax_after_rebate', 0):,.2f}
Health and Education Cess (4%): ₹{self.tax_calculation.get('cess', 0):,.2f}

TOTAL TAX LIABILITY: ₹{self.tax_calculation.get('total_tax', 0):,.2f}
"""

        # Add advance tax schedule if applicable
        if "advance_tax_schedule" in self.tax_calculation:
            report += "\nADVANCE TAX SCHEDULE:"
            for installment in self.tax_calculation["advance_tax_schedule"]:
                report += f"\n{installment['date']} - ₹{installment['installment_amount']:,.2f} ({installment['percentage']}% cumulative)"
        
        report += f"""

IMPORTANT NOTES:
1. This calculation is based on the New Tax Regime for FY 2024-25.
2. Most deductions like 80C, 80D, HRA exemption are not available in this regime.
3. Standard Deduction of ₹50,000 is available for salaried individuals.
4. Professional Tax deduction is allowed under section 16(iii).
5. Income up to ₹7,00,000 is effectively tax-free due to rebate u/s 87A.

=======================================
This is a computer-generated report and does not require a signature.
Report generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
=======================================
"""
        # Save the report to a file
        filename = f"tax_report_{self.user_data['personal'].get('pan', 'unknown')}.txt"
        try:
            with open(filename, 'w') as file:
                file.write(report)
            print(f"Tax report saved to {filename}")
        except Exception as e:
            print(f"Error saving tax report: {str(e)}")
        
        return report
    
    def ask_tax_question(self, question):
        """Use Gemini API to answer tax-related questions about Indian taxation"""
        if self.model is None:
            return "Gemini API is not initialized properly. Please check your API key."
            
        # Prompt engineering for tax-specific responses
        prompt = f"""
        You are an expert on Indian tax laws, specifically the new tax regime for the financial year 2024-25.
        Please answer the following question about Indian taxation:
        
        {question}
        
        Provide a concise, accurate response based on the latest Indian tax laws under the new regime.
        Include relevant section numbers and citations where appropriate.
        Focus on the new tax regime introduced in Budget 2023 and continued in 2024.
        
        Key points about the new tax regime to consider:
        1. The new regime is the default regime from FY 2023-24 onwards.
        2. It offers lower tax rates but removes most deductions and exemptions.
        3. Income up to ₹3 lakh is exempt from tax.
        4. Income between ₹3-6 lakh is taxed at 5%.
        5. Income between ₹6-9 lakh is taxed at 10%.
        6. Income between ₹9-12 lakh is taxed at 15%.
        7. Income between ₹12-15 lakh is taxed at 20%.
        8. Income above ₹15 lakh is taxed at 30%.
        9. A rebate u/s 87A makes income up to ₹7 lakh effectively tax-free.
        10. Standard deduction of ₹50,000 is available for salaried individuals.
        11. Professional tax deduction is allowed.
        12. Most other deductions like 80C, 80D, HRA, home loan interest are not available.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Sorry, I couldn't process your question due to an error: {str(e)}"
            
    def compare_tax_regimes(self):
        """Compare tax liability between old and new regimes"""
        
        comparison = {
            "new_regime": self.tax_calculation.get("total_tax", 0),
            "old_regime_estimated": 0,  # Would need to implement old regime calculation
            "difference": 0,
            "recommendation": "The new tax regime is generally beneficial if you don't claim many deductions like 80C, 80D, home loan interest, etc."
        }
        
        return comparison