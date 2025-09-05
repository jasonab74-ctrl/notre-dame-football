# feeds.py — Notre Dame Football sources + quick links

FEEDS = [
    # --- Core ND football news aggregators
    {"name": "Google News — Notre Dame Football",
     "url": "https://news.google.com/rss/search?q=%22Notre+Dame%22+football+OR+%22Fighting+Irish%22+football&hl=en-US&gl=US&ceid=US:en"},

    {"name": "Bing News — Notre Dame Football",
     "url": "https://www.bing.com/news/search?q=%22Notre+Dame%22+football+OR+%22Fighting+Irish%22+football&format=rss"},

    # --- Team-specific outlets
    {"name": "One Foot Down (SB Nation) — Notre Dame",
     "url": "https://www.onefootdown.com/rss/index.xml"},

    {"name": "Blue & Gold — On3 Notre Dame",
     "url": "https://www.on3.com/teams/notre-dame-fighting-irish/news/rss"},  # Sometimes partial

    {"name": "247Sports — Notre Dame",
     "url": "https://247sports.com/college/notre-dame/Feed.rss"},

    {"name": "Irish Illustrated (Rivals/On3 mirror via Google)",
     "url": "https://news.google.com/rss/search?q=%22Irish+Illustrated%22+Notre+Dame+football&hl=en-US&gl=US&ceid=US:en"},

    # --- Reddit (targeted searches)
    {"name": "Reddit — r/CFB (Notre Dame search)",
     "url": "https://www.reddit.com/r/CFB/search.rss?q=%22Notre+Dame%22+football&restrict_sr=on&sort=new"},

    {"name": "Reddit — r/notredame (football search)",
     "url": "https://www.reddit.com/r/notredame/search.rss?q=football&restrict_sr=on&sort=new"},

    # --- Official & national pages via Google News (for consistency)
    {"name": "Official — UND.com Football (via Google)",
     "url": "https://news.google.com/rss/search?q=site:und.com+football+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},

    {"name": "ESPN — Notre Dame (via Google)",
     "url": "https://news.google.com/rss/search?q=ESPN+Notre+Dame+football&hl=en-US&gl=US&ceid=US:en"},
]

# Quick-access buttons shown at top of the site.
STATIC_LINKS = [
    {"label": "Official Site", "href": "https://und.com/sports/football/"},
    {"label": "Schedule", "href": "https://und.com/sports/football/schedule/"},
    {"label": "Roster", "href": "https://und.com/sports/football/roster/"},
    {"label": "ESPN Team Page", "href": "https://www.espn.com/college-football/team/_/id/87/notre-dame-fighting-irish"},
    {"label": "247Sports", "href": "https://247sports.com/college/notre-dame/"},
    {"label": "On3 (Blue & Gold)", "href": "https://www.on3.com/teams/notre-dame-fighting-irish/"},
    {"label": "AP Top 25", "href": "https://apnews.com/hub/ap-top-25-college-football-poll"},
    {"label": "CFP Rankings", "href": "https://collegefootballplayoff.com/rankings"},
]
