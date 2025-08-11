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
driver.get("https://www.google.com/maps/place/Kantor+Pos+Fatmawati/@-6.2945288,106.7947741,17z/data=!4m16!1m9!3m8!1s0x2e69f19684fb0151:0xb0b69f82cb32571a!2sKantor+Pos+Fatmawati!8m2!3d-6.2945288!4d106.7947741!9m1!1b1!16s%2Fg%2F11dfj2fyrd!3m5!1s0x2e69f19684fb0151:0xb0b69f82cb32571a!8m2!3d-6.2945288!4d106.7947741!16s%2Fg%2F11dfj2fyrd?entry=ttu&g_ep=EgoyMDI1MDgwNS4wIKXMDSoASAFQAw%3D%3D")
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
                time.sleep(0.2)
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
df_maps.to_csv("data/ULASAN_POS_JAKARTAFLORA.csv", index=False, encoding="utf-8-sig")
print(f'\n✅ DONE: {len(reviews_list)} ulasan berhasil disimpan.')

driver.quit()
