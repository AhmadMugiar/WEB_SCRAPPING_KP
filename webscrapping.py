from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, pandas as pd
import os

# Setup Selenium
options = Options()
options.add_argument("--lang=id")
options.add_argument("accept-language=id-ID,id")
options.add_argument("--start-maximized")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless')  
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)

# URL lokasi Google Maps
driver.get("https://www.google.com/maps/place/Kantor+Pos+Banjarbaru/@-3.4404911,114.7423452,13z/data=!4m10!1m2!2m1!1sKCU+Pos+BanjarBARU!3m6!1s0x2de68171e5ef9d2b:0x5645719060616bdc!8m2!3d-3.4394242!4d114.8329991!15sChJLQ1UgUG9zIEJhbmphckJBUlVaFCISa2N1IHBvcyBiYW5qYXJiYXJ1kgELcG9zdF9vZmZpY2WaASNDaFpEU1VoTk1HOW5TMFZKUTBGblNVUklPRTUxWkdGUkVBRaoBUgoIL20vMGRoOHMQASoLIgdrY3UgcG9zKCYyHxABIhsC10eXsbJ_573D2rGAAmKEe4cveGehXrZQXdwyFhACIhJrY3UgcG9zIGJhbmphcmJhcnXgAQD6AQQIABAy!16s%2Fg%2F11b5ymcg9k?entry=ttu&g_ep=EgoyMDI1MDgwNi4wIKXMDSoASAFQAw%3D%3D")
time.sleep(5)

# Ambil nama tempat
try:
    place_name = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
except:
    place_name = "Unknown"

# Klik tombol "Ulasan lainnya"
try:
    review_button = driver.find_element(
        By.XPATH, "//span[contains(text(), 'Ulasan lainnya') or contains(text(), 'Lainnya')]/ancestor::button"
    )
    driver.execute_script("arguments[0].click();", review_button)
    time.sleep(8)
except:
    print("Tombol ulasan tidak ditemukan.")

# Scroll & ambil container ulasan
try:
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
except:
    print("Gagal menemukan container ulasan")
    driver.quit()
    exit()

reviews_list, seen = [], set()
scroll_count = 0
max_scrolls = 30

while len(reviews_list) < 500 and scroll_count < max_scrolls:
    elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    print(f"Scroll ke-{scroll_count+1}: {len(elements)} ulasan ditemukan.")

    # Klik semua tombol "Lainnya"
    try:
        more_buttons = driver.find_elements(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')
        for btn in more_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
            except:
                continue
    except:
        pass

    # Ambil data ulasan
    for c in elements:
        try:
            user_el = c.find_element(By.CLASS_NAME, "d4r55")
            review_el = c.find_element(By.CLASS_NAME, "wiI7pd")
            rating_el = c.find_element(By.CLASS_NAME, "kvMYJc")
            date_el = c.find_element(By.CLASS_NAME, "rsqaWe")

            if not review_el or not review_el.text.strip():
                continue

            user = user_el.text.strip() if user_el else "Tidak ditemukan"
            review = review_el.text.strip()
            rating = rating_el.get_attribute("aria-label").split()[0] if rating_el else "Tidak ditemukan"
            date = date_el.text.strip() if date_el else "Tidak ditemukan"

            if (user, review) not in seen:
                seen.add((user, review))
                reviews_list.append({
                    "Pos Office Branch": place_name,
                    "User": user,
                    "Reviews": review,
                    "Rate": rating,
                    "Date": date
                })
        except:
            continue

    # Scroll ke bawah
    try:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    except Exception as e:
        print("Gagal scroll:", e)
        break

    scroll_count += 1
    time.sleep(2)


if not os.path.exists("data"):
    os.makedirs("data")

df_maps = pd.DataFrame(reviews_list)
df_maps.to_csv("Ulasan Google Maps/ULASAN_POS_KCBANJARBARU.csv", index=False, encoding="utf-8-sig")
print(f'\n✅ DONE: {len(reviews_list)} ulasan berhasil disimpan.')

driver.quit()
