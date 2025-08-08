from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, pandas as pd

options = Options()
options.add_argument("--lang=id")  # Run in headless mode
options.add_argument("accept-language=id-ID,id")
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

driver.get("https://www.google.com/maps/place/Kantor+Pos+Denpasar/@-8.672505,115.1470464,12z/data=!4m10!1m2!2m1!1skantor+pos+denpasar!3m6!1s0x2dd2405455555519:0xec56c4b56ea2c101!8m2!3d-8.6725138!4d115.2294483!15sChNrYW50b3IgcG9zIGRlbnBhc2FyIgOIAQFaFSITa2FudG9yIHBvcyBkZW5wYXNhcpIBC3Bvc3Rfb2ZmaWNlqgFnCg0vZy8xMWM1OW50NG4zCgovbS8wOWdnemhnEAEqDiIKa2FudG9yIHBvcygmMh8QASIbm9BZYAikiV1z6e5uCbWwS8Ibb-fxCQ7VjNbcMhcQAiITa2FudG9yIHBvcyBkZW5wYXNhcuABAA!16s%2Fg%2F1thrgbr6?entry=ttu&g_ep=EgoyMDI1MDgwMy4wIKXMDSoASAFQAw%3D%3D")
time.sleep(5)

try :
    nama_tempat = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
except :
    nama_tempat = "Tidak ditemukan"

try :
    driver.find_element(By.XPATH,
                        "//span[contains(text(), 'Ulasan lainnya') or contains(text(), 'More reviews')]/ancestor::button").click()
    time.sleep(3)
except :
    pass

reviews, seen = [], set()

while len(reviews) < 5:
    for c in driver.find_elements(By.CSS_SELECTOR, "div.jftiEf"):
       user_el = c.find_element(By.CLASS_NAME, "d4r55")
       review_el = c.find_element(By.CLASS_NAME, "wiI7pd")
       rating_el = c.find_element(By.CLASS_NAME, "kvMYJc")

       if not review_el or not review_el.text.strip():
           continue

       user = user_el.text if user_el else "Tidak ditemukan"
       review = review_el.text.strip()
       rating = rating_el.get_attribute("aria-label").split()[0] if rating_el else "Tidak ditemukan"

       if (user, review) not in seen:
           seen.add((user, review))
           reviews.append({
                "nama_tempat": nama_tempat,
                "user": user,
                "review": review,
                "rating": rating
           })
    try :
        driver.execute_script("arguments[0].scrollIntoView();", driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")[-1])
    except:
        break
    time.sleep(2)

pd.DataFrame(reviews).to_csv("data/ws.csv", index=False)
print(f'INFO{len(reviews)} ulasan ditemukan untuk reviews.csv')
driver.quit()