import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

# Settings
input_file = r"C:\GhostDrive_REBUILD\Everything_else\datasets\ghostdata_master\wikihow_scraped\topics_wikihow.txt"
output_file = r"C:\GhostDrive_REBUILD\Everything_else\datasets\ghostdata_master\wikihow_scraped\wikihow_scraped.jsonl"
sleep_between = 3  # seconds between queries to avoid being blocked
chunk_size = 2000  # max characters per chunk

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text, chunk_size):
    """Splits text into chunks of <= chunk_size characters."""
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:
            current_chunk += " " + word if current_chunk else word
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def scrape_wikihow(query):
    query_formatted = query.replace(" ", "+")
    search_url = f"https://www.wikihow.com/wikiHowTo?search={query_formatted}"

    res = requests.get(search_url)
    if res.status_code != 200:
        print(f"❌ Failed search for: {query}")
        return []

    soup = BeautifulSoup(res.content, "html.parser")
    first_result = soup.find("a", class_="result_link")

    if not first_result:
        print(f"❌ No result found: {query}")
        return []

    href = first_result.get("href")
    if href.startswith("http"):
        article_url = href
    else:
        article_url = "https://www.wikihow.com" + href

    print(f"✅ Found article: {article_url}")

    res_article = requests.get(article_url)
    if res_article.status_code != 200:
        print(f"❌ Failed to fetch article: {article_url}")
        return []

    soup_article = BeautifulSoup(res_article.content, "html.parser")
    steps = soup_article.find_all("div", class_="step")

    if not steps:
        print(f"❌ No steps found: {query}")
        return []

    step_texts = [clean_text(step.get_text(separator=" ", strip=True)) for step in steps]
    combined_steps = "\n".join(step_texts)

    # Chunk if needed
    chunks = chunk_text(combined_steps, chunk_size)
    records = []

    for idx, chunk in enumerate(chunks):
        instruction = query
        if len(chunks) > 1:
            instruction += f" (Part {idx + 1})"

        records.append({
            "instruction": instruction,
            "input": "",
            "output": chunk
        })

    return records

def main():
    if not os.path.exists(input_file):
        print(f"❌ Topics file not found: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        topics = [line.strip() for line in f if line.strip()]

    if not topics:
        print("❌ No topics found in file.")
        return

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    total = len(topics)
    saved_count = 0

    for idx, topic in enumerate(topics, start=1):
        print(f"\n[{idx}/{total}] Scraping: {topic}")

        results = scrape_wikihow(topic)

        if results:
            with open(output_file, "a", encoding="utf-8") as f_out:
                for record in results:
                    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    saved_count += 1

        time.sleep(sleep_between)

    print(f"\n✅ Finished batch scraping. Total saved records: {saved_count}")

if __name__ == "__main__":
    main()
