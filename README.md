# Readmit-Test
# 🏫 DePaul SIS Automation: Student Records & Service Indicators Scraper

Automates data collection from DePaul's **Campus Connect (PeopleSoft)** using **Selenium**.  
This script logs in once (manually), then iterates through a CSV of Student IDs to extract:

- **Academic Term History** → *Current GPA*
- **Program/Plan** → *Status, Effective Date, Program Action, Action Reason, Academic Program, Academic Plan*
- **Service Indicators** → *Code, Description, Reason, Start Date*

> ✅ Outcome: Reduced manual lookups by ~**60%** for large student batches.

---

## 🚀 Features

- 🔐 **Single sign-on**: you log in manually once; the script handles the rest
- 🧭 **Robust navigation** across multiple PeopleSoft pages (Term History, Program/Plan, Service Indicators)
- ⏳ **Smart waits** with `WebDriverWait` (fewer brittle sleeps)
- 🧼 **Input cleaning**: handles BOM/odd characters in CSV (e.g., `\ufeff`, `�`)
- 📝 **CSV output** with stable column order (ready for analysis/import)
- 🧩 **PeopleSoft‑friendly**: preserves `#ICSearch` button selector convention (as preferred)

---

## 🗂 Project Structure

```text
sis-automation/
│
├── scraper.py                # Main script (the one in this README)
├── student_data.csv          # Input list of Student IDs (one per line)
├── readmit.csv               # Output file with results
└── README.md                 # This file
```

---

## 🧰 Requirements

- **Python** 3.9+
- **Google Chrome** (latest) and matching **ChromeDriver** (auto-managed)
- **Packages** (install with `pip install -r requirements.txt`):
  - `selenium`
  - `webdriver-manager`
  - `pandas` (optional; not required by the base script but useful for QA)
  - `python-dotenv` (optional)

**Example `requirements.txt`:**
```txt
selenium>=4.23.1
webdriver-manager>=4.0.2
pandas>=2.2.2
python-dotenv>=1.0.1
```

---

## 🔑 Setup

1. **Clone** or copy the repo contents locally.
2. **Create** your input CSV (one student ID per line) at:
   ```text
   /Users/<you>/Documents/python/readmit/student_data.csv
   ```
   *The script expects this path; adjust in code if needed.*
3. (Optional) Create a virtual env and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

---

## 🔧 Configuration

Paths used in the script (adjust if desired):
```python
students = load_students('/Users/rakulsk/Documents/python/readmit/student_data.csv')
output_path = '/Users/rakulsk/Documents/python/readmit/readmit.csv'
```
Chromedriver is auto-installed and kept up to date via `webdriver_manager`.

To run in **headless** mode, add before creating the driver:
```python
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
```

---

## ▶️ Usage

1. **Run the script**:
   ```bash
   python scraper.py
   ```

2. When the login page opens, **log in manually** to Campus Connect:
   - URL (auto): `https://campusconnect.depaul.edu/psp/CSPRD92/?cmd=login`
   - After successful login, **return to the console** and press **Enter** to continue.

3. The script will iterate over your `student_data.csv`, navigating to:
   - **Term History** → gets **GPA**
   - **Program/Plan** → gets **Status**, **Effective Date**, **Program Action**, **Action Reason**, **Academic Program**, **Academic Plan**
   - **Service Indicators** → captures **Code**, **Description**, **Reason**, **Active Date**

4. Results are written to:
   ```text
   /Users/<you>/Documents/python/readmit/readmit.csv
   ```

---

## 📄 Input / Output

### Input: `student_data.csv`
- Format: **one Student ID per line**
- Example:
  ```csv
  1234567
  9998888
  1002003
  ```

### Output: `readmit.csv`
- Primary rows (from Term History + Program/Plan):
  ```csv
  Student ID,GPA,Status,Effective Date,Program Action,Action Reason,Academic Program,Academic Plan
  1234567,3.61,Active,2024-09-01,PRGC,ADM,LAUG,Undergraduate – Data Science
  ```

- Followed by **Service Indicator** rows per student (same CSV), for easy grouping:
  ```csv
  1234567,SI_CODE,SI_DESCRIPTION,REASON_DESCRIPTION,ACTIVE_DATE
  1234567,XW,Financial Hold,Past Due,2024-08-15
  1234567,AD,Advising Required,New Admit,2024-09-01
  ```

> Note: Service indicator rows are written after each student's main row(s), reusing `Student ID` in column 1 for easy joins.

---

## 🧩 Key Implementation Notes

- **Selectors**: this project **intentionally keeps** the PeopleSoft **`#ICSearch`** button ID, per team preference.
- **Frames**: Campus Connect pages often require switching into `ptifrmtgtframe`:
  ```python
  wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ptifrmtgtframe")))
  ```
- **Resilience**: helper `safe_get_text()` returns `"N/A"` for missing elements to avoid crashes.
- **Pagination / Tables**: Service Indicator rows are scraped with a simple index loop until `NoSuchElementException` ends the loop.

---

## 🛡️ Security & Compliance

- The script **does not** store credentials.
- You **log in manually**; the session cookie is used only while the browser remains open.
- Treat all outputs as **FERPA-protected** where applicable. Secure/limit access to `readmit.csv`.

---

## 🧪 Troubleshooting

- **Blank values** or **timeouts**:
  - Ensure the iframe switch to `ptifrmtgtframe` succeeded.
  - Increase waits: `WebDriverWait(browser, 45)`.
- **Login loops**:
  - Complete DUO/SSO steps fully before pressing Enter.
- **UI changes**:
  - PeopleSoft upgrades may change element IDs slightly; re-check selectors like `STDNT_SRCH_EMPLID`, `ACAD_PROG_*`, or `SRVC_IND_*`.
- **Keeps clicking wrong things**:
  - Consider scoping with more specific locators and adding `scrollIntoView` via JS.

---

## 📈 Impact

- Reduced manual processing time by **~60%** for large student cohorts.
- Standardized output simplifies downstream import/analysis and audit.

---

## ✅ Roadmap / Ideas

- [ ] Write service indicators to a **separate CSV** with explicit headers
- [ ] Add **retry/backoff** for transient load errors
- [ ] Optional **headless** mode toggle via CLI arg (e.g., `--headless`)
- [ ] Add **structured logs** (CSV/JSON) for failures and durations
- [ ] Build a small **Streamlit dashboard** to upload input list and download results

---

## 📜 License

MIT © 2025 Rakul Senthilkumar
