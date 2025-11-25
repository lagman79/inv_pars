import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import threading
import time
import pandas as pd
import google.generativeai as genai
from glob import glob
from datetime import datetime

# --- ΚΕΙΜΕΝΑ ΟΔΗΓΙΩΝ (PROMPTS) ---

RULES_GREEN = """
ΚΑΝΟΝΕΣ ΚΑΤΗΓΟΡΙΟΠΟΙΗΣΗΣ (category_code):
- 1: Κτιριακές και λοιπές εγκαταστάσεις.
- 2.1: Παραγωγικός & Μηχανολογικός Εξοπλισμός.
- 2.2: Λοιπός εξοπλισμός (συστήματα ασφαλείας), εξοπλισμός γραφείου.
- 3: Εξοπλισμός για βελτίωση Ενεργειακής Απόδοσης.
- 4.1: Πιστοποίηση/συμμόρφωση προϊόντων.
- 4.2: Πιστοποίηση υπηρεσιών & διαδικασιών.
- 4.3: Πνευματική ιδιοκτησία - Ευρεσιτεχνίες.
- 5: Υπηρεσίες Σχεδιασμού Συσκευασίας - Branding.
- 6: Δαπάνες Προβολής και Εξωστρέφειας.
- 7: Συμμετοχή σε εμπορικές εκθέσεις.
- 8.1: Τεχνικές μελέτες.
- 8.2: Συμβουλευτική Υποστήριξη.
- 9: Ηλεκτρικά Μεταφορικά Μέσα.
- 10: Δαπάνες Προσωπικού.
"""

