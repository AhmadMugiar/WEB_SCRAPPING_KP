from google_play_scraper import reviews, Sort
import pandas as pd

def scrape_playstore_reviews(app_id, lang='id', count=800, sort=Sort.NEWEST):
    try:
        result, _ = reviews(
            app_id,
            lang=lang,
            count=count,
            sort=sort
        )
        df = pd.DataFrame([{
            'User': r.get('userName'),
            'Rate': r.get('score'),
            'Reviews': r.get('content'),
            'Tanggal Reviews': r.get('at')
        } for r in result])
        return df
    except Exception as e:
        print('Error:', e)
        return pd.DataFrame()