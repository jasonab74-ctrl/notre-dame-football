# feeds.py — Notre Dame Football sources + buttons
# Notes: feeds should be RSS. For sites without RSS, use Google/Bing News queries.

FEEDS = [
    # Broad news catch-alls
    {"name": "Google News — Notre Dame Football", "url": "https://news.google.com/rss/search?q=Notre+Dame+football&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bing News — Notre Dame Football", "url": "https://www.bing.com/news/search?q=Notre+Dame+football&format=RSS"},

    # Team-centric outlets (RSS)
    {"name": "One Foot Down (SB Nation)", "url": "https://www.onefootdown.com/rss/index.xml"},
    {"name": "Fighting Irish Wire (USA Today)", "url": "https://fightingirishwire.usatoday.com/feed/"},
    {"name": "Blue & Gold (On3) – ND", "url": "https://www.on3.com/teams/notre-dame-fighting-irish/rss/"},
    {"name": "Inside ND Sports (Rivals)", "url": "https://notredame.rivals.com/rss"},

    # Broader CFB that frequently includes ND (kept after filtering)
    {"name": "ESPN College Football", "url": "https://www.espn.com/espn/rss/ncf/news"},
    {"name": "CBS Sports College Football", "url": "https://www.cbssports.com/partners/feeds/rss/college-football/"},

    # Reddit (fresh fan chatter)
    {"name": "Reddit — r/CFB (Notre Dame search)", "url": "https://www.reddit.com/r/CFB/search.rss?q=Notre%20Dame%20football&restrict_sr=on&sort=new"},
    {"name": "Reddit — r/NotreDame (football search)", "url": "https://www.reddit.com/r/NotreDame/search.rss?q=football&restrict_sr=on&sort=new"},
]

STATIC_LINKS = [
    {"label": "Schedule", "url": "https://fightingirish.com/sports/football/schedule/"},
    {"label": "Roster", "url": "https://fightingirish.com/sports/football/roster/"},
    {"label": "Standings", "url": "https://www.espn.com/college-football/standings"},
    {"label": "ND Insider", "url": "https://www.southbendtribune.com/sports/notre-dame/"},
    {"label": "Irish Envy", "url": "https://www.irishenvy.com/forums/notre-dame-football.3/"},
    {"label": "Fighting Irish Wire", "url": "https://fightingirishwire.usatoday.com/"},
    {"label": "One Foot Down", "url": "https://www.onefootdown.com/"},
    {"label": "Blue & Gold (On3)", "url": "https://www.on3.com/teams/notre-dame-fighting-irish/"},
    {"label": "Inside ND Sports (Rivals)", "url": "https://notredame.rivals.com/"},
    {"label": "AP Poll", "url": "https://apnews.com/hub/ap-top-25-college-football-poll"},
    {"label": "247Sports ND", "url": "https://247sports.com/college/notre-dame/"},
    {"label": "Reddit", "url": "https://www.reddit.com/r/NotreDame/"},
]
