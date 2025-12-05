# AI Invoice Extractor
### 🧾 AI-powered invoice parsing, categorization & file organization

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/Gemini_API-2.5%20Flash-green" alt="Gemini API">
  <img src="https://img.shields.io/badge/GUI-Tkinter-yellow" alt="Tkinter GUI">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License">
</p>

> 🇬🇷 **Greek Version:** For the Greek documentation, click [here](README_GR.md).

**AI Invoice Extractor** is a desktop application with a **Python Tkinter GUI** that uses **Google Gemini 2.5 Flash** to extract structured data from invoices (**PDF, JPG, PNG, WEBP**) and export them into an **Excel file**.

It is designed for professionals who need to process invoices efficiently, with specialized features for **ESPA funding programs** (Greek NSRF).

---

## 📝 Overview & Extracted Fields

The AI automatically detects and structures the following fields:

* **General Info:** Date (converted to DD/MM/YYYY), Invoice Number, Supplier Name & VAT Number.
* **Financials:** Net Value, VAT Value, Total Amount.
* **Charges:** Withholding tax, stamp duties, environmental fees, etc.
* **Tax Compliance:** MARK Code (MyData), Serial Number (S/N).
* **Logistics:** Loading & Destination locations, Related Documents.
* **Descriptions:** Merged line item descriptions.
* **Dynamic Fields:** Detects *any* additional field found on the document (when "Full Extract" is enabled).

---

## ⭐ Key Features

### 🔹 AI-Powered Parsing
Uses the robust **Gemini 2.5 Flash** model to read complex document layouts.

### 🔹 ESPA Funding Categorization
Automatically assigns the correct **Expense Category Code** based on the invoice description. Supports:
* Green Productive Investment for SMEs
* Basic Digital Transformation for SMEs

### 🔹 File Organization
* **Auto-Renaming:** Files are renamed to `Supplier_InvoiceNumber.pdf`.
* **Smart Sorting:** Files are automatically copied or moved into folders named after the Supplier.

### 🔹 Progress Tracking
Includes a live progress bar, real-time logs, success/error summaries, and highlights failed entries in Red within the Excel file.

---

## 🛠 Installation

### 1. Clone the repository
```bash
git clone [https://github.com/](https://github.com/)<your_username>/<your_repo>.git
cd <your_repo>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a Gemini API Key
To run the application, you need a free API Key from Google.
1.  Visit **[Google AI Studio](https://aistudio.google.com/)**.
2.  Generate a new API Key.
3.  You will enter this key directly in the application GUI.

---

## ▶️ How to Use

### Step 1: Configuration
* **API Key:** Paste your Gemini API Key.
* **Folders:** Select your Input Folder (invoices) and Output Path (Excel).

<p align="center"><img src="screenshots/2. api.png" alt="API Key Input" width="600"/></p>
<p align="center"><img src="screenshots/3. φάκελος εισαγωγής.png" alt="Input Folder" width="600"/></p>

### Step 2: Parameters
* **ESPA Program:** Select a program to enable auto-categorization of expenses.
* **Full Extract:** Check this to extract all available dynamic fields.

<p align="center"><img src="screenshots/4 ρυθμίσεις - οργάνωση.png" alt="Settings" width="600"/></p>

### Step 3: Run & Monitor
Click **"🚀 ΕΚΚΙΝΗΣΗ" (START)**.
* The app processes files one by one.
* **Logs** show real-time status.

<p align="center"><img src="screenshots/5 progress bars & logs.png" alt="Logs" width="600"/></p>

### Step 4: Results
The Excel file opens automatically.
* **New Task:** Resets the interface.
* **Exit:** Closes the app.

<p align="center"><img src="screenshots/1. κεντρικό GUI.jpg" alt="Main GUI" width="600"/></p>
<p align="center"><img src="screenshots/6 start_new task & exit buttons.png" alt="Controls" width="400"/></p>

---

## ❗ Troubleshooting

| Issue | Cause | Solution |
|-------|--------|-----------|
| **Invalid or no JSON** | Model parsing issue | Retry or use a clearer scan. |
| **403 API Error** | Invalid Key | Enter a correct API Key. |
| **429 Too Many Requests** | Rate Limit | Wait 1–2 minutes and retry. |
| **Timeout** | File too large/complex | Try again. |
| **Excel cannot save** | File is open | **Close the Excel file** and re-run. |

---

## 🔧 Technical Notes
* **Engine:** Google Gemini 2.5 Flash via REST API.
* **GUI:** Python Tkinter.
* **Formats:** PDF, JPG, PNG, WEBP.
* **Output:** Dynamic Excel generation with `openpyxl`.

---

## 📄 License
MIT License