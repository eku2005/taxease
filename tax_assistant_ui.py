"""
Tax Assistant UI Module - Handles user interface components
"""

import os
import re
import json
from datetime import datetime

class TaxAssistantUI:
    """Class for handling user interface elements of the tax assistant"""

    @staticmethod
    def clear_screen():
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_header():
        """Print the application header"""
        TaxAssistantUI.clear_screen()
        print("=" * 60)
        print(" " * 10 + "INDIAN TAX ASSISTANT (NEW REGIME) 2024-25")
        print("=" * 60)

    @staticmethod
    def print_section_header(title):
        """Print a section header"""
        print("\n--- " + title + " ---")

    @staticmethod
    def get_input(prompt, validation_func=None, error_msg=None):
        """
        Get validated input from the user
        Args:
            prompt: The input prompt to display
            validation_func: A function that returns True if input is valid
            error_msg: Message to display if validation fails
        Returns:
            Validated input
        """
        while True:
            user_input = input(prompt)
            if validation_func is None or validation_func(user_input):
                return user_input
            print(error_msg or "Invalid input. Please try again.")

    @staticmethod
    def get_numeric_input(prompt, min_value=None, max_value=None):
        """Get numeric input within specified range"""
        def validate(value):
            try:
                num = float(value)
                if min_value is not None and num < min_value:
                    return False
                if max_value is not None and num > max_value:
                    return False
                return True
            except ValueError:
                return False

        error_msg = f"Please enter a number"
        if min_value is not None and max_value is not None:
            error_msg += f" between {min_value} and {max_value}"
        elif min_value is not None:
            error_msg += f" greater than or equal to {min_value}"
        elif max_value is not None:
            error_msg += f" less than or equal to {max_value}"

        return float(TaxAssistantUI.get_input(prompt, validate, error_msg))

    @staticmethod
    def get_yes_no_input(prompt):
        """Get a Yes/No input from the user"""
        response = TaxAssistantUI.get_input(
            prompt + " (Y/N): ",
            lambda x: x.upper() in ["Y", "N", "YES", "NO"],
            "Please enter Y or N."
        )
        return response.upper() in ["Y", "YES"]

    @staticmethod
    def get_date_input(prompt):
        """Get a date input in DD/MM/YYYY format"""
        def validate_date(date_str):
            pattern = r"^\d{1,2}/\d{1,2}/\d{4}$"
            if not re.match(pattern, date_str):
                return False
            try:
                datetime.strptime(date_str, "%d/%m/%Y")
                return True
            except ValueError:
                return False

        return TaxAssistantUI.get_input(
            prompt,
            validate_date,
            "Please enter a valid date in DD/MM/YYYY format."
        )

    @staticmethod
    def get_pan_input(prompt):
        """Get a valid PAN input"""
        def validate_pan(pan):
            # PAN format: AAAPL1234C (5 alphabets, 4 numbers, 1 alphabet)
            pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
            return re.match(pattern, pan.upper()) is not None

        return TaxAssistantUI.get_input(
            prompt,
            validate_pan,
            "Please enter a valid 10-character PAN (e.g., AAAPL1234C)."
        ).upper()

    @staticmethod
    def get_mobile_input(prompt):
        """Get a valid mobile number"""
        def validate_mobile(mobile):
            # Indian mobile numbers: 10 digits, starting with 6-9
            pattern = r"^[6-9]\d{9}$"
            return re.match(pattern, mobile) is not None

        return TaxAssistantUI.get_input(
            prompt,
            validate_mobile,
            "Please enter a valid 10-digit Indian mobile number."
        )

    @staticmethod
    def get_email_input(prompt):
        """Get a valid email address"""
        def validate_email(email):
            # Simple email validation
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return re.match(pattern, email) is not None

        return TaxAssistantUI.get_input(
            prompt,
            validate_email,
            "Please enter a valid email address."
        )

    @staticmethod
    def display_menu(title, options):
        """Display a menu with options and get user choice"""
        TaxAssistantUI.print_section_header(title)
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")
        choice = TaxAssistantUI.get_numeric_input(
            "\nEnter your choice (1-" + str(len(options)) + "): ",
            1, len(options)
        )
        return int(choice)

    @staticmethod
    def display_tax_calculation(tax_data):
        """Display tax calculation details in a formatted way"""
        TaxAssistantUI.print_section_header("TAX CALCULATION RESULTS")
        # Format with proper alignment
        print(f"\n{'Income Details':30} {'Amount (₹)'}")
        print("-" * 50)
        print(f"{'Salary Income':30} {tax_data.get('salary_income', 0):,.2f}")
        print(f"{'Business Income':30} {tax_data.get('business_income', 0):,.2f}")
        print(f"{'Capital Gains':30} {tax_data.get('capital_gains', 0):,.2f}")
        print(f"{'Other Income':30} {tax_data.get('other_income', 0):,.2f}")
        print(f"{'Standard Deduction':30} {tax_data.get('standard_deduction', 0):,.2f}")
        print("-" * 50)
        print(f"{'Total Taxable Income':30} {tax_data.get('total_income', 0):,.2f}")
        print("\nTax Calculation:")
        print(f"{'Tax Before Rebate':30} {tax_data.get('tax_before_rebate', 0):,.2f}")
        print(f"{'Rebate u/s 87A':30} {tax_data.get('rebate', 0):,.2f}")
        print(f"{'Tax After Rebate':30} {tax_data.get('tax_after_rebate', 0):,.2f}")
        print(f"{'Health & Education Cess':30} {tax_data.get('cess', 0):,.2f}")
        print("-" * 50)
        print(f"{'Total Tax Liability':30} {tax_data.get('total_tax', 0):,.2f}")

        if 'advance_tax_schedule' in tax_data:
            print("\nAdvance Tax Schedule:")
            for installment in tax_data['advance_tax_schedule']:
                print(f"{installment['date']:15} ₹{installment['installment_amount']:,.2f} "
                      f"({installment['percentage']}% cumulative)")
