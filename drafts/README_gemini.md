# AI Invoice Extractor - Automated Invoice Data Extraction & Organization Tool

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/Gemini_API-2.5%20Flash-green" alt="Gemini API">
  <img src="https://img.shields.io/badge/GUI-Tkinter-yellow" alt="Tkinter GUI">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey" alt="Platform">
</p>

> 🇬🇷 **Greek Version:** For the Greek documentation, click [here](README_GR.md).

The **AI Invoice Extractor** is a standalone application with a **Graphical User Interface (GUI)**, designed for the automated extraction of critical data from digital invoices and receipts (PDF, JPG, PNG, WEBP) using the **Gemini AI API** from Google. The extracted data is neatly organized and saved into an **Excel (.xlsx)** file.

---

## 💡 Key Features

* **Accurate Data Extraction:** Leverages the Gemini 2.5 Flash model for robust field recognition.
* **Specialized Categorization (ESPA/EU Funds):** Automated classification of expenses based on specific EU funding program rules (e.g., Greek ESPA programs).
* **File Organization:** Automatic renaming and sorting of invoice files into folders categorized by supplier.

### 📊 Extracted Fields

The application extracts and formats the following core fields:

* **Invoice Details:** Supplier Name, Supplier VAT, Invoice Number, Date ($\text{YYYY-MM-DD} \rightarrow \text{DD/MM/YYYY}$), Document Type.
* **Financial Data:** Net Value, VAT Value, Total Amount, Extra Charges/Fees (Withholding Tax, Stamp Duty, etc.).
* **Other:** Description (Concatenated), MARK Code ($\text{MyData}$), Serial Number, Related Document, Loading/Destination Places.
* **Expense Category ($\text{K.D.}$):** (If an ESPA program is selected).
* **Full Extract (Dynamic Fields):** Extracts **all** additional fields found on the invoice, added as new columns in Excel.

---

## 🛠️ System Requirements & Installation

The application is developed in **Python 3.x**.

### 📥 Installation

1. Clone the repository.
2. Install the required libraries:

```bash
pip install -r requirements.txt