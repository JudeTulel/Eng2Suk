'''
This script contains the web scraping logic to collect a parallel corpus of Pokot and English bible verses.
It is designed to be respectful of the source websites with built-in delays.
'''
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from tqdm import tqdm

class PokotScraper:
    '''A class to scrape Pokot and English bible verses from parallel views.'''
    def __init__(self, base_url="https://www.bible.com/bible/"):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_chapter_url(self, book, chapter, english_version="68", pokot_version="2884", english_code="GNT"):
        '''Constructs the URL for a specific bible chapter in parallel view.'''
        return f"{self.base_url}{english_version}/{book}.{chapter}.{english_code}?parallel={pokot_version}"

    def scrape_chapter_texts(self, book, chapter, english_version="68", pokot_version="2884"):
        '''Scrapes English and Pokot verses by making two requests, extracting the parallel data from each.'''
        
        # URL 1: English Primary, Pokot Parallel -> Parse Pokot from Parallel Data
        url_get_pokot = f"{self.base_url}{english_version}/{book}.{chapter}.GNT?parallel={pokot_version}"
        pokot_verses = self._fetch_parallel_content_from_url(url_get_pokot)
        
        # URL 2: Pokot Primary, English Parallel -> Parse English from Parallel Data
        # Note: Pokot code is PKO.
        url_get_english = f"{self.base_url}{pokot_version}/{book}.{chapter}.PKO?parallel={english_version}"
        english_verses = self._fetch_parallel_content_from_url(url_get_english)
        
        return english_verses, pokot_verses

    def _fetch_parallel_content_from_url(self, url):
        '''Fetches the URL and extracts verses from parallelChapterInfoData.'''
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                script = soup.find('script', id='__NEXT_DATA__')
                if script:
                    try:
                        data = json.loads(script.string)
                        page_props = data.get('props', {}).get('pageProps', {})
                        # Parallel content is consistently here
                        html_content = page_props.get('parallelChapterInfoData', {}).get('content')
                        return self._extract_verses_from_html(html_content)
                    except Exception as e:
                        print(f"Error parsing JSON for {url}: {e}")
            return {}
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return {}

    def _extract_verses_from_html(self, html_content):
        '''Helper to extract verses from an HTML string.'''
        if not html_content: return {}
        soup = BeautifulSoup(html_content, 'html.parser')
        verses = {}
        # Select all verse spans that have data-usfm attribute
        for verse_span in soup.select('span.verse[data-usfm]'):
            usfm = verse_span.get('data-usfm') # e.g. GEN.1.1
            content_span = verse_span.find('span', class_='content')
            if usfm and content_span:
                # Extract verse number from USFM or label
                verse_num_str = usfm.split('.')[-1]
                verses[verse_num_str] = content_span.get_text(strip=True)
        return verses

    def create_parallel_corpus(self, book_chapter_map, english_version="68", pokot_version="2884", english_code="GNT"):
        '''
        Creates a parallel corpus by scraping chapters for a given map of books and chapters.
        Args:
            book_chapter_map (dict): A dictionary where keys are book abbreviations (e.g., "GEN")
                                     and values are the number of chapters in that book to scrape.
            english_version (str): The version ID for the English bible on the website.
            pokot_version (str): The version ID for the Pokot bible on the website.
            english_code (str): The code for the English version (e.g., "GNT").
        '''
        data = []
        total_chapters = sum(book_chapter_map.values())
        with tqdm(total=total_chapters, desc="Scraping Chapters") as pbar:
            for book, num_chapters in book_chapter_map.items():
                for chapter in range(1, num_chapters + 1):
                    english_verses, pokot_verses = self.scrape_chapter_texts(book, chapter, english_version, pokot_version)
                    pbar.update(1)
                    if english_verses and pokot_verses:
                        verse_nums = sorted(set(english_verses.keys()) & set(pokot_verses.keys()), key=int)
                        for verse in verse_nums:
                            data.append({
                                "book": book,
                                "chapter": chapter,
                                "verse": int(verse),
                                "english": english_verses[verse],
                                "pokot": pokot_verses[verse]
                            })
                    time.sleep(random.uniform(3.0, 6.0))  # Longer respectful delay between chapters
        df = pd.DataFrame(data)
        output_path = 'data/parallel_corpus.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Successfully saved {len(df)} parallel verses to {output_path}")
        return df

if __name__ == "__main__":
    # Expanded sample for more language diversity: One chapter each from Genesis, Deuteronomy, Psalms, Matthew, and Romans.
    # You can add more books or increase chapters per book as needed.
    # Full list of books: GEN:50, EXO:40, LEV:27, NUM:36, DEU:34, etc. (abbreviate in 3 letters, uppercase).
    sample_book_map = {
        "GEN": 1,   # Narrative, creation
        "DEU": 1,   # Law, speeches
        "PSA": 1,   # Poetry, psalms
        "MAT": 1,   # Gospel, teachings
        "ROM": 1    # Epistle, theology
    }
    scraper = PokotScraper()
    scraper.create_parallel_corpus(sample_book_map)