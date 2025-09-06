# feeds.py — safe defaults; customize later
# This file is imported by /feeds.json; errors here should never crash server.py

# Buttons across the top of the page
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

# Feed source names to show in the filter dropdown (informational only)
FEEDS = [
    {"name": "247Sports"},
    {"name": "CBS Sports"},
    {"name": "ESPN"},
    {"name": "Fighting Irish Wire"},
    {"name": "Blue & Gold (On3)"},
    {"name": "The Athletic"},
    {"name": "Irish Sports Daily"},
    {"name": "NDNation"},
    {"name": "InsideNDSports (Rivals)"},
    {"name": "One Foot Down"},
]