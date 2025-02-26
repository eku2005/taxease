"""
Indian Tax Rules Module - New Tax Regime (FY 2024-25)
This module contains the hardcoded tax rules for the Indian new tax regime.
"""

class IndianTaxRules:
    @staticmethod
    def get_tax_slabs():
        """Return the tax slabs for the new tax regime (FY 2024-25)"""
        return [
            {"limit": 300000, "rate": 0.00},
            {"limit": 600000, "rate": 0.05},
            {"limit": 900000, "rate": 0.10},
            {"limit": 1200000, "rate": 0.15},
            {"limit": 1500000, "rate": 0.20},
            {"limit": float('inf'), "rate": 0.30}
        ]

    @staticmethod
    def get_standard_deduction():
        """Return the standard deduction amount for salaried individuals"""
        return 50000

    @staticmethod
    def get_rebate_limit():
        """Return the income limit for rebate under section 87A"""
        return 700000

    @staticmethod
    def get_rebate_amount():
        """Return the maximum rebate amount under section 87A"""
        return 25000

    @staticmethod
    def get_cess_rate():
        """Return the health and education cess rate"""
        return 0.04  # 4% health and education cess
    @staticmethod
    def calculate_tax(total_income):
        """Calculate tax based on the income and slabs"""
        slabs = IndianTaxRules.get_tax_slabs()
        tax = 0
        remaining_income = total_income
        prev_limit = 0
        
        for slab in slabs:
            if remaining_income <= 0:
                break
                
            taxable_in_slab = min(remaining_income, slab["limit"] - prev_limit)
            tax += taxable_in_slab * slab["rate"]
            
            remaining_income -= taxable_in_slab
            prev_limit = slab["limit"]
        
        return tax
    
    @staticmethod
    def calculate_rebate(total_income, tax):
        """Calculate rebate under section 87A if applicable"""
        if total_income <= IndianTaxRules.get_rebate_limit():
            return min(tax, IndianTaxRules.get_rebate_amount())
        return 0
    
    @staticmethod
    def calculate_cess(tax_after_rebate):
        """Calculate health and education cess"""
        return tax_after_rebate * IndianTaxRules.get_cess_rate()
    
    @staticmethod
    def is_eligible_for_new_regime(income_sources):
        """Check if a taxpayer is eligible for the new tax regime"""
        # From FY 2023-24, new tax regime is the default
        # Almost everyone is eligible with some exceptions
        
        # Potential restrictions for specific business incomes
        business_restrictions = [
            "44AD", "44ADA", "44AE", "Presumptive taxation schemes"
        ]
        
        # Most individuals are eligible 
        return True, "You are eligible for the new tax regime"
    
    @staticmethod
    def get_advance_tax_deadlines():
        """Return the advance tax deadlines and percentages"""
        return [
            {"date": "15-Jun-2024", "cumulative_percent": 15},
            {"date": "15-Sep-2024", "cumulative_percent": 45},
            {"date": "15-Dec-2024", "cumulative_percent": 75},
            {"date": "15-Mar-2025", "cumulative_percent": 100}
        ]
    
    @staticmethod
    def get_tax_regime_comparison_factors():
        """Return key points for comparing old vs new regime"""
        return {
            "new_regime_pros": [
                "Lower tax rates for most income brackets",
                "Simpler compliance with fewer deduction calculations",
                "Beneficial for those with limited investments or deductions",
                "Lower rates beneficial for younger taxpayers starting careers",
                "Standard deduction of ₹50,000 still available"
            ],
            "new_regime_cons": [
                "Most deductions and exemptions not available (80C, 80D, HRA, etc.)",
                "May result in higher taxes for those with significant deductions",
                "Loss of tax benefits for home loan interest (Section 24)",
                "No tax benefits for health insurance premiums (Section 80D)",
                "No exemption for House Rent Allowance (HRA)"
            ]
        }
    
