# feeds.py — Notre Dame Football sources + quick links

FEEDS = [
    # Broad aggregators
    {"name": "\"Notre Dame football\" - Google News", "url": "https://news.google.com/rss/search?q=%22Notre+Dame+football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Notre Dame football - BingNews", "url": "https://www.bing.com/news/search?q=Notre+Dame+football&format=RSS"},

    # Major outlets (RSS where possible; otherwise via Google News site: queries)
    {"name": "CBS Sports — Notre Dame", "url": "https://www.cbssports.com/rss/headlines/college-football/notre-dame/"},
    {"name": "ESPN — Notre Dame (GN)", "url": "https://news.google.com/rss/search?q=site%3Aespn.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "247Sports — Notre Dame (GN)", "url": "https://news.google.com/rss/search?q=site%3A247sports.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "On3 — Blue & Gold (GN)", "url": "https://news.google.com/rss/search?q=site%3Ablueandgold.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "The Athletic — Notre Dame (GN)", "url": "https://news.google.com/rss/search?q=site%3Atheathletic.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Yahoo Sports — Notre Dame (GN)", "url": "https://news.google.com/rss/search?q=site%3Asports.yahoo.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "NBC Sports — Notre Dame (GN)", "url": "https://news.google.com/rss/search?q=site%3Anbcsports.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},

    # Local / team beat
    {"name": "ND Insider / South Bend Tribune (GN)", "url": "https://news.google.com/rss/search?q=site%3Asouthbendtribune.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Fighting Irish Wire (USA Today)", "url": "https://fightingirishwire.usatoday.com/feed/"},
    {"name": "Irish Breakdown (SI/FanNation)", "url": "https://www.si.com/api/v2/feeds/fannation/college/notredame/rss"},
    {"name": "Inside ND Sports (Rivals) (GN)", "url": "https://news.google.com/rss/search?q=site%3Ainsideindsports.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Blue & Gold — On3 Headlines (GN)", "url": "https://news.google.com/rss/search?q=site%3Aon3.com+%22Blue%20%26%20Gold%22+%22Notre%20Dame%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Irish Sports Daily (GN)", "url": "https://news.google.com/rss/search?q=site%3Airishsportsdaily.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "One Foot Down (SB Nation)", "url": "https://www.onefootdown.com/rss/index.xml"},
    {"name": "FightingIrish.com (official) (GN)", "url": "https://news.google.com/rss/search?q=site%3Afightingirish.com+football&hl=en-US&gl=US&ceid=US:en"},

    # Extras / national perspectives
    {"name": "AP News — ND (GN)", "url": "https://news.google.com/rss/search?q=site%3Aapnews.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "FOX Sports — ND (GN)", "url": "https://news.google.com/rss/search?q=site%3Afoxsports.com+%22Notre+Dame%20football%22&hl=en-US&gl=US&ceid=US:en"},

    # Reddit (fresh chatter)
    {"name": "Reddit — r/NotreDame (football search)", "url": "https://www.reddit.com/r/NotreDame/search.rss?q=football&restrict_sr=on&sort=new"},
    {"name": "Reddit — r/CFB (Notre Dame search)", "url": "https://www.reddit.com/r/CFB/search.rss?q=%22Notre%20Dame%20football%22&restrict_sr=on&sort=new"},
]

# Quick buttons for the header
STATIC_LINKS = [
    {"label": "Schedule", "url": "https://fightingirish.com/sports/football/schedule/"},
    {"label": "Roster", "url": "https://fightingirish.com/sports/football/roster/"},
    {"label": "AP Poll", "url": "https://apnews.com/hub/ap-top-25-college-football-poll"},
    {"label": "Coaches Poll", "url": "https://www.usatoday.com/sports/ncaaf/polls/coaches-poll/"},
    {"label": "ND Insider", "url": "https://www.southbendtribune.com/sports/notre-dame/"},
    {"label": "Irish Envy", "url": "https://www.irishenvy.com/forums/notre-dame-football.3/"},
    {"label": "Fighting Irish Wire", "url": "https://fightingirishwire.usatoday.com/"},
    {"label": "One Foot Down", "url": "https://www.onefootdown.com/"},
    {"label": "Blue & Gold (On3)", "url": "https://www.on3.com/teams/notre-dame-fighting-irish/"},
    {"label": "Inside ND Sports (Rivals)", "url": "https://notredame.rivals.com/"},
    {"label": "247Sports ND", "url": "https://247sports.com/college/notre-dame/"},
    {"label": "CBS ND", "url": "https://www.cbssports.com/college-football/teams/ND/notre-dame-fighting-irish/"},
    {"label": "Reddit", "url": "https://www.reddit.com/r/NotreDame/"},
]