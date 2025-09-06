# feeds.py — Source list + quick links (Notre Dame Football)

FEEDS = [
    # Broad news aggregators
    {"name": "Google News — Notre Dame Football", "url": "https://news.google.com/rss/search?q=Notre+Dame+football&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Bing News — Notre Dame Football", "url": "https://www.bing.com/news/search?q=Notre+Dame+football&format=RSS"},

    # Major outlets
    {"name": "ESPN Notre Dame", "url": "https://www.espn.com/college-football/team/_/id/87/notre-dame-fighting-irish"},
    {"name": "CBS Sports — Notre Dame", "url": "https://www.cbssports.com/rss/headlines/college-football/notre-dame/"},
    {"name": "247Sports — Notre Dame", "url": "https://247sports.com/college/notre-dame/HeadlinesFeed.rss"},
    {"name": "On3 Blue & Gold", "url": "https://www.on3.com/teams/notre-dame-fighting-irish/news/feed/"},
    {"name": "The Athletic — Notre Dame", "url": "https://theathletic.com/team/notre-dame-fighting-irish/feed/"},

    # Independent/fan
    {"name": "One Foot Down (SB Nation)", "url": "https://www.onefootdown.com/rss/index.xml"},
    {"name": "Irish Sports Daily", "url": "https://www.irishsportsdaily.com/rss/articles"},
    {"name": "ND Nation", "url": "https://www.ndnation.com/feed/"},
    {"name": "Inside ND Sports (Rivals)", "url": "https://notredame.rivals.com/rss"},
    {"name": "Fighting Irish Wire (USA Today)", "url": "https://fightingirishwire.usatoday.com/feed/"},

    # Reddit
    {"name": "Reddit — r/NotreDame", "url": "https://www.reddit.com/r/NotreDame/.rss"},
    {"name": "Reddit — r/CFB (ND search)", "url": "https://www.reddit.com/r/CFB/search.rss?q=Notre%20Dame%20football&restrict_sr=on&sort=new"},
]

# Buttons at top of the site
STATIC_LINKS = [
    {"label": "Schedule", "url": "https://fightingirish.com/sports/football/schedule/"},
    {"label": "Roster", "url": "https://fightingirish.com/sports/football/roster/"},
    {"label": "AP Poll", "url": "https://apnews.com/hub/ap-top-25-college-football-poll"},
    {"label": "Coaches Poll", "url": "https://www.usatoday.com/sports/ncaaf/polls/coaches-poll/"},
    {"label": "CBS ND", "url": "https://www.cbssports.com/college-football/teams/ND/notre-dame-fighting-irish/"},
    {"label": "247Sports ND", "url": "https://247sports.com/college/notre-dame/"},
    {"label": "Inside ND Sports (Rivals)", "url": "https://notredame.rivals.com/"},
    {"label": "Reddit", "url": "https://www.reddit.com/r/NotreDame/"},
]