# feeds.py — Notre Dame Football sources + quick links

FEEDS = [
    # Aggregators
    {"name": "Google News — Notre Dame Football",
     "url": "https://news.google.com/rss/search?q=%22Notre+Dame%22+football+OR+%22Fighting+Irish%22+football&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bing News — Notre Dame Football",
     "url": "https://www.bing.com/news/search?q=%22Notre+Dame%22+football+OR+%22Fighting+Irish%22+football&format=rss"},

    # Team-specific outlets
    {"name": "One Foot Down (SB Nation)",
     "url": "https://www.onefootdown.com/rss/index.xml"},
    {"name": "Blue & Gold — On3",
     "url": "https://www.on3.com/teams/notre-dame-fighting-irish/news/rss"},
    {"name": "247Sports — Notre Dame",
     "url": "https://247sports.com/college/notre-dame/Feed.rss"},
    {"name": "Irish Illustrated (Rivals via Google)",
     "url": "https://news.google.com/rss/search?q=%22Irish+Illustrated%22+Notre+Dame+football&hl=en-US&gl=US&ceid=US:en"},

    # Reddit targets
    {"name": "Reddit — r/CFB (ND search)",
     "url": "https://www.reddit.com/r/CFB/search.rss?q=%22Notre+Dame%22+football&restrict_sr=on&sort=new"},
    {"name": "Reddit — r/notredame (football)",
     "url": "https://www.reddit.com/r/notredame/search.rss?q=football&restrict_sr=on&sort=new"},

    # Official & national
    {"name": "UND.com Football (via Google)",
     "url": "https://news.google.com/rss/search?q=site:und.com+football+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "ESPN — Notre Dame (via Google)",
     "url": "https://news.google.com/rss/search?q=ESPN+Notre+Dame+football&hl=en-US&gl=US&ceid=US:en"},
]

# Top-row quick links (more than before, Purdue-style fullness)
STATIC_LINKS = [
    {"label": "Official Site", "href": "https://und.com/sports/football/"},
    {"label": "Schedule", "href": "https://und.com/sports/football/schedule/"},
    {"label": "Roster", "href": "https://und.com/sports/football/roster/"},
    {"label": "ESPN Team Page", "href": "https://www.espn.com/college-football/team/_/id/87/notre-dame-fighting-irish"},
    {"label": "247Sports", "href": "https://247sports.com/college/notre-dame/"},
    {"label": "On3 (Blue & Gold)", "href": "https://www.on3.com/teams/notre-dame-fighting-irish/"},
    {"label": "Irish Illustrated (Rivals)", "href": "https://notredame.rivals.com/"},
    {"label": "NBC Sports ND", "href": "https://www.nbcsports.com/tags/notre-dame-fighting-irish"},
    {"label": "AP Top 25", "href": "https://apnews.com/hub/ap-top-25-college-football-poll"},
    {"label": "CFP Rankings", "href": "https://collegefootballplayoff.com/rankings"},
    {"label": "Tickets", "href": "https://und.com/tickets/"},
    {"label": "Stats", "href": "https://www.sports-reference.com/cfb/schools/notre-dame/"},
]
