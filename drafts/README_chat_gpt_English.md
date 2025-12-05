# AI Invoice Extractor  
### 🧾 AI-powered invoice parsing, categorization & file organization (Gemini 2.5 Flash + Python GUI)

---

## 📑 Table of Contents / Πίνακας Περιεχομένων
- [English Version](#english-version)
  - [Overview](#overview)
  - [Features](#features)
  - [Installation](#installation)
  - [How to Use](#how-to-use)
  - [Screenshots](#screenshots)
  - [Troubleshooting](#troubleshooting)
  - [Technical Notes](#technical-notes)
  - [License](#license)

- [Ελληνική Έκδοση](#ελληνική-έκδοση)
  - [Περιγραφή](#περιγραφή)
  - [Λειτουργίες](#λειτουργίες)
  - [Εγκατάσταση](#εγκατάσταση)
  - [Οδηγίες Χρήσης](#οδηγίες-χρήσης)
  - [Στιγμιότυπα Οθόνης](#στιγμιότυπα-οθόνης)
  - [Αντιμετώπιση Προβλημάτων](#αντιμετώπιση-προβλημάτων)
  - [Τεχνικές Σημειώσεις](#τεχνικές-σημειώσεις)
  - [Άδεια](#άδεια)

---

# ENGLISH VERSION

---

## 📝 Overview

**AI Invoice Extractor** is a desktop application with a Python GUI (Tkinter) that uses **Google Gemini 2.5 Flash** to extract structured data from invoice files:

- **PDF**, **JPG**, **PNG**, **WEBP**

It automatically reads and writes structured fields to an **Excel file**, such as:

- Date (ISO → DD/MM/YYYY)
- Supplier name & VAT number
- Invoice number
- Description lines (merged)
- Net value, VAT, total amount
- MARK code (MyData)
- Serial number (S/N)
- Extra charges (taxes, retention, stamp duty, etc.)
- Related document
- Loading & destination points
- Additional dynamic fields ("Full Extract")

The application also provides **automatic renaming** and **supplier-based folder organization**, helpful when processing large volumes of invoices.

---

## ⭐ Features

### 🔹 AI-Powered Invoice Parsing
Extracts all essential accounting fields using Google Gemini.

### 🔹 ESPA Funding Program Categorization
Two supported programs:
- *Green Productive Investment for SMEs*
- *Basic Digital Transformation for SMEs*

The model automatically assigns the correct **Expense Category Code** based on the invoice description.

### 🔹 Full Extract Mode
Detects **any extra fields** present in the invoice and generates additional Excel columns dynamically.

### 🔹 Automatic File Renaming
Renames files to: Supplier_InvoiceNumber.pdf


### 🔹 Organization into Supplier Folders
Copies or moves files into auto-created folders per supplier.

### 🔹 Progress Display
- Progress bar
- Real-time logs per file  
- Summary of successes & failures  
- Failed rows in Excel are highlighted in red

---

## 🛠 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your_username>/<your_repo>.git
cd <your_repo>
