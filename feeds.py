# feeds.py — Notre Dame Football sources + top buttons (safe config only)
# Web server NEVER fetches these at request time. collect.py reads them on a schedule.

from urllib.parse import quote_plus

def gnews(query: str) -> str:
    q = quote_plus(query)
    # English US, Google News RSS
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

# =========================
# NEWS SOURCES (RSS inputs)
# =========================
# Each entry must include a "url". We use Google News with site: filters for reliability.

FEEDS = [
    # Broad ND Football sweep
    {"name": "Google News — Notre Dame Football", "url": gnews("Notre Dame Fighting Irish football")},

    # Requested outlets (site-scoped)
    {"name": "One Foot Down", "url": gnews("site:onefootdown.com Notre Dame Football")},
    {"name": "Irish Sports Daily", "url": gnews("site:irishsportsdaily.com Notre Dame Football")},
    {"name": "NDNation", "url": gnews("site:ndnation.com Notre Dame Football")},
    {"name": "InsideNDSports (Rivals)", "url": gnews("site:insideindsports.com Notre Dame Football")},
    {"name": "CBS Sports — Notre Dame", "url": gnews("site:cbssports.com Notre Dame Fighting Irish football")},
    {"name": "247Sports — Notre Dame", "url": gnews("site:247sports.com Notre Dame Fighting Irish football")},
    {"name": "ESPN — Notre Dame", "url": gnews("site:espn.com Notre Dame Fighting Irish football")},
    {"name": "On3 — Blue & Gold", "url": gnews("site:on3.com 'Blue & Gold' Notre Dame football")},
    {"name": "The Athletic — Notre Dame", "url": gnews("site:theathletic.com Notre Dame Fighting Irish football")},
    {"name": "Fighting Irish Wire (USA Today)", "url": gnews("site:fightingirishwire.usatoday.com Notre Dame Football")},
    {"name": "ND Insider", "url": gnews("site:ndinsider.com Notre Dame Football")},
]

# ====================
# TOP NAVIGATION LINKS
# ====================
# These render as buttons at the top of the page. You asked for Reddit, Irish Envy, YouTube, CFB Rankings, ND Insider, etc.

STATIC_LINKS = [
    {"label": "Official Site", "href": "https://und.com/sports/football/"},
    {"label": "Schedule", "href": "https://und.com/sports/football/schedule/"},
    {"label": "Roster", "href": "https://und.com/sports/football/roster/"},
    {"label": "CFB Rankings", "href": "https://www.espn.com/college-football/rankings"},

    {"label": "ND Insider", "href": "https://www.ndinsider.com/"},
    {"label": "One Foot Down", "href": "https://www.onefootdown.com/"},
    {"label": "Slap the Sign", "href": "https://slapthesign.com/"},
    {"label": "Irish Envy Forum", "href": "https://www.irishenvy.com/"},
    {"label": "Reddit — r/notredamefootball", "href": "https://www.reddit.com/r/notredamefootball/"},
    {"label": "YouTube — ND Football", "href": "https://www.youtube.com/channel/UCAMR05qSc5mfhVx20fDyAoQ"},

    {"label": "247Sports ND", "href": "https://247sports.com/college/notre-dame/"},
    {"label": "ESPN ND Football", "href": "https://www.espn.com/college-football/team/_/id/87/notre-dame-fighting-irish"},
    {"label": "CBS Sports ND", "href": "https://www.cbssports.com/college-football/teams/ND/notre-dame-fighting-irish/"},
    {"label": "On3 — Blue & Gold", "href": "https://www.on3.com/teams/notre-dame-fighting-irish/"},
    {"label": "The Athletic — ND", "href": "https://theathletic.com/college-football/team/notre-dame-fighting-irish/"},
    {"label": "Fighting Irish Wire", "href": "https://fightingirishwire.usatoday.com/"},
]