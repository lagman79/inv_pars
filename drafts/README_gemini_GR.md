# AI Invoice Extractor

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue" alt="Python Version">
  <img src="https://img.shields.io/badge/Gemini_API-2.5%20Flash-green" alt="Gemini API">
  <img src="https://img.shields.io/badge/GUI-Tkinter-yellow" alt="Tkinter GUI">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey" alt="Platform">
</p>

> 🇬🇧 **English Version:** For the English documentation, click [here](README.md).

Το **AI Invoice Extractor** είναι μία εφαρμογή με γραφικό περιβάλλον (GUI) για την αυτοματοποιημένη εξαγωγή δεδομένων από ψηφιακά παραστατικά (PDF, JPG, PNG) με χρήση του **Google Gemini AI**. Τα δεδομένα εξάγονται οργανωμένα σε **Excel**.

---

## 🛠️ Εγκατάσταση & Ρύθμιση

### 1. Εγκατάσταση Βιβλιοθηκών
Κατεβάστε τον κώδικα και εγκαταστήστε τα απαραίτητα:

```bash
pip install pandas google-generativeai openpyxl tkinter pillow
```

### 2. Απόκτηση Gemini API Key
Η εφαρμογή απαιτεί κλειδί API.

1. Μπείτε στο [Google AI Studio](https://aistudio.google.com/).
2. Δημιουργήστε ένα νέο API Key.
3. Θα το εισάγετε στην εφαρμογή κατά την εκκίνηση.

---

## 💡 Δυνατότητες

* **Εξαγωγή Δεδομένων:** Ημερομηνία, Προμηθευτής, ΑΦΜ, Ποσά, MARK Code, Serial Numbers κ.ά.
* **Κατηγοριοποίηση ΕΣΠΑ:** Αυτόματη ταξινόμηση δαπανών (π.χ. "Πράσινη Παραγωγική Επένδυση").
* **Οργάνωση Αρχείων:** Αυτόματη μετονομασία (`Προμηθευτής_ΑρΠαραστατικού`) και ταξινόμηση σε φακέλους.

---

## ⚙️ Οδηγίες Χρήσης

### Βήμα 1: Βασικές Ρυθμίσεις
* **Gemini API Key:** Εισάγετε το κλειδί.
* **Φάκελος Εισαγωγής:** Επιλέξτε τον φάκελο με τα παραστατικά.
* **Αποθήκευση Excel:** Επιλέξτε φάκελο εξόδου.

<p align="center"><img src="screenshots/2. api.png" alt="API" width="600"/></p>
<p align="center"><img src="screenshots/3. φάκελος εισαγωγής.png" alt="Φάκελος" width="600"/></p>

### Βήμα 2: Παράμετροι
* **Πρόγραμμα ΕΣΠΑ:** Επιλέξτε για αυτόματη κατηγοριοποίηση (Κ.Δ.).
* **Full Extract:** Ενεργοποιήστε για εξαγωγή όλων των πεδίων (δυναμικά).

<p align="center"><img src="screenshots/4 ρυθμίσεις - οργάνωση.png" alt="Ρυθμίσεις" width="600"/></p>

### Βήμα 3: Εκτέλεση
Πατήστε **"🚀 ΕΚΚΙΝΗΣΗ"**.
* Παρακολουθήστε την εξέλιξη από την μπάρα προόδου και τα logs.
* Αν επιλεγεί, τα αρχεία θα μετονομαστούν και θα ταξινομηθούν αυτόματα.

<p align="center"><img src="screenshots/5 progress bars & logs.png" alt="Logs" width="600"/></p>

### Βήμα 4: Ολοκλήρωση
Το Excel ανοίγει αυτόματα.
* **Νέα Εργασία:** Καθαρισμός για νέα εκκίνηση.
* **Έξοδος:** Κλείσιμο εφαρμογής.

<p align="center"><img src="screenshots/1. κεντρικό GUI.jpg" alt="GUI" width="600"/></p>
<p align="center"><img src="screenshots/6 start_new task & exit buttons.png" alt="Buttons" width="400"/></p>

---

## 🚨 Αντιμετώπιση Προβλημάτων

| Σφάλμα | Λύση |
| :--- | :--- |
| **API Key Error** | Ελέγξτε αν το κλειδί είναι ενεργό στο Google AI Studio. |
| **429 Too Many Requests** | Πολλά αιτήματα. Περιμένετε λίγο και ξαναδοκιμάστε. |
| **PermissionError** | **Κλείστε το Excel** αν είναι ανοιχτό. |