# Tax-related FAQ for the new regime
TAX_FAQ = {
    "What is the new tax regime for FY 2024-25?":
        "The new tax regime is a simplified tax structure with lower rates but fewer deductions. It's the default regime since FY 2023-24 unless you specifically opt for the old regime. For FY 2024-25, it offers a progressive slab structure starting from 0% for income up to ₹3 lakh, gradually increasing to 30% for income above ₹15 lakh.",
    
    "What are the upcoming changes to tax slabs in FY 2025-26?":
        "The Finance Bill 2025 has proposed significant changes to the tax slabs under the new regime. The tax-free income limit will increase to ₹4 lakh, with subsequent slabs at 5% (₹4-8 lakh), 10% (₹8-12 lakh), 15% (₹12-16 lakh), 20% (₹16-20 lakh), 25% (₹20-24 lakh), and 30% (above ₹24 lakh). These changes will apply from April 1, 2025, for the assessment year 2026-27.",
    
    "Who benefits most from the new tax regime?":
        "The new regime generally benefits individuals with limited investments or deductions, such as young professionals starting their careers, those with modest incomes, or taxpayers who don't claim significant deductions under sections like 80C, 80D, or 24(b). With the standard deduction still available, it offers simplicity and potentially lower tax rates for many.",
    
    "Can I switch between old and new tax regimes?":
        "Salaried individuals can choose either regime each financial year based on what's most advantageous. However, those with business income face restrictions - once they choose the new regime, they must continue with it for subsequent years with limited exceptions. It's advisable to calculate your tax liability under both regimes before making a decision.",
    
    "What deductions remain available in the new regime?":
        "While most deductions are unavailable in the new regime, you can still claim the standard deduction (₹50,000 for salaried individuals, increasing to ₹75,000 in FY 2025-26), professional tax deduction under section 16(iii), and employer contribution to NPS (up to 10% of salary). Additionally, certain business-related deductions like 80JJAA and 80M remain available.",
    
    "How does the tax rebate work under section 87A?":
        "Under Section 87A, if your total income doesn't exceed ₹7 lakh in FY 2024-25, you're eligible for a tax rebate of up to ₹25,000, effectively making income up to ₹7 lakh tax-free. For FY 2025-26, this rebate threshold will increase, making income up to ₹12 lakh effectively tax-free for salaried individuals (considering the ₹75,000 standard deduction).",
    
    "Are capital gains taxed differently under the new regime?":
        "The new tax regime primarily affects your regular income taxation (salary, business income, etc.). Capital gains continue to be taxed at their special rates regardless of which regime you choose. This includes short-term capital gains (15% on equity shares/mutual funds), long-term capital gains (10% on equity, 20% with indexation on other assets), and other special rates.",
    
    "Do I still need to file ITR if my income is below taxable limit?":
        "Yes. Even if no tax is payable because your income falls below the taxable threshold, you must file an Income Tax Return (ITR) if your income exceeds the basic exemption limit. Filing ITR is beneficial for claiming refunds, maintaining financial records for loans or visas, carrying forward losses, and avoiding scrutiny from tax authorities.",
    
    "What happens to my home loan tax benefits in the new regime?":
        "Under the new tax regime, you cannot claim deductions for home loan interest (Section 24) or principal repayment (Section 80C). If these deductions significantly reduce your tax liability, you might find the old regime more beneficial. However, with the higher basic exemption limit and revised slabs in the new regime, you should calculate both scenarios to determine which is more advantageous.",
    
    "What is the 'Tax Year' concept in the upcoming Income Tax Bill 2025?":
        "The Income Tax Bill 2025 introduces a unified 'Tax Year' concept to replace the current dual system of 'previous year' and 'assessment year'. This standardized 12-month period will simplify tax calculations and align with global practices. For new businesses or professionals, the tax year will commence from the date they establish their business or generate a new source of income.",
    
    "How will the new Income Tax Bill 2025 affect compliance requirements?":
        "The Income Tax Bill 2025 aims to simplify compliance through clearer language, reduced complexity, and streamlined provisions. The bill reduces the number of chapters from 47 to 23 and sections from 819 to 536. It eliminates obsolete provisions, simplifies references, and introduces more digital compliance mechanisms. These changes should make tax filing more straightforward and reduce litigation.",
    
    "What are the advance tax payment deadlines?":
        "If your total tax liability exceeds ₹10,000, you must pay advance tax in installments: 15% by June 15, 2024; 45% by September 15, 2024; 75% by December 15, 2024; and 100% by March 15, 2025. These percentages represent cumulative amounts, so each payment covers the difference between the current and previous threshold."
}

# Common exemptions and deductions NOT available in new tax regime
UNAVAILABLE_EXEMPTIONS = {
    "HRA": "House Rent Allowance exemption is not available in new regime",
    "LTA": "Leave Travel Allowance exemption is not available in new regime",
    "Section_80C": "Deduction for investments up to ₹1.5 lakh is not available in new regime",
    "Section_80D": "Deduction for health insurance premium is not available in new regime",
    "Section_24": "Deduction for home loan interest is not available in new regime",
    "Section_80E": "Deduction for education loan interest is not available in new regime",
    "Section_80G": "Deduction for charitable donations is not available in new regime",
    "Section_80TTA": "Deduction for savings account interest up to ₹10,000 is not available in new regime",
    "Section_80EEA": "Additional deduction for affordable housing loan interest is not available in new regime",
    "Section_80CCD": "Additional NPS contribution deduction (beyond employer contribution) is not available in new regime"
}
