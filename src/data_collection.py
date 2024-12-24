import requests
import json
import time
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build

def collect_data(api_key, cse_id, search_terms, start_date, end_date, site):
    """
    Verzamelt data via de Google Search API.

    Args:
        api_key: Google Search API key.
        cse_id: Custom Search Engine ID.
        search_terms: Lijst met zoektermen.
        start_date: Startdatum (YYYY-MM-DD).
        end_date: Einddatum (YYYY-MM-DD).

    Returns:
        Een lijst met zoekresultaten (JSON).
    """

    service = build("customsearch", "v1", developerKey=api_key)

    all_results = []

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    for term in search_terms:
        current_date = start_date
        while current_date <= end_date:
            month_delta = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month) + 1
            try:
                res = service.cse().list(
                    q=term,
                    cx=cse_id,
                    siteSearch=site,
                    lr='lang_nl',
                    dateRestrict=f'm{month_delta}',
                    num=10,
                ).execute()

                if "items" in res:
                    for item in res["items"]:
                        item['search_term'] = term
                        item['search_date'] = current_date.strftime("%Y-%m-%d")
                        item['source_site'] = site
                        all_results.extend(res["items"])

                time.sleep(1) # Respecteer de API limieten

            except Exception as e:
                print(f"Error for {term} on {current_date.strftime('%Y-%m')}: {e}")

            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

    return all_results

def save_results(results, filename="search_results.json"):
    """Slaat de zoekresultaten op in een JSON-bestand."""
    filepath = os.path.join("data", "raw", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    with open("config.json") as config_file:
        config = json.load(config_file)

    all_search_results = []
    for source in config["data_sources"]:
        search_results = collect_data(
            config["google_search_api_key"],
            config["cse_id"],
            config["search_terms"],
            config["start_date"],
            config["end_date"],
            source['site'],
        )
        all_search_results.extend(search_results)

    save_results(all_search_results)