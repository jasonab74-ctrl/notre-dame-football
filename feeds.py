# feeds.py — Notre Dame Football sources + quick links

# Primary list used by collect.py; "name" shows in the Sources dropdown.
# Where a site doesn't have a stable public RSS, we use a Google News RSS
# filtered to that domain.
FEEDS = [
    # 1) One Foot Down (SB Nation)
    {"name": "One Foot Down", "url": "https://www.onefootdown.com/rss/index.xml"},

    # 2) Irish Sports Daily (use Google News feed to the domain)
    {"name": "Irish Sports Daily", "url": "https://news.google.com/rss/search?q=site:irishsportsdaily.com+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},

    # 3) NDNation
    {"name": "NDNation", "url": "https://news.google.com/rss/search?q=site:ndnation.com+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},

    # 4) InsideNDSports (Rivals)
    {"name": "InsideNDSports (Rivals)", "url": "https://news.google.com/rss/search?q=site:notredame.rivals.com+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},

    # 5) CBS Sports — Notre Dame Fighting Irish
    {"name": "CBS Sports — Notre Dame", "url": "https://news.google.com/rss/search?q=site:cbssports.com+%22Notre+Dame%22+football&hl=en-US&gl=US&ceid=US:en"},

    # 6) 247Sports — Notre Dame
    {"name": "247Sports — Notre Dame", "url": "https://news.google.com/rss/search?q=site:247sports.com+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},

    # 7) ESPN — Notre Dame Football
    {"name": "ESPN — Notre Dame", "url": "https://news.google.com/rss/search?q=site:espn.com+%22Notre+Dame%22+football&hl=en-US&gl=US&ceid=US:en"},

    # 8) On3 (Blue & Gold) — Notre Dame
    {"name": "On3 — Blue & Gold", "url": "https://news.google.com/rss/search?q=site:on3.com+%22Notre+Dame%22&hl=en-US&gl=US&ceid=US:en"},

    # 9) The Athletic — Notre Dame Football
    {"name": "The Athletic — Notre Dame", "url": "https://news.google.com/rss/search?q=site:theathletic.com+%22Notre+Dame%22+football&hl=en-US&gl=US&ceid=US:en"},

    # 10) Fighting Irish Wire (USA Today)
    {"name": "Fighting Irish Wire", "url": "https://fightingirishwire.usatoday.com/feed/"},

    # General catch-all (Google News)
    {"name": "Google News — Notre Dame Football", "url": "https://news.google.com/rss/search?q=%22Notre+Dame%22+football&hl=en-US&gl=US&ceid=US:en"},
]

# Top-row quick links (buttons). Edit freely; these don’t affect crawling.
STATIC_LINKS = [
    {"label": "Official Site", "href": "https://und.com/sports/football/"},
    {"label": "Schedule", "href": "https://und.com/sports/football/schedule/"},
    {"label": "ND Insider", "href": "https://www.ndinsider.com/"},
    {"label": "One Foot Down", "href": "https://www.onefootdown.com/"},
    {"label": "Slap the Sign", "href": "https://slapthesign.com/"},
    {"label": "Irish Envy Forum", "href": "https://www.irishenvy.com/"},
    {"label": "YouTube — Notre Dame Football", "href": "https://www.youtube.com/channel/UCAMR05qSc5mfhVx20fDyAoQ"},
    {"label": "Reddit — r/notredamefootball", "href": "https://www.reddit.com/r/notredamefootball/"},
]