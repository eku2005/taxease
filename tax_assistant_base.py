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
        self.tax_calculation = {}

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, value):
        self._user_data = value

    def setup_gemini(self):
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            print("Gemini API initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini API: {str(e)}")
            self.model = None

    def ask_tax_question(self, question):
        if self.model is None:
            return "Gemini API is not initialized properly. Please check your API key."

        prompt = f"""
        You are an expert on Indian tax laws for FY 2024–25 (new regime).
        Answer the following question clearly and accurately:
        {question}

        Use current slab rates and laws. Mention section numbers if relevant.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def collect_user_data(self, ui=None):
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

        def collect_income(section, fields):
            ui.print_section_header(section.upper())
            has_income = ui.get_yes_no_input(f"Do you have {section.lower()} income?")
            if has_income:
                self.user_data["income"][section] = {
                    field: ui.get_numeric_input(f"{label}: ₹", 0)
                    for field, label in fields.items()
                }
            else:
                self.user_data["income"][section] = {"total": 0}

        collect_income("salary", {
            "basic_salary": "Basic Salary",
            "hra_received": "HRA Received",
            "special_allowance": "Special Allowance",
            "transport_allowance": "Transport Allowance",
            "medical_allowance": "Medical Allowance",
            "other_allowances": "Other Allowances",
            "professional_tax": "Professional Tax Paid"
        })

        collect_income("business", {
            "gross_receipts": "Gross Receipts/Turnover",
            "expenses": "Total Expenses",
            "depreciation": "Depreciation"
        })

        collect_income("capital_gains", {
            "short_term": "Short-term Capital Gains",
            "long_term": "Long-term Capital Gains"
        })

        collect_income("other", {
            "interest": "Interest Income",
            "rental": "Rental Income",
            "dividends": "Dividend Income",
            "other": "Any Other Income"
        })

        self.save_user_data()
        print("\nUser data collected and saved successfully!")
        input("\nPress Enter to continue...")

    def save_user_data(self):
        try:
            filename = f"tax_data_{self.user_data['personal']['pan']}.json"
            with open(filename, 'w') as file:
                json.dump(self.user_data, file, indent=4)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

    def load_user_data(self, pan_number):
        try:
            filename = f"tax_data_{pan_number}.json"
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
        if not self.user_data or "income" not in self.user_data:
            print("No valid income data to calculate")
            return 0

        total = 0
        salary = self.user_data["income"].get("salary", {})
        if "total" not in salary:
            s = (
                salary.get("basic_salary", 0) +
                salary.get("hra_received", 0) +
                salary.get("special_allowance", 0) +
                salary.get("transport_allowance", 0) +
                salary.get("medical_allowance", 0) +
                salary.get("other_allowances", 0) -
                salary.get("professional_tax", 0)
            )
            self.tax_calculation["salary_income"] = s
            total += s
        else:
            s = salary.get("total", 0)
            self.tax_calculation["salary_income"] = s
            total += s

        business = self.user_data["income"].get("business", {})
        if "total" not in business:
            b = (
                business.get("gross_receipts", 0) -
                business.get("expenses", 0) -
                business.get("depreciation", 0)
            )
            self.tax_calculation["business_income"] = b
            total += b
        else:
            b = business.get("total", 0)
            self.tax_calculation["business_income"] = b
            total += b

        cg = self.user_data["income"].get("capital_gains", {})
        c = cg.get("short_term", 0) + cg.get("long_term", 0)
        self.tax_calculation["capital_gains"] = c
        total += c

        other = self.user_data["income"].get("other", {})
        if "total" not in other:
            o = (
                other.get("interest", 0) +
                other.get("rental", 0) +
                other.get("dividends", 0) +
                other.get("other", 0)
            )
            self.tax_calculation["other_income"] = o
            total += o
        else:
            o = other.get("total", 0)
            self.tax_calculation["other_income"] = o
            total += o

        std_ded = IndianTaxRules.get_standard_deduction() if self.tax_calculation.get("salary_income", 0) > 0 else 0
        total -= std_ded
        self.tax_calculation["standard_deduction"] = std_ded
        self.tax_calculation["total_income"] = max(0, total)
        return self.tax_calculation["total_income"]

    def calculate_tax(self):
        total_income = self.calculate_total_income()
        print(f"\nTotal Income: ₹{total_income:,.2f}")

        tax_before_rebate = IndianTaxRules.calculate_tax(total_income)
        rebate = IndianTaxRules.calculate_rebate(total_income, tax_before_rebate)
        tax_after_rebate = max(0, tax_before_rebate - rebate)
        cess = IndianTaxRules.calculate_cess(tax_after_rebate)
        total_tax = tax_after_rebate + cess

        self.tax_calculation.update({
            "tax_before_rebate": tax_before_rebate,
            "rebate": rebate,
            "tax_after_rebate": tax_after_rebate,
            "cess": cess,
            "total_tax": total_tax
        })

        if total_tax >= 10000:
            self.calculate_advance_tax()

        return self.tax_calculation

    def calculate_advance_tax(self):
        total_tax = self.tax_calculation["total_tax"]
        schedule = []
        for d in IndianTaxRules.get_advance_tax_deadlines():
            cum = total_tax * d["cumulative_percent"] / 100
            prev = schedule[-1]["cumulative_amount"] if schedule else 0
            inst = cum - prev
            schedule.append({
                "date": d["date"],
                "percentage": d["cumulative_percent"],
                "installment_amount": inst,
                "cumulative_amount": cum
            })
        self.tax_calculation["advance_tax_schedule"] = schedule

    def generate_tax_report(self):
        if not self.tax_calculation:
            self.calculate_tax()

        try:
            dob = datetime.strptime(self.user_data["personal"]["dob"], "%d/%m/%Y")
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            age = "N/A"

        rpt = f"""
