import requests
from bs4 import BeautifulSoup
import sys
import re
import os
import time

scraped_topics = set()  # To avoid duplicates when scraping See Also pages

def clean_text(text):
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def scrape_wikipedia_page(topic):
    topic_formatted = topic.replace(" ", "_")

    if topic_formatted in scraped_topics:
        print(f"🔁 Already scraped: {topic_formatted}")
        return

    scraped_topics.add(topic_formatted)

    url = f"https://en.wikipedia.org/wiki/{topic_formatted}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch Wikipedia page: {url}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = '\n\n'.join([p.get_text() for p in paragraphs])
    cleaned = clean_text(text)

    output_dir = r"C:\GhostDrive_REBUILD\Everything_else\datasets\ghostdata_master\scraped_raw"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"wiki_{topic_formatted.lower()}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    file_size_kb = os.path.getsize(filepath) // 1024
    print(f"✅ Saved: {filepath}")
    print(f"{file_size_kb}KB\n")

    # -----------------------------------
    # 🧠 NEW: SCRAPE "See Also" Links (BETTER METHOD)
    # -----------------------------------
    see_also_header = soup.find("span", {"id": "See_also"})

    if see_also_header:
        print(f"🔗 Found 'See Also' section for {topic_formatted}, fetching related topics...")

        current = see_also_header.find_parent()
        see_also_content = []

        # Collect all siblings until next H2 or H3 (new section)
        while True:
            current = current.find_next_sibling()
            if current is None:
                break
            if current.name in ["h2", "h3"]:
                break
            see_also_content.append(current)

        # Find all links inside See Also content
        for content in see_also_content:
            links = content.find_all("a")
            for link in links:
                related_title = link.get("href", "")

                if related_title.startswith("/wiki/") and ":" not in related_title:
                    related_topic = related_title.replace("/wiki/", "").replace("_", " ")
                    print(f"   → Scraping related topic: {related_topic}")

                    time.sleep(2)

                    scrape_wikipedia_page(related_topic)


#######################################
# 🚀 MAIN SCRIPT
#######################################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python wiki_scraper.py <topic1> <topic2> ... <topicN>")
        print("  python wiki_scraper.py batch <filename>")
    else:
        if sys.argv[1].lower() == "batch":
            if len(sys.argv) < 3:
                print("❗ Error: Please provide a batch filename.")
                sys.exit(1)

            batch_file = sys.argv[2]

            if not os.path.exists(batch_file):
                print(f"❗ Error: Batch file not found: {batch_file}")
                sys.exit(1)

            with open(batch_file, "r", encoding="utf-8") as f:
                topics = [line.strip() for line in f if line.strip()]

            print(f"📦 Loaded {len(topics)} topics from {batch_file}\n")

            for topic in topics:
                scrape_wikipedia_page(topic)

        else:
            topics = sys.argv[1:]
            for topic in topics:
                scrape_wikipedia_page(topic)
