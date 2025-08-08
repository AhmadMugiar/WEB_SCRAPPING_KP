from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time, pandas as pd
import os

# Setup
options = Options()
options.add_argument("--lang=id")
options.add_argument("accept-language=id-ID,id")
options.add_argument("--start-maximized")  # maximize window
driver = webdriver.Chrome(options=options)

# URL Google Maps tempat
driver.get("https://www.google.com/maps/place/Kantor+Pos+Denpasar/@-8.672505,115.1470464,12z/data=!4m12!1m2!2m1!1skantor+pos+denpasar!3m8!1s0x2dd2405455555519:0xec56c4b56ea2c101!8m2!3d-8.6725138!4d115.2294483!9m1!1b1!15sChNrYW50b3IgcG9zIGRlbnBhc2FyIgOIAQFaFSITa2FudG9yIHBvcyBkZW5wYXNhcpIBC3Bvc3Rfb2ZmaWNlqgFnCg0vZy8xMWM1OW50NG4zCgovbS8wOWdnemhnEAEqDiIKa2FudG9yIHBvcygmMh8QASIbm9BZYAikiV1z6e5uCbWwS8Ibb-fxCQ7VjNbcMhcQAiITa2FudG9yIHBvcyBkZW5wYXNhcuABAA!16s%2Fg%2F1thrgbr6?entry=ttu")
time.sleep(5)

# Ambil nama tempat
try:
    nama_tempat = driver.find_element(By.CLASS_NAME, "DUwDvf").text.strip()
except:
    nama_tempat = "Unknown"

# Klik tombol "Ulasan lainnya"
try:
    review_button = driver.find_element(
        By.XPATH, "//span[contains(text(), 'Ulasan lainnya') or contains(text(), 'More reviews')]/ancestor::button"
    )
    driver.execute_script("arguments[0].click();", review_button)
    time.sleep(3)
except:
    print("Tombol 'Ulasan lainnya' tidak ditemukan")

# Scroll dan ambil ulasan
reviews, seen = [], set()

try:
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf')
except:
    print("Gagal menemukan container ulasan")
    driver.quit()
    exit()

scroll_count = 0
max_scrolls = 30

while len(reviews) < 100 and scroll_count < max_scrolls:
    elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
    print(f"Scroll ke-{scroll_count+1}: {len(elements)} ulasan ditemukan di halaman.")
    
    for c in elements:
        try:
            user_el = c.find_element(By.CLASS_NAME, "d4r55")
            review_el = c.find_element(By.CLASS_NAME, "wiI7pd")
            rating_el = c.find_element(By.CLASS_NAME, "kvMYJc")

            if not review_el or not review_el.text.strip():
                continue

            user = user_el.text.strip() if user_el else "Tidak ditemukan"
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
        except:
            continue

    # Scroll down
    try:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
    except Exception as e:
        print("Gagal scroll:", e)
        break

    scroll_count += 1
    time.sleep(2)

# Simpan ke CSV
if not os.path.exists("data"):
    os.makedirs("data")

df = pd.DataFrame(reviews)
df.to_csv("data/reviews_posdenpasar.csv", index=False, encoding="utf-8-sig")
print(f'\n✅ DONE: {len(reviews)} ulasan berhasil disimpan ke data/reviews_posdenpasar.csv')

driver.quit()