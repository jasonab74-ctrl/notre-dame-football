# feeds.py — Notre Dame Football sources + header buttons

# ====== NEWS FEEDS (RSS / RSS-like) ======
# Each item is: {"name": "...", "url": "..."}.
# If a site doesn't expose clean RSS, we use Google News’ RSS for that domain.

FEEDS = [
    # Broad ND football news
    {"name": "Google News — Notre Dame Football", "url": "https://news.google.com/rss/search?q=%22Notre+Dame%22+football&hl=en-US&gl=US&ceid=US:en"},

    # Team-centric outlets
    {"name": "Irish Wire", "url": "https://ndwire.usatoday.com/feed/"},
    {"name": "On3 — Blue & Gold", "url": "https://www.on3.com/teams/notre-dame-fighting-irish/feeds/rss/"},
    {"name": "247Sports — Notre Dame", "url": "https://247sports.com/college/notre-dame/Feeds/"},
    {"name": "Irish Illustrated", "url": "https://247sports.com/college/notre-dame/Article/rss/"},
    {"name": "NBC Sports — Notre Dame", "url": "https://sports.nbcsports.com/tag/notre-dame-football/feed/"},
    {"name": "CBS Sports — Notre Dame", "url": "https://www.cbssports.com/college-football/teams/ND/notre-dame-fighting-irish/rss/"},
    # ND Insider (requested). If their global RSS changes, the domain-scoped Google News RSS is stable.
    {"name": "ND Insider", "url": "https://news.google.com/rss/search?q=site%3Andinsider.com+%22Notre+Dame%22+football&hl=en-US&gl=US&ceid=US:en"},
    # Fan sites (usually lots of good pieces)
    {"name": "One Foot Down", "url": "https://www.onefootdown.com/rss/index.xml"},
    {"name": "Slap the Sign", "url": "https://slapthesign.com/feed/"},
]

# ====== HEADER / QUICK LINKS (the gold “pills” up top) ======
STATIC_LINKS = [
    {"label": "Official Site", "href": "https://fightingirish.com/sports/football/"},
    {"label": "Schedule", "href": "https://fightingirish.com/sports/football/schedule/"},
    {"label": "Roster", "href": "https://fightingirish.com/sports/football/roster/"},
    {"label": "Rankings", "href": "https://www.espn.com/college-football/rankings"},  # easy-to-read aggregate
    {"label": "Reddit — r/notredamefootball", "href": "https://www.reddit.com/r/notredamefootball/"},
    {"label": "Irish Envy Forum", "href": "https://www.irishenvy.com/"},
    {"label": "One Foot Down", "href": "https://www.onefootdown.com/"},
    {"label": "Slap the Sign", "href": "https://slapthesign.com/"},
]