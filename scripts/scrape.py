import csv
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://www.kidsplaceonline.com.br/alimentacao/cardapio"
CSV_PATH = "data/menu_history.csv"


def fetch_menu_html():
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    return r.text


def parse_menu(html):
    """
    Change this function according to the structure of the page.
    Example below uses simple div scanning.
    """

    soup = BeautifulSoup(html, "html.parser")

    menu_entries = []

    current_year = datetime.now().year

    # Example: find all blocks that contain daily menu info
    # Adjust these selectors according to the real HTML
    days = soup.select("div.day-block")

    for day in days:
        raw_date = day.select_one("div.date").get_text(strip=True)

        # Example converting "22/11" -> "2025-11-22"
        day_num, month_num = raw_date.split("/")
        full_date = datetime(current_year, int(month_num), int(day_num))

        # Example of meal types
        for meal_div in day.select("div.meal"):
            meal_type = meal_div.select_one("span.meal-title").get_text(strip=True)
            meal_text = meal_div.select_one("div.meal-desc").get_text(strip=True)

            menu_entries.append({
                "date": full_date.strftime("%Y-%m-%d"),
                "meal_type": meal_type,
                "meal_text": meal_text
            })

    return menu_entries


def load_existing_entries():
    if not os.path.exists(CSV_PATH):
        return set()

    existing = set()
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["date"], row["meal_type"], row["meal_text"])
            existing.add(key)
    return existing


def append_new_entries(new_entries):
    existing = load_existing_entries()

    with open(CSV_PATH, "a+", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "meal_type", "meal_text"])

        for e in new_entries:
            key = (e["date"], e["meal_type"], e["meal_text"])
            if key not in existing:
                writer.writerow(e)


def main():
    html = fetch_menu_html()
    menu_entries = parse_menu(html)
    append_new_entries(menu_entries)


if __name__ == "__main__":
    main()
