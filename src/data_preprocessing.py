import json
import re
from fuzzywuzzy import fuzz
import os

def load_data(filename="search_results.json"):
    """Laadt de ruwe data uit het JSON-bestand."""
    filepath = os.path.join("data", "raw", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def clean_text(text):
    """
    Verwijdert HTML tags, speciale tekens en zet om naar kleine letters.
    """
    text = re.sub(r"<.*?>", "", text)  # Verwijder HTML tags
    text = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", text)  # Houd alleen letters en spaties
    text = text.lower()
    return text

def remove_duplicates(data, title_similarity_threshold=90):
    """
    Verwijdert duplicaten op basis van URL en titelsimilariteit.

    Args:
        data: Lijst met artikelen (dicts).
        title_similarity_threshold: Drempelwaarde voor titelsimilariteit (0-100).

    Returns:
        Lijst met unieke artikelen.
    """
    unique_articles = []
    seen_urls = set()
    seen_titles = set()

    for item in data:
        url = item.get("link", "")
        title = clean_text(item.get("title", ""))

        # URL check
        if url in seen_urls:
            continue

        # Title similarity check
        is_duplicate = False
        for seen_title in seen_titles:
            similarity_ratio = fuzz.ratio(title, seen_title)
            if similarity_ratio >= title_similarity_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_articles.append(item)
            seen_urls.add(url)
            seen_titles.add(title)

    return unique_articles

def prepare_data(data):
    """
    Bereidt de data voor voor sentimentanalyse.
    """
    cleaned_data = []
    for item in data:
        cleaned_item = {
            "title": clean_text(item.get("title", "")),
            "snippet": clean_text(item.get("snippet", "")),
            "link": item.get("link", ""),
            "search_term": item.get("search_term", ""),
            "search_date": item.get("search_date", ""),
            "source_site": item.get("source_site", ""),
        }
        cleaned_data.append(cleaned_item)
    return cleaned_data

def save_prepared_data(data, filename="prepared_data.json"):
    """Slaat de voorbereide data op in een JSON-bestand."""
    filepath = os.path.join("data", "processed", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    raw_data = load_data()
    unique_data = remove_duplicates(raw_data)
    prepared_data = prepare_data(unique_data)
    save_prepared_data(prepared_data)