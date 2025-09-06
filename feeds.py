# feeds.py — Notre Dame Football sources + top buttons

# Helper to form Google News RSS queries that are reliable
def gnews(query: str) -> str:
    from urllib.parse import quote_plus
    q = quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

FEEDS = [
    # General Notre Dame Football news
    {"name": "Google News — Notre Dame Football", "url": gnews("Notre Dame Football")},
    # Requested outlets (use site: filters so we stay on target)
    {"name": "One Foot Down", "url": gnews("site:onefootdown.com Notre Dame Football")},
    {"name": "Irish Sports Daily", "url": gnews("site:irishsportsdaily.com Notre Dame Football")},
    {"name": "NDNation", "url": gnews("site:ndnation.com Notre Dame Football")},
    {"name": "InsideNDSports (Rivals)", "url": gnews("site:insideindsports.com Notre Dame Football")},
    {"name": "CBS Sports — Notre Dame", "url": gnews("site:cbssports.com Notre Dame Fighting Irish football")},
    {"name": "247Sports — Notre Dame", "url": gnews("site:247sports.com Notre Dame Fighting Irish football")},
    {"name": "ESPN — Notre Dame", "url": gnews("site:espn.com Notre Dame Fighting Irish football")},
    {"name": "On3 — Blue & Gold", "url": gnews("site:on3.com 'Blue & Gold' Notre Dame Football")},
    {"name": "The Athletic — Notre Dame", "url": gnews("site:theathletic.com Notre Dame Fighting Irish football")},
    {"name": "Fighting Irish Wire", "url": gnews("site:fightingirishwire.usatoday.com Notre Dame Football")},
]

# Top nav buttons
STATIC_LINKS = [
    {"label": "Official Site", "href": "https://und.com/sports/football/"},
    {"label": "Schedule", "href": "https://und.com/sports/football/schedule/"},
    {"label": "Roster",   "href": "https://und.com/sports/football/roster/"},
    {"label": "ND Insider", "href": "https://www.ndinsider.com/"},
    {"label": "One Foot Down", "href": "https://www.onefootdown.com/"},
    {"label": "Slap the Sign", "href": "https://slapthesign.com/"},
    {"label": "Irish Envy Forum", "href": "https://www.irishenvy.com/"},
    {"label": "YouTube — Notre Dame Football", "href": "https://www.youtube.com/channel/UCAMR05qSc5mfhVx20fDyAoQ"},
    {"label": "Reddit — r/notredamefootball", "href": "https://www.reddit.com/r/notredamefootball/"},
    {"label": "CFB Rankings", "href": "https://www.espn.com/college-football/rankings"},
]