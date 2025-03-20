#!/usr/bin/env python3
"""
Advanced Threat Intelligence Platform
---------------------------------------
Features:
- Aggregates threat intelligence data from RSS feeds.
- Stores threat indicators in a persistent SQLite database.
- Provides a CLI for querying stored threat data.
- Extensible architecture to support multiple threat sources.

Usage:
  python advanced_threat_intel.py --fetch
  python advanced_threat_intel.py --query
"""

import feedparser, sqlite3, argparse, logging
from datetime import datetime

DB_NAME = "advanced_threat_intel.db"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            published TEXT,
            summary TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_store_feed(feed_url):
    try:
        feed = feedparser.parse(feed_url)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for entry in feed.entries:
            c.execute("INSERT INTO threats (title, link, published, summary) VALUES (?, ?, ?, ?)",
                      (entry.title, entry.link, entry.published, entry.summary))
        conn.commit()
        conn.close()
        logging.info("Threat feed updated from %s", feed_url)
    except Exception as e:
        logging.error("Error fetching or storing feed: %s", e)

def query_threats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, published FROM threats ORDER BY published DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def main_threat_intel():
    init_db()
    parser = argparse.ArgumentParser(description="Advanced Threat Intelligence Platform")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true", help="Fetch threat feed and update database")
    group.add_argument("--query", action="store_true", help="Query stored threat data")
    args = parser.parse_args()
    if args.fetch:
        feed_url = "https://www.securityweek.com/rss"
        fetch_and_store_feed(feed_url)
        print("Threat feed updated.")
    else:
        threats = query_threats()
        for t in threats:
            print(f"{t[2]} - {t[1]} (ID: {t[0]})")

if __name__ == "__main__":
    main_threat_intel()