RULES_DIGITAL = """
ΚΑΝΟΝΕΣ ΚΑΤΗΓΟΡΙΟΠΟΙΗΣΗΣ (category_code):
- 1: Ψηφιακός εξοπλισμός γραφείου (PC, Laptop, Printers, Servers).
- 2: Αναβάθμιση υποδομών internet (Cabling, Wi-Fi).
- 3: Εφαρμογές γραφείου/ασφάλειας/αποθήκευσης (Office, Antivirus, Cloud).
- 4: Εφαρμογές βελτιστοποίησης (ERP, CRM, WMS, E-shop).
- 5: Κατασκευή ιστοσελίδας, eshop.
- 6: Συμβουλευτική υποστήριξη.
- 7: Τεχνικός σύμβουλος.
- 8: Λογισμικό ως υπηρεσία (SaaS).
"""

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Invoice Extractor Pro V10")
        self.root.geometry("700x650")

        # Variables
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        self.api_key = tk.StringVar()
        self.extract_all = tk.BooleanVar()
        self.category_mode = tk.StringVar(value="None")
        self.is_running = False

        # --- UI LAYOUT ---
        frame_api = tk.LabelFrame(root, text="Ρυθμίσεις API", padx=10, pady=10)
        frame_api.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_api, text="Gemini API Key:").pack(side="left")
        self.entry_api = tk.Entry(frame_api, textvariable=self.api_key, show="*", width=40)
        self.entry_api.pack(side="left", padx=5)
        
        frame_files = tk.LabelFrame(root, text="Αρχεία", padx=10, pady=10)
        frame_files.pack(fill="x", padx=10, pady=5)
        tk.Button(frame_files, text="📂 Επιλογή Φακέλου PDF (Είσοδος)", command=self.select_input).grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(frame_files, textvariable=self.input_folder, fg="blue").grid(row=0, column=1, sticky="w", padx=5)
        tk.Button(frame_files, text="💾 Αποθήκευση Excel ως... (Έξοδος)", command=self.select_output).grid(row=1, column=0, sticky="w", pady=2)
        tk.Label(frame_files, textvariable=self.output_file, fg="green").grid(row=1, column=1, sticky="w", padx=5)

        frame_opts = tk.LabelFrame(root, text="Επιλογές Επεξεργασίας", padx=10, pady=10)
        frame_opts.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_opts, text="Πρόγραμμα / Κατηγοριοποίηση:").grid(row=0, column=0, sticky="w")
        options = ["Χωρίς Κατηγοριοποίηση", "Πράσινη Παραγωγική Επένδυση ΜμΕ", "Βασικός Ψηφιακός Μετασχηματισμός ΜμΕ"]
        self.combo_cat = ttk.Combobox(frame_opts, textvariable=self.category_mode, values=options, width=40, state="readonly")
        self.combo_cat.current(0)
        self.combo_cat.grid(row=0, column=1, sticky="w", padx=5)

        tk.Checkbutton(frame_opts, text="🔍 Εξαγωγή ΟΛΩΝ των επιπλέον πεδίων (Full Extract)", variable=self.extract_all).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        tk.Label(frame_opts, text="(Θα μπουν στο τέλος)", font=("Arial", 8, "italic")).grid(row=2, column=0, columnspan=2, sticky="w")

        self.progress = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=10)
        
        self.log_text = tk.Text(root, height=10, state="disabled", bg="#f0f0f0")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        self.btn_start = tk.Button(root, text="🚀 ΕΚΚΙΝΗΣΗ", command=self.start_thread, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.btn_start.pack(fill="x", padx=10, pady=10)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def select_input(self):
        folder = filedialog.askdirectory()
        if folder: self.input_folder.set(folder)

    def select_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file: self.output_file.set(file)

    def start_thread(self):
        if not self.api_key.get() or not self.input_folder.get() or not self.output_file.get():
            messagebox.showwarning("Προσοχή", "Συμπλήρωσε API Key, Φάκελο Εισόδου και Αρχείο Εξόδου!")
            return
        
        self.is_running = True
        self.btn_start.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        
        threading.Thread(target=self.process_invoices, daemon=True).start()

    def process_invoices(self):
        try:
            input_dir = self.input_folder.get()
            output_path = self.output_file.get()
            api_key = self.api_key.get().strip()
            mode = self.category_mode.get()
            full_extract = self.extract_all.get()

            genai.configure(api_key=api_key, transport='rest')
            
            pdf_files = glob(os.path.join(input_dir, "*.pdf"))
            if not pdf_files:
                self.log("❌ Δεν βρέθηκαν PDF στον φάκελο.")
                self.reset_ui()
                return

            self.log(f"🚀 Βρέθηκαν {len(pdf_files)} αρχεία. Ξεκινάμε...")
            self.progress["maximum"] = len(pdf_files)
            
            all_data = []

            for i, pdf_file in enumerate(pdf_files, 1):
                filename = os.path.basename(pdf_file)
                self.log(f"[{i}/{len(pdf_files)}] Επεξεργασία: {filename}")
                
                try:
                    data = self.analyze_single_pdf(pdf_file, mode, full_extract)
                    if data:
                        data['filename'] = filename
                        all_data.append(data)
                        self.log("   ✅ Επιτυχία")
                    else:
                        self.log("   ⚠️ Αποτυχία ανάλυσης")
                except Exception as e:
                    self.log(f"   ❌ Σφάλμα: {str(e)}")

                self.progress["value"] = i
                time.sleep(2)

            # --- EXCEL SAVING LOGIC ---
            if all_data:
                df = pd.DataFrame(all_data)
                
                for col in ['net_value', 'vat_value', 'total_amount']:
                    if col in df.columns:
                        df[col] = df[col].apply(self.format_currency)

                # Rename Standard Columns
                mapping = {
                    'supplier_name': 'ΠΡΟΜΗΘΕΥΤΗΣ', 'supplier_vat': 'ΑΦΜ ΠΡΟΜΗΘΕΥΤΗ',
                    'type': 'ΕΙΔΟΣ ΠΑΡΑΣΤ.', 'invoice_number': 'ΑΡ. ΠΑΡΑΣΤ.',
                    'date': 'ΗΜ/ΝΙΑ', 'description': 'ΠΕΡΙΓΡΑΦΗ',
                    'net_value': 'ΚΑΘΑΡΗ ΑΞΙΑ', 'vat_value': 'ΦΠΑ',
                    'total_amount': 'ΤΕΛΙΚΗ ΑΞΙΑ', 'mark_code': 'ΜΑΡΚ',
                    'filename': 'ΟΝΟΜΑ ΑΡΧΕΙΟΥ', 'serial_number': 'SERIAL',
                    'category_code': 'Κ.Δ.', 'related_document': 'ΣΧΕΤ. ΠΑΡΑΣΤ.',
                    'notes': 'ΠΑΡΑΤΗΡΗΣΕΙΣ', 'loading_place': 'ΦΟΡΤΩΣΗ',
                    'destination_place': 'ΠΡΟΟΡΙΣΜΟΣ'
                }
                
                # Expand Dynamic Fields
                dynamic_cols_names = []
                if full_extract and 'dynamic_fields' in df.columns:
                    dynamic_df = df['dynamic_fields'].apply(pd.Series)
                    df = pd.concat([df.drop(['dynamic_fields'], axis=1), dynamic_df], axis=1)
                    dynamic_cols_names = list(dynamic_df.columns)

                df.rename(columns=mapping, inplace=True)
                
                # --- ΔΙΑΤΑΞΗ ΣΤΗΛΩΝ ---
                left_cols = [
                    'ΠΡΟΜΗΘΕΥΤΗΣ', 'ΑΦΜ ΠΡΟΜΗΘΕΥΤΗ', 'ΕΙΔΟΣ ΠΑΡΑΣΤ.', 'ΑΡ. ΠΑΡΑΣΤ.',
                    'ΗΜ/ΝΙΑ', 'ΠΕΡΙΓΡΑΦΗ', 'ΚΑΘΑΡΗ ΑΞΙΑ', 'ΦΠΑ', 'ΤΕΛΙΚΗ ΑΞΙΑ',
                    'ΜΑΡΚ', 'ΟΝΟΜΑ ΑΡΧΕΙΟΥ', 'ΣΧΕΤ. ΠΑΡΑΣΤ.', 'ΠΑΡΑΤΗΡΗΣΕΙΣ', 
                    'ΦΟΡΤΩΣΗ', 'ΠΡΟΟΡΙΣΜΟΣ', 'Κ.Δ.', 'SERIAL'
                ]
                # 2. Σταθερά Δεξιά (ΤΟ ΑΔΕΙΑΖΟΥΜΕ ή το σβήνουμε, αφού πήγε στο left_cols)
                right_cols = [] 
                
                # 3. Υπολογισμός υπαρκτών στηλών
                existing_left = [c for c in left_cols if c in df.columns]
                # Τα δυναμικά είναι όσα δεν είναι στη λίστα left_cols
                existing_dynamic = [c for c in df.columns if c not in left_cols]
                
                # Τελική Σύνθεση: Πρώτα τα Σταθερά (με SERIAL), μετά τα Έξτρα
                final_order = existing_left + existing_dynamic
                
                df = df[final_order]
                df = df.fillna("")

                df.to_excel(output_path, index=False)
                self.log(f"\n🎉 Ολοκληρώθηκε! Αποθηκεύτηκε στο:\n{output_path}")
                messagebox.showinfo("Επιτυχία", "Η διαδικασία ολοκληρώθηκε!")
            else:
                self.log("⚠️ Δεν εξήχθησαν δεδομένα.")

        except Exception as e:
            self.log(f"❌ Κρίσιμο Σφάλμα: {e}")
            messagebox.showerror("Σφάλμα", str(e))
        finally:
            self.reset_ui()

    def analyze_single_pdf(self, pdf_path, mode, full_extract):
        sample_file = genai.upload_file(path=pdf_path, display_name="Invoice")
        while sample_file.state.name == "PROCESSING":
            time.sleep(1)
            sample_file = genai.get_file(sample_file.name)
        
        if sample_file.state.name == "FAILED": return None

        model = genai.GenerativeModel("models/gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})

        cat_rules = ""
        if mode == "Πράσινη Παραγωγική Επένδυση ΜμΕ": cat_rules = RULES_GREEN
        elif mode == "Βασικός Ψηφιακός Μετασχηματισμός ΜμΕ": cat_rules = RULES_DIGITAL
        else: cat_rules = "- 1: Hardware\n- 3: Software\n- 8: SaaS\n- 6: Services"

        extra_instruction = ""
        if full_extract:
            extra_instruction = """
            ΕΠΙΠΛΕΟΝ (FULL EXTRACT):
            Ψάξε για ΟΠΟΙΟΔΗΠΟΤΕ άλλο πεδίο υπάρχει (π.χ. Διεύθυνση, Πόλη, ΤΚ, Τηλέφωνο, IBAN, Τράπεζα, ΔΟΥ).
            Βάλτα όλα σε ένα αντικείμενο 'dynamic_fields' με κλειδιά ΑΥΣΤΗΡΑ ΣΤΑ ΕΛΛΗΝΙΚΑ (π.χ. "Διεύθυνση", "Τηλέφωνο").
            """

        # --- ΕΝΗΜΕΡΩΜΕΝΟ PROMPT ΓΙΑ SERIAL NUMBER ---
        prompt = f"""
        Είσαι ειδικός λογιστής. Ανάλυσε το τιμολόγιο και δώσε JSON.
        
        {cat_rules}

        ΟΔΗΓΙΕΣ:
        1. serial_number (SERIAL): 
           α) Ψάξε για ετικέτες: "serial number", "s/n", "σειριακός", "sn".
           β) ΣΗΜΑΝΤΙΚΟ: Ψάξε για "ορφανά" αλφαριθμητικά strings (π.χ. A5I4B3500039JV) που βρίσκονται ακριβώς κάτω από την περιγραφή του είδους, ακόμα κι αν δεν έχουν ετικέτα "S/N" (όπως σε τιμολόγια Πλαισίου/InfoQuest). Αν βρεις τέτοιον κωδικό, είναι το serial number.
        2. net_value: Η Φορολογητέα Αξία (μετά τις εκπτώσεις).
        3. mark_code: Αριθμός που ξεκινάει με "40".
        4. description: Αντίγραψε τα είδη χωρισμένα με "|".
        5. type: ΜΟΝΟ "ΤΠΥ", "ΤΔΑ", "ΠΙΣΤΩΤΙΚΟ", "ΤΙΜ".
        
        {extra_instruction}

        ΠΕΔΙΑ JSON:
        - date, supplier_name, supplier_vat, invoice_number, mark_code
        - description, net_value, vat_value, total_amount, type
        - related_document, notes, loading_place, destination_place
        - category_code
        - serial_number
        {"- dynamic_fields (object)" if full_extract else ""}
        """

        response = model.generate_content([sample_file, prompt])
        genai.delete_file(sample_file.name)
        data = json.loads(response.text)

        data['mark_code'] = self.validate_mark_code(data.get('mark_code'))
        data['type'] = self.normalize_type(data.get('type'))
        
        return data

    def reset_ui(self):
        self.is_running = False
        self.btn_start.config(state="normal")

    @staticmethod
    def validate_mark_code(code):
        if not code: return None
        c = str(code).replace(" ", "").replace("-", "")
        if c.isdigit() and c.startswith("40") and len(c) >= 15: return c
        return None

    @staticmethod
    def normalize_type(t):
        if not t: return "ΤΙΜ"
        t = t.strip().upper()
        return t if t in ["ΤΙΜ", "ΤΠΥ", "ΤΔΑ", "ΠΙΣΤΩΤΙΚΟ"] else "ΤΙΜ"

    @staticmethod
    def format_currency(val):
        if not val: return ""
        try:
            return "{:,.2f}".format(float(val)).replace(",", "X").replace(".", ",").replace("X", ".") + " €"
        except: return str(val)

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()