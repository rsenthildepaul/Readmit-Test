import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Setup ===
options = Options()
options.add_argument("--start-maximized")
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(browser, 20)

# === Go to Page ===
browser.get("https://campusconnect.depaul.edu/psp/CSPRD92/EMPLOYEE/SA/c/MAINTAIN_SERVICE_INDICATORS.ACTIVE_SRVC_INDICA.GBL")
input("⏸️ Log in manually, then press Enter to continue...")

# === Switch into iframe ===
wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ptifrmtgtframe")))
print("✅ Switched to iframe.")

# === Enter Student ID ===
student_id = "2054685"
id_box = wait.until(EC.presence_of_element_located((By.ID, "PEOPLE_SRCH_EMPLID")))
id_box.clear()
id_box.send_keys(student_id)
time.sleep(0.5)

# === Click Search Button ===
search_btn = wait.until(EC.element_to_be_clickable((By.ID, "#ICSearch")))
search_btn.click()
print("🔍 Clicked search.")

# === Wait for table to load ===
wait.until(EC.presence_of_element_located((By.ID, "SRVC_IND_SEL_VW$scroll$0")))
print("📋 Table loaded.")

# === Write to CSV ===
with open("/Users/rakulsk/Documents/python/readmit/testdata.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Student ID", "Code", "Code Description", "Reason Description", "Start Date"])

    i = 0
    while True:
        try:
            code = browser.find_element(By.ID, f"SRVC_IND_CODE${i}").text.strip()
        except:
            print(f"⚠️ No more rows or failed on row {i}")
            break

        try:
            description = browser.find_element(By.ID, f"CODE_DESCR${i}").text.strip()
        except:
            description = "N/A"
            print(f"⚠️ Could not find CODE_DESCR${i}")

        try:
            reason = browser.find_element(By.ID, f"REASON_DESCR${i}").text.strip()
        except:
            reason = "N/A"
            print(f"⚠️ Could not find REASON_DESCR${i}")

        try:
            start_date = browser.find_element(By.ID, f"SRVC_IND_SEL_VW_SRVC_IND_ACTIVE_DT${i}").text.strip()
        except:
            start_date = "N/A"
            print(f"⚠️ Could not find SRVC_IND_SEL_VW_SRVC_IND_ACTIVE_DT${i}")

        print(f"✅ Row {i} → Code: {code}, Desc: {description}, Reason: {reason}, Start: {start_date}")
        writer.writerow([student_id, code, description, reason, start_date])
        i += 1

print("✅ Done writing to CSV.")
browser.quit()