=======================================
INDIAN TAX CALCULATION REPORT (FY 2024–25)
NEW TAX REGIME
=======================================
Name: {self.user_data['personal'].get('name', 'N/A')}
PAN: {self.user_data['personal'].get('pan', 'N/A')}
Age: {age}
Mobile: {self.user_data['personal'].get('mobile', 'N/A')}
Email: {self.user_data['personal'].get('email', 'N/A')}

INCOME DETAILS:
Salary: ₹{self.tax_calculation.get('salary_income', 0):,.2f}
Business: ₹{self.tax_calculation.get('business_income', 0):,.2f}
Capital Gains: ₹{self.tax_calculation.get('capital_gains', 0):,.2f}
Other: ₹{self.tax_calculation.get('other_income', 0):,.2f}
Standard Deduction: ₹{self.tax_calculation.get('standard_deduction', 0):,.2f}

TOTAL TAXABLE INCOME: ₹{self.tax_calculation.get('total_income', 0):,.2f}

TAX:
Before Rebate: ₹{self.tax_calculation.get('tax_before_rebate', 0):,.2f}
Rebate u/s 87A: ₹{self.tax_calculation.get('rebate', 0):,.2f}
After Rebate: ₹{self.tax_calculation.get('tax_after_rebate', 0):,.2f}
Cess (4%): ₹{self.tax_calculation.get('cess', 0):,.2f}
TOTAL TAX PAYABLE: ₹{self.tax_calculation.get('total_tax', 0):,.2f}
"""

        if "advance_tax_schedule" in self.tax_calculation:
            rpt += "\nADVANCE TAX SCHEDULE:"
            for i in self.tax_calculation["advance_tax_schedule"]:
                rpt += f"\n{i['date']} - ₹{i['installment_amount']:,.2f} ({i['percentage']}% cumulative)"

        rpt += f"""

NOTES:
1. Based on New Regime for FY 2024–25.
2. Most exemptions (80C, HRA, 80D) are not applicable.
3. Income up to ₹7L effectively tax-free due to 87A.
4. Report generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
=======================================
"""
        filename = f"tax_report_{self.user_data['personal'].get('pan', 'unknown')}.txt"
        try:
            with open(filename, 'w') as file:
                file.write(rpt)
            print(f"Tax report saved to {filename}")
        except Exception as e:
            print(f"Error saving tax report: {str(e)}")

        return rpt

    def compare_tax_regimes(self):
        return {
            "new_regime": self.tax_calculation.get("total_tax", 0),
            "old_regime_estimated": 0,
            "difference": 0,
            "recommendation": "The new regime is beneficial if you're not claiming many deductions like 80C, 80D, or HRA."
        }
