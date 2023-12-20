logo_table = {
    "Atlanta Hawks": "<:hawks:1186728259354898564>",
    "Boston Celtics": "<:celtics:1186728253105389619>",
    "Brooklyn Nets": "<:nets:1186728279202332682>",
    "Charlotte Hornets": "<:hornets:1186728261816946750>",
    "Chicago Bulls": "<:bulls:1186728249473118208>",
    "Cleveland Cavaliers": "<:cavaliers:1186728251993899108>",
    "Dallas Mavericks": "<:mavericks:1186728277939867729>",
    "Denver Nuggets": "<:nuggets:1186728281672777790>",
    "Detroit Pistons": "<:pistons:1186728287750340679>",
    "Golden State Warriors": "<:warriors:1186732386638106684>",
    "Houston Rockets": "<:rockets:1186732366899724318>",
    "Indiana Pacers": "<:pacers:1186728944284737567>",
    "Los Angeles Clippers": "<:clippers:1186728254598565928>",
    "Los Angeles Lakers": "<:lakers:1186728270079733850>",
    "Memphis Grizzlies": "<:grizzlies:1186728257144500254>",
    "Miami Heat": "<:heat:1186728261091340318>",
    "Milwaukee Bucks": "<:bucks:1186728248252571818>",
    "Minnesota Timberwolves": "<:timberwolves:1186728294989713408>",
    "New Orleans Pelicans": "<:pelicans:1186728286387195987>",
    "New York Knicks": "<:knicks:1186728268276174999>",
    "Oklahoma City Thunder": "<:thunder:1186732311631364136>",
    "Orlando Magic": "<:magic:1186732333630501044>",
    "Philadelphia 76ers": "<:76ers:1186728245589184594>",
    "Phoenix Suns": "<:suns:1186728954762113054>",
    "Portland Trail Blazers": "<:trailblazers:1186728958633459794>",
    "Sacramento Kings": "<:kings:1186728933396332595>",
    "San Antonio Spurs": "<:spurs:1186728291181277294>",
    "Toronto Raptors": "<:raptors:1186732262071472269>",
    "Utah Jazz": "<:jazz:1186728263440138381>",
    "Washington Wizards": "<:wizards:1186732218199052329>"
}


def get_key(val):
    for key, value in logo_table.items():
        if val == value:
            return key
    return None
