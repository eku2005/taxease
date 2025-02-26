
# TaxEase: AI-Powered Indian Tax Assistant

## Navigating the Tax Maze with Confidence

TaxEase transforms the complex world of Indian taxation into a streamlined, intuitive experience. Designed for the new tax regime (FY 2024-25), this AI-powered assistant helps individuals calculate their tax liability, identify potential deductions, analyze financial data, and access personalized tax advice—all through a user-friendly interface.

> "Taxation made simple through the power of artificial intelligence."

## Key Features

- **Automated Tax Calculations**: Precise tax liability calculations under the new tax regime
- **Bank Statement Analysis**: Intelligent parsing of bank statements to identify potential tax deductions
- **Personalized Tax Reports**: Comprehensive, downloadable tax reports tailored to your financial situation
- **AI-Powered Tax Consultation**: Get answers to your tax questions through our Gemini-powered assistant
- **Tax Knowledge Base**: Access a comprehensive FAQ about the latest tax regulations
- **User-Friendly Interface**: Intuitive Streamlit interface accessible to users of all technical backgrounds

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip package manager

### Installation

1. Clone the repository:
```

git clone https://github.com/yourusername/taxease.git
cd taxease

```

2. Create a virtual environment (recommended):
```

python -m venv venv
source venv/bin/activate  \# On Windows: venv\Scripts\activate

```

3. Install dependencies:
```

pip install -r requirements.txt

```

### Running TaxEase

Launch the application with a simple command:

```

streamlit run tax_assistant.py

```

The application will open in your default web browser at `http://localhost:8501`.

## Using TaxEase

TaxEase offers a comprehensive suite of tax management tools:

### Enter Your Tax Details

Input your personal information and income details to begin your tax assessment. TaxEase securely stores this information for future sessions.

### Calculate Your Tax Liability

Get instant calculations of your tax liability under the new tax regime, including:
- Income breakdown by source
- Tax before and after rebate
- Health and education cess
- Total tax liability
- Visual representation of your tax burden

### Analyze Bank Statements

Upload your bank statements to automatically identify potential tax deductions:
- Medical expenses
- Education expenses
- Housing-related payments
- Insurance premiums
- Investments
- Charitable donations
- Business expenses

### Generate Tax Reports

Create detailed tax reports that can be downloaded and shared with your accountant or kept for your records.

### Consult TaxEase AI

Ask specific tax-related questions and receive accurate, personalized responses powered by Google's Gemini AI.

## Use Cases

### For Salaried Professionals

- Calculate tax liability under the new regime
- Compare with old regime implications
- Identify potential deductions from regular expenses
- Plan tax-saving investments

### For Freelancers and Consultants

- Track business expenses eligible for deductions
- Manage advance tax payment schedules
- Analyze income patterns for tax planning

### For Financial Advisors

- Generate client tax reports
- Provide data-driven tax advice
- Streamline client tax management

## AI Integration

TaxEase leverages Google's Gemini AI to provide:

- Natural language responses to tax queries
- Contextual understanding of Indian tax laws
- Up-to-date information on tax regulations
- Personalized advice based on financial situation

## Privacy and Security

- All data is stored locally on your machine
- No sensitive information is transmitted to external servers (except when using the optional AI consultation feature)
- Bank statement analysis happens entirely on your local system

## Technical Architecture

TaxEase is built with:

- **Streamlit**: For the interactive web interface
- **Pandas**: For financial data processing and analysis
- **Google Generative AI**: For the AI-powered tax consultation
- **Regular Expressions**: For intelligent parsing of financial documents

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Indian Income Tax Department for tax guidelines
- Streamlit for the interactive web framework
- Google for the Gemini AI capabilities

---

*Disclaimer: TaxEase is designed as an assistant tool and should not replace professional tax advice. Always consult with a qualified tax professional for your specific situation.*

*Developed for Girl Hackathon 2025 - Software Engineering Track*
```

<div style="text-align: center">⁂</div>

[^1]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/c6a2c744-daa9-496e-91da-e70b8c90f164/tax_assistant.py

[^2]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/29dc9c83-3eaa-4c88-a6bc-1074b13ee747/bank_statement_analyzer.py

[^3]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/f12c8a5b-3fb5-446d-a3a8-55037293e225/tax_assistant_ui.py

[^4]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/df461742-a4ac-486c-8317-69127de0390a/tax_assistant_base.py

[^5]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/d2002a77-6bb9-4a67-8ff7-d869009ea0a6/tax_assistant.py

[^6]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/d66598f0-b632-44a0-a6ea-a47f651cfefb/bank_statement_ui.py

[^7]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/428b6b6e-8108-4c74-a4f2-afcf5a32d3d6/README.md

[^8]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/60e4b613-7b8b-4fd0-b554-168c1e9a0d1e/requirements.txt

[^9]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/1f6bce71-2843-47b5-ba94-a33bf4a7910f/tax_rules.py

[^10]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/52529817/2773ba6f-5748-4936-a893-a1994affdf85/Ekam-Sandhu_Girl-Hackathon_SWE_2025.pdf

