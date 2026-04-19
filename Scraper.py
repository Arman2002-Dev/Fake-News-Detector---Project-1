import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os
import random

CSV_FILE = 'fake_or_real_news.csv'

# List of user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]

def get_headers():
    return {'User-Agent': random.choice(USER_AGENTS)}

def scrape_tribune(pages=3):
    """Scrape Tribune with pagination"""
    all_news = []
    
    for page in range(1, pages + 1):
        try:
            # Tribune pagination URLs
            if page == 1:
                url = 'https://tribune.com.pk/'
            else:
                url = f'https://tribune.com.pk/latest/page/{page}'
            
            print(f"  Tribune page {page}...", end=" ")
            response = requests.get(url, headers=get_headers(), timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', class_='singleBlock')
            page_count = 0
            
            for article in articles:
                title_tag = article.find('h2')
                if not title_tag:
                    continue
                
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue
                
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href', '')
                
                summary_tag = article.find('p')
                text = summary_tag.get_text(strip=True) if summary_tag else ''
                
                date_tag = article.find('span', class_='date') or article.find('span', class_='time')
                date = date_tag.get_text(strip=True) if date_tag else ''
                
                if title and len(title) > 10:
                    all_news.append({
                        'title': title,
                        'text': text,
                        'source': 'tribune',
                        'url': link,
                        'published_date': date,
                        'scraped_date': datetime.now().isoformat(),
                        'label': 'REAL'
                    })
                    page_count += 1
            
            print(f"{page_count} articles")
            time.sleep(2)  # Be polite to server
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            continue
    
    return all_news

def scrape_dawn(pages=3):
    """Scrape Dawn with pagination"""
    all_news = []
    
    for page in range(1, pages + 1):
        try:
            # Dawn pagination
            if page == 1:
                url = 'https://www.dawn.com/latest-news'
            else:
                url = f'https://www.dawn.com/latest-news/{page}'
            
            print(f"  Dawn page {page}...", end=" ")
            response = requests.get(url, headers=get_headers(), timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', class_='story') or soup.find_all('div', class_='story')
            page_count = 0
            
            for article in articles:
                title_tag = article.find('h2', class_='story__title') or article.find('a', class_='story__link')
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '') if title_tag.name == 'a' else title_tag.find('a', href=True)
                if isinstance(link, dict):
                    link = link.get('href', '')
                
                summary_tag = article.find('div', class_='story__excerpt') or article.find('p')
                text = summary_tag.get_text(strip=True) if summary_tag else ''
                
                if title and len(title) > 10:
                    all_news.append({
                        'title': title,
                        'text': text,
                        'source': 'dawn',
                        'url': link if isinstance(link, str) else '',
                        'published_date': '',
                        'scraped_date': datetime.now().isoformat(),
                        'label': 'REAL'
                    })
                    page_count += 1
            
            print(f"{page_count} articles")
            time.sleep(2)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            continue
    
    return all_news

def scrape_bbc_urdu(pages=2):
    """Scrape BBC Urdu for regional language support"""
    all_news = []
    
    for page in range(1, pages + 1):
        try:
            if page == 1:
                url = 'https://www.bbc.com/urdu'
            else:
                url = f'https://www.bbc.com/urdu?page={page}'
            
            print(f"  BBC Urdu page {page}...", end=" ")
            response = requests.get(url, headers=get_headers(), timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article') or soup.find_all('div', class_='bbc-uk8dsi')
            page_count = 0
            
            for article in articles[:10]:  # Limit per page
                title_tag = article.find('h2') or article.find('h3')
                if not title_tag:
                    continue
                
                link_tag = title_tag.find('a')
                title = title_tag.get_text(strip=True)
                link = link_tag.get('href', '') if link_tag else ''
                
                if title and len(title) > 10:
                    all_news.append({
                        'title': title,
                        'text': '',  # BBC requires visiting individual pages
                        'source': 'bbc_urdu',
                        'url': f"https://www.bbc.com{link}" if link.startswith('/') else link,
                        'published_date': '',
                        'scraped_date': datetime.now().isoformat(),
                        'label': 'REAL'
                    })
                    page_count += 1
            
            print(f"{page_count} articles")
            time.sleep(2)
            
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    return all_news

def generate_synthetic_fake_news(real_news_list, count=50):
    """
    Generate synthetic FAKE news by modifying REAL news
    This is TEMPORARY - replace with actual fake news sources when available
    """
    print(f"\nGenerating {count} synthetic FAKE samples for training...")
    
    fake_templates = [
        "BREAKING: Secret sources reveal {topic}",
        "SHOCKING: What they don't want you to know about {topic}",
        "URGENT: Government hiding evidence that {topic}",
        "VIRAL: Everyone is sharing this! {topic}",
        "EXPOSED: Anonymous insider confirms {topic}",
        "ALERT: Conspiracy theorists were right about {topic}",
        "MUST READ: The truth about {topic} they tried to ban",
        "LEAKED: Classified documents show {topic}",
        "WARNING: Experts are lying about {topic}",
        "REVEALED: Hidden camera footage shows {topic}"
    ]
    
    fake_news_list = []
    
    for i in range(count):
        # Pick a random real news item
        real_item = random.choice(real_news_list)
        
        # Create fake version
        template = random.choice(fake_templates)
        fake_title = template.format(topic=real_item['title'])
        
        fake_text = (
            f"Unverified sources claim that {real_item['text']} "
            f"This has been widely disputed by independent fact-checkers. "
            f"Social media users are sharing this without confirmation. "
            f"Experts warn this may be misleading information."
        )
        
        fake_news_list.append({
            'title': fake_title,
            'text': fake_text,
            'source': 'unverified_social_media',
            'url': '',
            'published_date': '',
            'scraped_date': datetime.now().isoformat(),
            'label': 'FAKE'
        })
    
    print(f"Generated {len(fake_news_list)} FAKE samples")
    return fake_news_list

def save_to_csv(news_list, include_fake=True):
    if not news_list:
        print("No articles to save")
        return
    
    df_new = pd.DataFrame(news_list)
    df_new = df_new.drop_duplicates(subset=['title'], keep='first')
    
    # If we want to add synthetic fake data for training balance
    if include_fake and len(df_new) > 0:
        real_count = len(df_new[df_new['label'] == 'REAL'])
        fake_news = generate_synthetic_fake_news(
            df_new[df_new['label'] == 'REAL'].to_dict('records'), 
            count=min(real_count, 100)  # Generate equal or up to 100 fake
        )
        df_new = pd.concat([df_new, pd.DataFrame(fake_news)], ignore_index=True)
        print(f"Added {len(fake_news)} synthetic FAKE samples for balanced training")
    
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        try:
            df_existing = pd.read_csv(CSV_FILE)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=['title'], keep='first')
            df_combined.to_csv(CSV_FILE, index=False)
            
            real_count = len(df_combined[df_combined['label'] == 'REAL'])
            fake_count = len(df_combined[df_combined['label'] == 'FAKE'])
            print(f"Saved! Total: {len(df_combined)} (REAL: {real_count}, FAKE: {fake_count})")
        except Exception as e:
            print(f"Error merging: {e}")
            df_new.to_csv(CSV_FILE, index=False)
            print(f"Saved new: {len(df_new)} articles")
    else:
        df_new.to_csv(CSV_FILE, index=False)
        real_count = len(df_new[df_new['label'] == 'REAL'])
        fake_count = len(df_new[df_new['label'] == 'FAKE'])
        print(f"Created new: {len(df_new)} (REAL: {real_count}, FAKE: {fake_count})")

def continuous_scrape(pages_per_source=3, interval_minutes=5):
    print("=" * 60)
    print("ENHANCED FAKE NEWS DATA COLLECTOR")
    print("Sources: Tribune, Dawn, BBC Urdu")
    print("=" * 60)
    print(f"Pages per source: {pages_per_source}")
    print(f"Collection interval: {interval_minutes} minutes")
    print("Press Ctrl+C to stop\n")
    
    # Delete empty CSV if exists
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) == 0:
        os.remove(CSV_FILE)
    
    cycle = 1
    while True:
        print(f"\n{'='*60}")
        print(f"CYCLE #{cycle} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        all_news = []
        
        # Scrape all sources with pagination
        print("\nScraping REAL news sources...")
        all_news.extend(scrape_tribune(pages=pages_per_source))
        all_news.extend(scrape_dawn(pages=pages_per_source))
        # all_news.extend(scrape_bbc_urdu(pages=2))  # Uncomment if needed
        
        if all_news:
            save_to_csv(all_news, include_fake=True)
        else:
            print("No articles collected in this cycle")
        
        next_time = (datetime.now() + pd.Timedelta(minutes=interval_minutes)).strftime('%H:%M:%S')
        print(f"\nSleeping for {interval_minutes} minutes... (Next: {next_time})")
        
        try:
            time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            break
        
        cycle += 1

def single_scrape(pages_per_source=5):
    """Run once and exit - good for initial data collection"""
    print("=" * 60)
    print("SINGLE SCRAPE MODE")
    print("=" * 60)
    
    all_news = []
    
    print("\nScraping REAL news sources...")
    all_news.extend(scrape_tribune(pages=pages_per_source))
    all_news.extend(scrape_dawn(pages=pages_per_source))
    
    if all_news:
        save_to_csv(all_news, include_fake=True)
        print(f"\nDone! Collected {len(all_news)} REAL articles")
    else:
        print("No articles collected")

if __name__ == '__main__':
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once: python Scraper.py --once
        single_scrape(pages_per_source=5)
    else:
        # Continuous mode: python Scraper.py
        continuous_scrape(pages_per_source=3, interval_minutes=5)