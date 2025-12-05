# 🧾 AI Invoice Parser

AI-powered application for extracting structured data from PDF invoices.

---

# 📑 Table of Contents
1. Introduction
2. Key Features
3. System Requirements
4. Installation
5. User Guide
   - 1. Main Interface
   - 2. API Key Setup
   - 3. Select Invoice Folder
   - 4. Settings
   - 5. Start Parsing
6. Output Files
7. Troubleshooting
8. Notes

---

# Introduction

AI Invoice Parser is a simple and user-friendly Python application that extracts structured data from invoices using advanced AI models.

You select a folder containing PDF invoices, and the application automatically generates:

- A .txt file with extracted text  
- A .json file with structured fields  
- A .pdf copy of the original invoice  

---

# Key Features

- Automatic AI-based extraction  
- Clean and intuitive graphical interface  
- Batch processing of multiple invoices  
- Detailed logs and progress indicators  
- Local configuration for output options  
- API key stored locally and securely  

---

# System Requirements

- Windows 10 or 11  
- Python 3.10 or newer  
- Required Python packages from requirements.txt  

---

# Installation

1. Install Python (version 3.10 or higher).  
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Obtain a valid Google Gemini API key.  
4. Save your API key inside a file called **api.txt** in the project root folder.

---

# User Guide

## 1. Main Interface
![Main GUI](screenshots/1_gui.png)

## 2. API Key Setup
Insert your Gemini API key into **api.txt**.

![API Setup](screenshots/2_api.png)

## 3. Select Invoice Folder
Choose the folder that contains your PDF invoices.

![Source Folder](screenshots/3_source_folder.png)

## 4. Settings
Configure output preferences and formats.

![Settings](screenshots/4_settings.png)

## 5. Start Parsing
Press **Start** to begin invoice extraction.

![Progress & Logs](screenshots/5_progress_logs.png)

---

# Output Files

For each invoice, the application generates:

- `invoice_data.json` — structured extracted data  
- `invoice_text.txt` — extracted raw text  
- `invoice_original.pdf` — original invoice copy  

All files are saved inside the same folder you selected.

---

# Troubleshooting

### “API key not found”
Ensure that **api.txt** exists and contains a valid API key.

### “No PDF files found”
Verify that the selected folder contains `.pdf` files.

### Extraction errors
Check the log panel for details (corrupted or unreadable PDFs).

---

# Notes

- Your API key stays locally on your machine and is ignored by Git.  
- The application only sends text content to the AI model for extraction — no files are uploaded.
