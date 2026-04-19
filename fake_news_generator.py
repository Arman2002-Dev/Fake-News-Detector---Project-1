"""
FAKE NEWS GENERATOR BOT
Generates realistic fake news variations from real news articles
Run this alongside the scraper to create balanced training data
"""

import pandas as pd
import random
import os
from datetime import datetime
import re

# Input/Output files
INPUT_CSV = 'live_news_dataset.csv'
OUTPUT_CSV = 'live_news_dataset.csv'  # Appends to same file

class FakeNewsGenerator:
    def __init__(self):
        # Templates for generating fake news (subtle and realistic)
        self.title_templates = [
            # Misattribution - Wrong source
            "{source} reports: {original_title}",
            "Sources claim: {original_title}",
            "Unconfirmed: {original_title}",
            
            # Exaggeration
            "BREAKING: {original_title} - Sources say situation worse than reported",
            "URGENT: {original_title} (Developing)",
            "ALERT: {original_title}",
            
            # False details
            "{original_title}, dozens feared dead",
            "{original_title}, government denies cover-up",
            "{original_title} - Exclusive details emerge",
            
            # Emotional manipulation
            "Shocking: {original_title}",
            "You won't believe: {original_title}",
            "Outrage as {original_title}",
            
            # Conspiracy angle
            "What they hide: {original_title}",
            "The truth about: {original_title}",
            "Exposed: {original_title}",
            
            # Social media style
            "Viral: {original_title}",
            "Everyone's sharing: {original_title}",
            "Trending now: {original_title}",
        ]
        
        self.text_manipulations = [
            # Add false details
            lambda text: f"{text} Sources close to the matter reveal the situation is far more serious than officially acknowledged.",
            
            # Add unverified claims
            lambda text: f"Unverified reports suggest {text} Independent journalists are investigating.",
            
            # Add emotional manipulation
            lambda text: f"This is devastating. {text} People are outraged by this development.",
            
            # Add conspiracy
            lambda text: f"{text} However, critics question the official narrative, pointing to inconsistencies in the report.",
            
            # Add urgency/fear
            lambda text: f"BREAKING: {text} Experts warn this could escalate rapidly. Stay tuned for updates.",
            
            # Add anonymous sources
            lambda text: f"{text} An anonymous insider who requested anonymity stated, 'This is just the tip of the iceberg.'",
            
            # Add social media angle
            lambda text: f"{text} The story has gone viral on social media, with millions sharing unverified claims.",
            
            # Add denial/cover-up angle
            lambda text: f"{text} Officials have refused to comment on allegations of a cover-up.",
            
            # Add false expert opinion
            lambda text: f"{text} Independent experts we spoke to expressed grave concerns about the official version of events.",
            
            # Add religious/political angle
            lambda text: f"{text} Religious leaders have called for prayers amid growing uncertainty.",
        ]
        
        # Fake sources to attribute to
        self.fake_sources = [
            'social_media_post',
            'unverified_blog',
            'anonymous_tip',
            'viral_message',
            'unconfirmed_report',
            'foreign_tabloid',
            'conspiracy_forum',
            'satire_site',
            'fake_news_site',
            'propaganda_outlet'
        ]

    def safe_text(self, text):
        """Ensure text is a string, handle NaN/None"""
        if pd.isna(text) or text is None:
            return ""
        return str(text)

    def generate_fake_variations(self, real_news, num_variations=10):
        """
        Generate fake news variations from a real news article
        """
        fake_news_list = []
        
        original_title = self.safe_text(real_news['title'])
        original_text = self.safe_text(real_news['text'])
        original_source = self.safe_text(real_news.get('source', 'unknown'))
        
        # Skip if no meaningful content
        if not original_title and not original_text:
            return []
        
        # Use title as text if text is empty
        if not original_text:
            original_text = original_title
        
        for i in range(num_variations):
            # Select random template and manipulation
            title_template = random.choice(self.title_templates)
            text_modification = random.choice(self.text_manipulations)
            
            # Generate fake title
            fake_title = title_template.format(
                original_title=original_title,
                source=original_source.capitalize()
            )
            
            # Generate fake text
            try:
                fake_text = text_modification(original_text)
            except:
                # Fallback if manipulation fails
                fake_text = f"Sources claim: {original_text} This remains unverified."
            
            # Add extra fake details randomly
            if random.random() > 0.5:
                fake_details = self._generate_fake_details(original_title)
                fake_text += " " + fake_details
            
            # Create fake news entry
            fake_entry = {
                'title': fake_title,
                'text': fake_text,
                'source': random.choice(self.fake_sources),
                'url': '',
                'published_date': '',
                'scraped_date': datetime.now().isoformat(),
                'label': 'FAKE',
                'based_on': original_title[:50] if original_title else 'unknown'  # Track which real news this is based on
            }
            
            fake_news_list.append(fake_entry)
        
        return fake_news_list

    def _generate_fake_details(self, title):
        """Generate plausible-sounding but false details"""
        fake_details = [
            "Witnesses reported hearing explosions before the incident.",
            "Local residents claim this was predicted days ago.",
            "The official spokesperson could not be reached for comment.",
            "Contradictory statements from officials raise questions.",
            "Deleted social media posts suggest prior knowledge.",
            "Foreign intelligence agencies are reportedly monitoring the situation.",
            "The timing coincides with other suspicious events.",
            "Critics point to similar incidents that were later debunked.",
            "Anonymous officials suggest the full story may never be known.",
            "Internet users have spotted what they claim are inconsistencies.",
        ]
        return random.choice(fake_details)

    def process_csv(self, num_fake_per_real=2):
        """
        Read CSV, generate fake news for each real news, append to CSV
        """
        if not os.path.exists(INPUT_CSV):
            print(f"Error: {INPUT_CSV} not found!")
            return
        
        # Read existing data
        try:
            df = pd.read_csv(INPUT_CSV)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return
        
        # Get only REAL news that haven't been processed yet
        real_news = df[df['label'] == 'REAL'].to_dict('records')
        
        if not real_news:
            print("No real news found to process!")
            return
        
        print(f"Found {len(real_news)} real news articles")
        print(f"Generating {num_fake_per_real} fake variations each...")
        print(f"Total fake news to generate: {len(real_news) * num_fake_per_real}")
        
        all_fake_news = []
        skipped = 0
        
        for idx, news in enumerate(real_news, 1):
            # Skip if this real news already has generated fakes (check based_on column)
            title_check = self.safe_text(news['title'])[:50]
            existing_fakes = df[df.get('based_on', pd.Series(['']*len(df))) == title_check]
            
            if len(existing_fakes) >= num_fake_per_real:
                skipped += 1
                continue
            
            print(f"Processing {idx}/{len(real_news)}: {self.safe_text(news['title'])[:60]}...")
            
            # Generate fake variations
            fake_variations = self.generate_fake_variations(news, num_fake_per_real)
            all_fake_news.extend(fake_variations)
            
            # Progress update every 10
            if idx % 10 == 0:
                print(f"  Generated {len(all_fake_news)} fake articles so far...")
        
        if skipped > 0:
            print(f"\nSkipped {skipped} articles (already have generated fakes)")
        
        # Create DataFrame and save
        if all_fake_news:
            df_fake = pd.DataFrame(all_fake_news)
            
            # Combine with existing data
            df_combined = pd.concat([df, df_fake], ignore_index=True)
            
            # Remove duplicates based on title
            df_combined = df_combined.drop_duplicates(subset=['title'], keep='first')
            
            # Save back to CSV
            df_combined.to_csv(OUTPUT_CSV, index=False)
            
            print(f"\n{'='*60}")
            print("GENERATION COMPLETE!")
            print(f"{'='*60}")
            real_count = len(df_combined[df_combined['label'] == 'REAL'])
            fake_count = len(df_combined[df_combined['label'] == 'FAKE'])
            print(f"Total real news: {real_count}")
            print(f"Total fake news: {fake_count}")
            print(f"Total dataset size: {len(df_combined)}")
            print(f"\nSaved to: {OUTPUT_CSV}")
            
            # Show samples
            print(f"\n{'='*60}")
            print("SAMPLE GENERATED FAKE NEWS:")
            print(f"{'='*60}")
            for i in range(min(3, len(df_fake))):
                sample = df_fake.iloc[i]
                print(f"\n{i+1}. {self.safe_text(sample['title'])[:80]}...")
                print(f"   Source: {sample['source']}")
                text_sample = self.safe_text(sample['text'])[:100]
                print(f"   Text: {text_sample}...")
        else:
            print("No new fake news generated (all articles may already have variations)")

def continuous_generation(interval_minutes=10):
    """
    Continuously run the generator every X minutes
    """
    generator = FakeNewsGenerator()
    
    print("=" * 60)
    print("FAKE NEWS GENERATOR BOT - CONTINUOUS MODE")
    print("=" * 60)
    print(f"Will check for new real news every {interval_minutes} minutes")
    print("Press Ctrl+C to stop\n")
    
    cycle = 1
    while True:
        print(f"\n{'='*60}")
        print(f"CYCLE #{cycle} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        generator.process_csv(num_fake_per_real=2)
        
        next_time = (datetime.now() + pd.Timedelta(minutes=interval_minutes)).strftime('%H:%M:%S')
        print(f"\nSleeping for {interval_minutes} minutes... (Next: {next_time})")
        
        try:
            import time
            time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            break
        
        cycle += 1

if __name__ == '__main__':
    import sys
    import pandas as pd  # Import here for the time calculation
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once: python fake_news_generator.py --once
        generator = FakeNewsGenerator()
        generator.process_csv(num_fake_per_real=2)
    else:
        # Continuous mode: python fake_news_generator.py
        continuous_generation(interval_minutes=2)