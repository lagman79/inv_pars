import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import threading
import time
import re  # <-- ΝΕΑ ΒΙΒΛΙΟΘΗΚΗ ΓΙΑ REGEX
import pandas as pd
import google.generativeai as genai
from glob import glob
from datetime import datetime

# --- ΡΥΘΜΙΣΕΙΣ & CONSTANTS ---
SETTINGS_FILE = "settings.json"

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

class DataProcessor:
    
    @staticmethod
    def validate_mark_code(code):
        """
        Έξυπνος εντοπισμός ΜΑΡΚ με Regex.
        Ψάχνει για μοτίβο '40' ακολουθούμενο από τουλάχιστον 13 ψηφία,
        οπουδήποτε μέσα στο κείμενο.
        """
        if not code: return None
        
        # Καθαρίζουμε κενά και παύλες για να μην σπάει ο αριθμός
        clean_text = str(code).replace(" ", "").replace("-", "")
        
        # REGEX: Ψάξε για 40 ακολουθούμενο από 13 ή περισσότερα ψηφία (\d{13,})
        match = re.search(r'40\d{13,}', clean_text)
        
        if match:
            return match.group(0) # Επιστρέφει μόνο τον αριθμό που βρήκε
        return None

    @staticmethod
    def normalize_type(t):
        if not t: return "ΤΙΜ"
        t = t.strip().upper()
        valid = ["ΤΙΜ", "ΤΠΥ", "ΤΔΑ", "ΠΙΣΤΩΤΙΚΟ", "ΠΑΡΑΓΓΕΛΙΑ"]
        return t if t in valid else "ΤΙΜ"

    @staticmethod
    def format_currency(val):
        if not val: return ""
        try:
            return "{:,.2f}".format(float(val)).replace(",", "X").replace(".", ",").replace("X", ".") + " €"
        except: return str(val)

    @staticmethod
    def fix_description_lines(data):
        desc = data.get('description')
        if isinstance(desc, list):
            items = []
            for item in desc:
                if isinstance(item, dict): items.append(str(item.get('description', '')))
                else: items.append(str(item))
            data['description'] = " | ".join(items)

        keys_to_check = ['lines', 'items', 'products']
        found_extra_desc = []
        for key in keys_to_check:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        d = item.get('description')
                        if d: found_extra_desc.append(str(d))
                    else: found_extra_desc.append(str(item))
                del data[key]
        
        if (not data.get('description') or data.get('description') == "") and found_extra_desc:
            data['description'] = " | ".join(found_extra_desc)

        return data

    @staticmethod
    def analyze_file(file_path, api_key, mode, full_extract):
        genai.configure(api_key=api_key, transport='rest')
        sample_file = genai.upload_file(path=file_path, display_name="Invoice")
        
        timeout = 60 
        start_time = time.time()
        while sample_file.state.name == "PROCESSING":
            if time.time() - start_time > timeout: raise TimeoutError("Timeout.")
            time.sleep(1)
            sample_file = genai.get_file(sample_file.name)
        
        if sample_file.state.name == "FAILED": raise ValueError("Upload failed.")

        model = genai.GenerativeModel("models/gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})

        cat_rules = ""
        if mode == "Πράσινη Παραγωγική Επένδυση ΜμΕ": cat_rules = RULES_GREEN
        elif mode == "Βασικός Ψηφιακός Μετασχηματισμός ΜμΕ": cat_rules = RULES_DIGITAL
        else: cat_rules = "- 1: Hardware\n- 3: Software\n- 8: SaaS\n- 6: Services"

        extra_instruction = ""
        if full_extract:
            extra_instruction = """
            ΕΠΙΠΛΕΟΝ (FULL EXTRACT):
            Ψάξε για ΟΠΟΙΟΔΗΠΟΤΕ άλλο πεδίο υπάρχει.
            Βάλτα σε αντικείμενο 'dynamic_fields' με κλειδιά ΑΥΣΤΗΡΑ ΣΤΑ ΕΛΛΗΝΙΚΑ.
            """

        prompt = f"""
        Είσαι ειδικός λογιστής. Ανάλυσε το παραστατικό και δώσε JSON.
        
        {cat_rules}

        ΟΔΗΓΙΕΣ:
        1. serial_number (SERIAL): 
           α) Ψάξε για ετικέτες "s/n", "serial".
           β) Ψάξε για "ορφανά" αλφαριθμητικά strings κάτω από την περιγραφή.
        2. net_value: Η Φορολογητέα Αξία (μετά τις εκπτώσεις).
        3. mark_code: Ψάξε για τον "Μ.Αρ.Κ" ή "MARK" ή "UID". Είναι ένας αριθμός που ξεκινάει με "40". Αν είναι δίπλα σε άλλο κείμενο (π.χ. "Αναγν: ... / Μ.Αρ.Κ: 40..."), εξήγαγε ΜΟΝΟ τον αριθμό που ξεκινάει με 40.
        4. description: Όλα τα είδη σε ΕΝΑ string με "|".
        5. type: "ΤΠΥ", "ΤΔΑ", "ΠΙΣΤΩΤΙΚΟ", "ΤΙΜ", "ΠΑΡΑΓΓΕΛΙΑ".
        
        {extra_instruction}

        ΠΕΔΙΑ JSON:
        - date, supplier_name, supplier_vat, invoice_number, mark_code
        - description (String), net_value, vat_value, total_amount, type
        - related_document, notes, loading_place, destination_place
        - category_code
        - serial_number
        {"- dynamic_fields (object)" if full_extract else ""}
        """

        try:
            response = model.generate_content([sample_file, prompt])
            genai.delete_file(sample_file.name)
            data = json.loads(response.text)

            data = DataProcessor.fix_description_lines(data)
            data['mark_code'] = DataProcessor.validate_mark_code(data.get('mark_code'))
            data['type'] = DataProcessor.normalize_type(data.get('type'))
            
            return data
        except Exception as e:
            try: genai.delete_file(sample_file.name)
            except: pass
            raise e

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Invoice Extractor Pro V14")
        self.root.geometry("720x750")
        
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        self.api_key = tk.StringVar()
        self.extract_all = tk.BooleanVar()
        self.category_mode = tk.StringVar(value="None")
        self.is_running = False
        
        self.load_settings()
        self.create_widgets()
        
    def create_widgets(self):
        frame_api = tk.LabelFrame(self.root, text="🔐 Ρυθμίσεις Ασφαλείας", padx=10, pady=10)
        frame_api.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_api, text="Gemini API Key:").pack(side="left")
        
        self.entry_api = tk.Entry(frame_api, textvariable=self.api_key, show="*", width=50)
        self.entry_api.pack(side="left", padx=5)
        self.add_context_menu(self.entry_api)

        frame_files = tk.LabelFrame(self.root, text="📂 Διαχείριση Αρχείων", padx=10, pady=10)
        frame_files.pack(fill="x", padx=10, pady=5)
        
        tk.Button(frame_files, text="Επιλογή Φακέλου", command=self.select_input, width=20).grid(row=0, column=0, pady=2)
        tk.Entry(frame_files, textvariable=self.input_folder, width=50, state="readonly").grid(row=0, column=1, padx=5)
        
        tk.Button(frame_files, text="Αποθήκευση Excel", command=self.select_output, width=20).grid(row=2, column=0, pady=2)
        tk.Entry(frame_files, textvariable=self.output_file, width=50, state="readonly").grid(row=2, column=1, padx=5)

        frame_opts = tk.LabelFrame(self.root, text="⚙️ Παράμετροι", padx=10, pady=10)
        frame_opts.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_opts, text="Πρόγραμμα:").grid(row=0, column=0, sticky="w")
        options = ["Χωρίς Κατηγοριοποίηση", "Πράσινη Παραγωγική Επένδυση ΜμΕ", "Βασικός Ψηφιακός Μετασχηματισμός ΜμΕ"]
        self.combo_cat = ttk.Combobox(frame_opts, textvariable=self.category_mode, values=options, width=45, state="readonly")
        self.combo_cat.current(0)
        self.combo_cat.grid(row=0, column=1, padx=5, sticky="w")

        tk.Checkbutton(frame_opts, text="Ενεργοποίηση Full Extract (Δυναμικά Πεδία)", variable=self.extract_all).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=10)
        
        self.log_text = tk.Text(self.root, height=12, state="disabled", bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        self.btn_start = tk.Button(self.root, text="🚀 ΕΚΚΙΝΗΣΗ", command=self.start_thread, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
        self.btn_start.pack(fill="x", padx=10, pady=5)

        frame_actions = tk.Frame(self.root)
        frame_actions.pack(fill="x", padx=10, pady=5)
        tk.Button(frame_actions, text="🔄 Νέα Εργασία", command=self.reset_app, width=15).pack(side="left", padx=5)
        tk.Button(frame_actions, text="❌ Έξοδος", command=self.close_app, width=15, fg="red").pack(side="right", padx=5)

    def add_context_menu(self, widget):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Επικόλληση", command=lambda: widget.event_generate("<<Paste>>"))
        widget.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.api_key.set(data.get("api_key", ""))
                    self.input_folder.set(data.get("input_folder", ""))
                    self.output_file.set(data.get("output_file", ""))
            except: pass

    def save_settings(self):
        data = {
            "api_key": self.api_key.get(),
            "input_folder": self.input_folder.get(),
            "output_file": self.output_file.get()
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def select_input(self):
        f = filedialog.askdirectory()
        if f: self.input_folder.set(f)

    def select_output(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if f: self.output_file.set(f)
    
    def reset_app(self):
        self.input_folder.set("")
        self.output_file.set("")
        self.progress["value"] = 0
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        self.btn_start.config(state="normal")
        self.log("🔄 Έτοιμο για νέα εργασία.")

    def close_app(self):
        if messagebox.askyesno("Έξοδος", "Θέλετε σίγουρα να κλείσετε την εφαρμογή;"):
            self.root.destroy()

    def start_thread(self):
        if not self.api_key.get() or not self.input_folder.get():
            messagebox.showwarning("Προσοχή", "Λείπουν στοιχεία (API Key ή Φάκελος)!")
            return
        
        self.save_settings()
        self.is_running = True
        self.btn_start.config(state="disabled", text="⏳ ΣΕ ΕΞΕΛΙΞΗ...")
        self.log_text.config(state="normal"); self.log_text.delete(1.0, "end"); self.log_text.config(state="disabled")
        
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        try:
            input_dir = self.input_folder.get()
            output_path = self.output_file.get()
            if not output_path: output_path = os.path.join(input_dir, "results.xlsx")
            
            supported_extensions = ["*.pdf", "*.jpg", "*.jpeg", "*.png", "*.webp"]
            all_files = []
            for ext in supported_extensions:
                all_files.extend(glob(os.path.join(input_dir, ext)))
            all_files = sorted(all_files)

            if not all_files:
                self.log("❌ Δεν βρέθηκαν αρχεία.")
                return

            self.progress["maximum"] = len(all_files)
            all_data = []

            for i, f in enumerate(all_files, 1):
                if not self.is_running: break
                filename = os.path.basename(f)
                self.log(f"Επεξεργασία: {filename}")
                
                try:
                    data = DataProcessor.analyze_file(
                        f, 
                        self.api_key.get().strip(), 
                        self.category_mode.get(), 
                        self.extract_all.get()
                    )
                    data['filename'] = filename
                    all_data.append(data)
                    self.log("✅ Επιτυχία")
                except Exception as e:
                    self.log(f"❌ Σφάλμα: {str(e)}")
                
                self.progress["value"] = i
                time.sleep(2)

            if all_data:
                self.generate_excel(all_data, output_path)
            else:
                self.log("⚠️ Δεν προέκυψαν δεδομένα.")

        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_running = False
            self.btn_start.config(state="normal", text="🚀 ΕΚΚΙΝΗΣΗ")

    def generate_excel(self, all_data, path):
        df = pd.DataFrame(all_data)
        
        for col in ['net_value', 'vat_value', 'total_amount']:
            if col in df.columns:
                df[col] = df[col].apply(DataProcessor.format_currency)

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
        
        dynamic_cols = []
        if self.extract_all.get() and 'dynamic_fields' in df.columns:
            dynamic_df = df['dynamic_fields'].apply(pd.Series)
            df = pd.concat([df.drop(['dynamic_fields'], axis=1), dynamic_df], axis=1)
            dynamic_cols = list(dynamic_df.columns)

        df.rename(columns=mapping, inplace=True)

        # DATE FORMATTING FIX
        if 'ΗΜ/ΝΙΑ' in df.columns:
            def fix_date(x):
                if not x: return ""
                try:
                    return pd.to_datetime(x, dayfirst=True, errors='coerce').strftime('%d/%m/%Y')
                except: return str(x)
            df['ΗΜ/ΝΙΑ'] = df['ΗΜ/ΝΙΑ'].apply(fix_date)

        left_cols = [
            'ΠΡΟΜΗΘΕΥΤΗΣ', 'ΑΦΜ ΠΡΟΜΗΘΕΥΤΗ', 'ΕΙΔΟΣ ΠΑΡΑΣΤ.', 'ΑΡ. ΠΑΡΑΣΤ.',
            'ΗΜ/ΝΙΑ', 'ΠΕΡΙΓΡΑΦΗ', 'ΚΑΘΑΡΗ ΑΞΙΑ', 'ΦΠΑ', 'ΤΕΛΙΚΗ ΑΞΙΑ',
            'ΜΑΡΚ', 'ΟΝΟΜΑ ΑΡΧΕΙΟΥ', 'ΣΧΕΤ. ΠΑΡΑΣΤ.', 'ΠΑΡΑΤΗΡΗΣΕΙΣ', 
            'ΦΟΡΤΩΣΗ', 'ΠΡΟΟΡΙΣΜΟΣ', 'Κ.Δ.', 'SERIAL' 
        ]
        
        existing_left = [c for c in left_cols if c in df.columns]
        existing_dynamic = [c for c in df.columns if c not in left_cols]
        final_order = existing_left + existing_dynamic
        
        df = df[final_order]
        df = df.fillna("")
        
        try:
            df.to_excel(path, index=False)
            self.log(f"🎉 Το Excel αποθηκεύτηκε: {path}")
            messagebox.showinfo("Ολοκληρώθηκε", f"Το αρχείο δημιουργήθηκε:\n{path}")
        except PermissionError:
            messagebox.showerror("Σφάλμα", "Κλείσε το αρχείο Excel! Είναι ανοιχτό.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()