import json
import time
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.colab import userdata

def collect_data(search_terms, start_date, end_date, site, max_queries):
    """
    Verzamelt data via de Google Search API.

    Args:
        search_terms: Lijst met zoektermen.
        start_date: Startdatum (YYYY-MM-DD).
        end_date: Einddatum (YYYY-MM-DD).
        site: De website waarop gezocht moet worden.
        max_queries: Het maximale aantal queries dat uitgevoerd mag worden.

    Returns:
        Een lijst met zoekresultaten (JSON).
    """

    # Gebruik de geheimen uit Google Colab
    api_key = userdata.get('GOOGLE_SEARCH_API_KEY')
    cse_id = userdata.get('CSE_ID')

    service = build("customsearch", "v1", developerKey=api_key)

    all_results = []
    query_count = 0

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    for term in search_terms:
        current_date = start_date
        while current_date <= end_date:
            month_delta = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month) + 1
            try:
                if query_count >= max_queries:
                    print(f"Maximum aantal queries ({max_queries}) bereikt voor site {site}.")
                    return all_results
                
                res = service.cse().list(
                    q=term,
                    cx=cse_id,
                    siteSearch=site,
                    lr='lang_nl',
                    dateRestrict=f'm{month_delta}',
                    num=10,
                ).execute()

                query_count += 1

                if "items" in res:
                    for item in res["items"]:
                        item['search_term'] = term
                        item['search_date'] = current_date.strftime("%Y-%m-%d")
                        item['source_site'] = site
                        all_results.extend(res["items"])

                time.sleep(1)  # Respecteer de API limieten

            except Exception as e:
                print(f"Error for {term} on {current_date.strftime('%Y-%m')} on site {site}: {e}")

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
    # Laad configuratie uit config.json
    with open("config.json") as f:
        config = json.load(f)

    search_terms = config["search_terms"]
    start_date = config["start_date"]
    end_date = config["end_date"]
    data_sources = config["data_sources"]

    # Stel het maximum aantal queries in (voor testdoeleinden)
    max_queries_for_test = 1 # Voorbeeld

    all_search_results = []
    total_queries = 0
    for source in data_sources:
        site = source["site"]
        print(f"Zoeken op: {site}")
        search_results = collect_data(
            search_terms,
            start_date,
            end_date,
            site,
            max_queries_for_test - total_queries
        )
        all_search_results.extend(search_results)
        total_queries += max_queries_for_test

        if total_queries >= max_queries_for_test:
          print("Totaal aantal toegestane test queries bereikt.")
          break

    save_results(all_search_results)