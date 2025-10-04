import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Setup ===
options = Options()
options.add_argument("--start-maximized")
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(browser, 30)

# === Helpers ===
def load_students(filepath):
    students = []
    with open(filepath, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            clean_id = row[0].strip().replace('\ufeff', '').replace('�', '')
            students.append(clean_id)
    return students

def safe_get_text(by, value, attr="text"):
    try:
        elem = browser.find_element(by, value)
        return elem.text.strip() if attr == "text" else elem.get_attribute(attr).strip()
    except:
        return "N/A"

def scrape_service_indicators(student_id):
    try:
        browser.get("https://campusconnect.depaul.edu/psp/CSPRD92/EMPLOYEE/SA/c/MAINTAIN_SERVICE_INDICATORS.ACTIVE_SRVC_INDICA.GBL")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ptifrmtgtframe")))

        sid_input = wait.until(EC.presence_of_element_located((By.ID, "PEOPLE_SRCH_EMPLID")))
        sid_input.clear()
        sid_input.send_keys(student_id)
        sid_input.send_keys(Keys.TAB)
        time.sleep(0.5)

        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "#ICSearch")))
        search_btn.click()
        wait.until(EC.presence_of_element_located((By.ID, "SRVC_IND_SEL_VW$scroll$0")))

        rows = []
        i = 0
        while True:
            try:
                code = browser.find_element(By.ID, f"SRVC_IND_CODE${i}").text.strip()
                code_descr = browser.find_element(By.ID, f"CODE_DESCR${i}").text.strip()
                reason_descr = browser.find_element(By.ID, f"REASON_DESCR${i}").text.strip()
                start_date = browser.find_element(By.ID, f"SRVC_IND_SEL_VW_SRVC_IND_ACTIVE_DT${i}").text.strip()
                rows.append([student_id, code, code_descr, reason_descr, start_date])
                i += 1
            except:
                break

        return rows
    except Exception as e:
        print(f"⚠️ Could not fetch service indicators for {student_id}: {e}")
        return [[student_id, "ERROR", "", "", ""]]

# === Load Data ===
students = load_students('/Users/rakulsk/Documents/python/readmit/student_data.csv')

# === Output CSV Setup ===
output_path = '/Users/rakulsk/Documents/python/readmit/readmit.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

output_file = open(output_path, mode='w', newline='')
writer = csv.writer(output_file)
writer.writerow([
    'Student ID', 'GPA', 'Status', 'Effective Date',
    'Program Action', 'Action Reason', 'Academic Program', 'Academic Plan'
])

# === Log in First ===
browser.get("https://campusconnect.depaul.edu/psp/CSPRD92/?cmd=login")
input("⏸️ Log in manually, then press Enter to continue...")

# === Process All Students ===
for student_id in students:
    try:
        print(f"\n🔍 Searching student: {student_id}")

        # Navigate to Term History
        browser.get("https://campusconnect.depaul.edu/psp/CSPRD92/EMPLOYEE/SA/c/MANAGE_ACADEMIC_RECORDS.TERM_HISTORY.GBL")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ptifrmtgtframe")))

        id_input = wait.until(EC.presence_of_element_located((By.ID, "STDNT_SRCH_EMPLID")))
        id_input.clear()
        id_input.send_keys(student_id)
        id_input.send_keys(Keys.TAB)
        time.sleep(1)

        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "#ICSearch")))
        search_btn.click()

        gpa_span = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[id^='STDNT_CAR_TERM_CUR_GPA']")))
        gpa_value = gpa_span.text.strip()
        print(f"✅ GPA: {gpa_value}")

        return_btn = wait.until(EC.element_to_be_clickable((By.ID, "#ICList")))
        return_btn.click()
        wait.until(EC.presence_of_element_located((By.ID, "STDNT_SRCH_EMPLID")))

        # === Program/Plan Page ===
        browser.get("https://campusconnect.depaul.edu/psp/CSPRD92/EMPLOYEE/SA/c/TRACK_STUDENT_CAREERS.ACAD_PLAN.GBL")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ptifrmtgtframe")))

        prog_input = wait.until(EC.presence_of_element_located((By.ID, "STDNT_CAR_SRCH_EMPLID")))
        prog_input.clear()
        prog_input.send_keys(student_id)
        prog_input.send_keys(Keys.TAB)
        time.sleep(1)

        prog_search_btn = wait.until(EC.element_to_be_clickable((By.ID, "#ICSearch")))
        prog_search_btn.click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[id^='PSXLATITEM_XLATLONGNAME']")))
        time.sleep(2)

        status = safe_get_text(By.CSS_SELECTOR, "span[id^='PSXLATITEM_XLATLONGNAME']")
        eff_date = safe_get_text(By.ID, "ACAD_PROG_EFFDT$0", attr="value")
        prog_action = safe_get_text(By.ID, "ACAD_PROG_PROG_ACTION$0", attr="value")
        reason = safe_get_text(By.ID, "ACAD_PROG_PROG_REASON$0", attr="value")
        program = safe_get_text(By.ID, "ACAD_PROG_ACAD_PROG$0", attr="value")

        try:
            tab_link = wait.until(EC.element_to_be_clickable((By.ID, "ICTAB_1")))
            tab_link.click()
            wait.until(EC.presence_of_element_located((By.ID, "ACAD_PLAN_TBL_DESCR$0")))
            time.sleep(1)
            academic_plan = safe_get_text(By.ID, "ACAD_PLAN_TBL_DESCR$0")
        except:
            academic_plan = "N/A"

        print(f"📋 Status: {status}, Effective: {eff_date}, Action: {prog_action}, Reason: {reason}, Program: {program}, Plan: {academic_plan}")
        writer.writerow([student_id, gpa_value, status, eff_date, prog_action, reason, program, academic_plan])

        # === Service Indicators ===
        service_rows = scrape_service_indicators(student_id)
        for row in service_rows:
            writer.writerow(row)

    except Exception as e:
        print(f"❌ Error with {student_id}: {e}")
        writer.writerow([student_id, "ERROR", "", "", "", "", "", ""])
        continue

output_file.close()
browser.quit()
print(f"\n🎉 Done! Check: {output_path}")
