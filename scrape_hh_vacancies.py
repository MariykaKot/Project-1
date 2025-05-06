#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Собирает вакансии 'Data Scientist' в Москве через публичное API hh.ru
и сохраняет их в data/processed/hh_data_scientist_msk.csv
"""

import os, csv, time, random, requests
from datetime import datetime

SEARCH_TEXT = "data scientist"
AREA_ID     = "1"          # Москва
PAGES       = 5            # 0…4 → 5 страниц
PER_PAGE    = 50           # максимум, итого ≤ 250 записей
OUTFILE     = "data/processed/hh_data_scientist_msk.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0 Safari/537.36"
    )
}
API_ENDPOINT = "https://api.hh.ru/vacancies"

os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
session = requests.Session()
session.headers.update(HEADERS)

rows = []
for page in range(PAGES):
    params = {
        "text": SEARCH_TEXT,
        "area": AREA_ID,
        "page": page,
        "per_page": PER_PAGE,
        "only_with_salary": False,
    }
    resp = session.get(API_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for item in data["items"]:
        salary = item["salary"]
        rows.append({
            "title":   item["name"],
            "company": item["employer"]["name"] if item.get("employer") else "",
            "salary_from": salary["from"] if salary else None,
            "salary_to":   salary["to"]   if salary else None,
            "salary_currency": salary["currency"] if salary else None,
            "schedule": item.get("schedule", {}).get("name", ""),
            "experience": item.get("experience", {}).get("name", ""),
            "published_at": item["published_at"],
            "url": item["alternate_url"],
            "page": page,
            "scrape_ts": datetime.now().isoformat(timespec="seconds")
        })

    print(f"Страница {page+1}/{PAGES} → {len(data['items'])} вакансий")
    time.sleep(random.uniform(1.0, 2.0))

# --- сохраняем CSV -----------------------------------------------
if rows:
    with open(OUTFILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"\n✅  Saved {len(rows)} vacancies → {OUTFILE}")
else:
    print("API не вернуло ни одной вакансии. Проверьте параметры запроса или соединение.")
