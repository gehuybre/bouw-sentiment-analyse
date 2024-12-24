import json
import os
from google.cloud import language_v1
from google.cloud.language_v1 import types
from datetime import datetime

def analyze_sentiment(text, language_code):
    """
    Analyseert het sentiment van een tekst met de Google Cloud Natural Language API.

    Args:
        text: De te analyseren tekst.

    Returns:
        Een Sentiment object met score en magnitude.
    """
    client = language_v1.LanguageServiceClient()
    document = types.Document(content=text, type_=types.Document.Type.PLAIN_TEXT, language=language_code)

    try:
        response = client.analyze_sentiment(request={"document": document})
        sentiment = response.document_sentiment
        return sentiment
    except Exception as e:
        print(f"Error during sentiment analysis: {e}")
        return None

def load_prepared_data(filename="prepared_data.json"):
    """Laadt de voorbereide data uit het JSON-bestand."""
    filepath = os.path.join("data", "processed", filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_sentiment_results(data, filename="sentiment_results.json"):
    """Slaat de resultaten van de sentimentanalyse op in een JSON-bestand."""
    filepath = os.path.join("data", "processed", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    
    with open("config.json") as config_file:
        config = json.load(config_file)
    
    prepared_data = load_prepared_data()
    results_with_sentiment = []

    for item in prepared_data:
        language_code = 'nl'
        sentiment_title = analyze_sentiment(item["title"], language_code)
        sentiment_snippet = analyze_sentiment(item["snippet"], language_code)
        
        search_date = datetime.strptime(item["search_date"], "%Y-%m-%d")
        formatted_date = search_date.strftime("%Y-%m-%d")

        result = {
            "date": formatted_date,
            "title": item["title"],
            "snippet": item["snippet"],
            "link": item["link"],
            "search_term": item["search_term"],
            "source_site": item["source_site"],
            "sentiment_title_score": sentiment_title.score if sentiment_title else None,
            "sentiment_title_magnitude": sentiment_title.magnitude if sentiment_title else None,
            "sentiment_snippet_score": sentiment_snippet.score if sentiment_snippet else None,
            "sentiment_snippet_magnitude": sentiment_snippet.magnitude if sentiment_snippet else None,
        }
        results_with_sentiment.append(result)

    save_sentiment_results(results_with_sentiment)