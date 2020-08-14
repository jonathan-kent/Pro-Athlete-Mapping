import config
import urllib.request
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from time import sleep
from selenium import webdriver

def get_locations(url):
    # get page html
    page = urllib.request.urlopen(url)
    pg_bytes = page.read()
    pg_str = pg_bytes.decode("utf8")
    page.close()
    # extract players birthplace city and state/country
    pattern = "\{(\"id\":\"\d{1,}\",\"uid.*?)\"slug\""
    players = re.finditer(pattern, pg_str)
    birthplaces = []
    for player in players:
        player_str = player.groups()[0]
        pattern = "birthPlace\":(\{[A-z \'\-\.\":,]{0,}\},)"
        match = re.search(pattern, player_str)
        birthplace = ""
        if match is not None:
            birthplace = match.groups()[0]
        birthplaces.append(birthplace)
    # extract players names
    pattern = "\"fullName\":\"([A-z \-\'\.ñá]{1,})\",\"displayName"
    full_names = re.finditer(pattern, pg_str)
    cities = []
    states = []
    countries = []
    for place in birthplaces:
        if "city" in place:
            pattern = "city\":\"([A-z \-\.\']{1,})\""
            city = re.search(pattern, place).groups()[0]
            cities.append(city)
        else:
            cities.append("")
        if "state" in place:
            pattern = "state\":\"([A-z \-\.\']{1,})\""
            state = re.search(pattern, place).groups()[0]
            states.append(state)
        else:
            states.append("")
        if "country" in place:
            pattern = "country\":\"([A-z \-\.\']{1,})\""
            country = re.search(pattern, place).groups()[0]
            countries.append(country)
        else:
            countries.append("")
    names = []
    for full_name in full_names:
        name = full_name.groups()[0]
        names.append(name)
    return (names, cities, states, countries)


def get_coords(names, cities, states, countries):
    geolocator = Nominatim(user_agent=config.email)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    lat_longs = []
    for idx, name in enumerate(names):
        location = ""
        if len(cities[idx]) > 0:
            location = location + cities[idx]
            if len(states[idx]) > 0:
                location = location + ", " + states[idx]
            if len(countries[idx]) > 0 and countries[idx] != "CAN":
                location = location + ", " + countries[idx]

            print(location)
            coords = geocode(location)
            try:
                print(str(coords.latitude)+","+str(coords.longitude))
                lat_longs.append(str(coords.latitude)+","+str(coords.longitude))
            except:
                if len(states[idx]) > 0:
                    location = cities[idx]+", "+states[idx]
                else:
                    location = cities[idx]
                coords = geocode(location)
                try:
                    print(str(coords.latitude)+","+str(coords.longitude))
                    lat_longs.append(str(coords.latitude)+","+str(coords.longitude))
                except:
                    try:
                        coords = get_coords_alt(location)
                        print(coords)
                        lat_longs.append(coords)
                    except:
                        print("NO COORDINATES")
                        lat_longs.append(",")
        else:
            lat_longs.append(",")
    return lat_longs


def get_coords_alt(location):
    driver = webdriver.Chrome(config.driver_path)
    location = location.replace(" ", "%20")
    url = "https://www.google.com/search?q="+location+"+latitude+and+longitude"
    driver.get(url)
    sleep(1)
    coords = driver.find_element_by_class_name("Z0LcW.XcVN5d").text
    lat_long = coords.split(", ")
    if lat_long[0][-1] == "S":
        lat_long[0] = "-"+lat_long[0]
    if lat_long[1][-1] == "W":
        lat_long[1] = "-"+lat_long[1]
    latitude = lat_long[0].replace("° ", "")
    latitude = latitude[:-1]
    longitude = lat_long[1].replace("° ", "")
    longitude = longitude[:-1]
    driver.quit()
    return latitude+","+longitude


def create_csv(league, names, cities, states, countries, coords):
    csv = open(league+".csv", "w")
    header = "name,latitude,longitude,city,state,country\n"
    csv.writelines(header)
    for idx, name in enumerate(names):
        entry = name+","+coords[idx]+","+cities[idx]+","+states[idx]+","+countries[idx]+"\n"
        csv.writelines(entry)
    csv.close()


def fill_missing(league):
    csv = open(league+".csv", "r")
    entries = csv.readlines()
    csv.close()
    csv = open(league+"_filled.csv", "w")
    for entry in entries:
        parts = entry.split(",")
        if len(parts[1]) < 1:
            print(parts[0])
            birthplace = get_birthplace(parts[0])
            coords = ","
            if len(birthplace) > 1:
                coords = get_birthplace_coords(birthplace)
            else:
                print("NO COORDINATES")
            entry = parts[0]+","+coords+","+parts[3]+","+parts[4]+","+parts[5]
        csv.writelines(entry)
    csv.close()


def get_birthplace(player):
    player = player.replace(" ", "_")
    url = "https://en.wikipedia.org/wiki/"+player
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}
    request = urllib.request.Request(url, headers=header)
    page = None
    try:
        page = urllib.request.urlopen(request)
    except:
        return ""
    pg_bytes = page.read()
    pg_str = pg_bytes.decode("utf8")
    page.close()
    pattern = "<br \/>(.*?)<\/td>"
    match = re.search(pattern, pg_str)
    if match is None:
        return ""
    #print(match.groups()[0])
    pattern = ">(.*?)<\/a>"
    matches = re.finditer(pattern, match.groups()[0])
    # birthplace without a link
    pattern = "<\/a>([A-z ,\.\'\-]{1,})$"
    match = re.search(pattern, match.groups()[0])
    no_link = ""
    if match is not None:
        no_link = match.groups()[0]
    birthplace = ""
    for match in matches:
        if len(birthplace) > 0:
            birthplace = birthplace + ", " + match.groups()[0]
        else:
            birthplace = match.groups()[0]
    birthplace = birthplace + no_link
    return birthplace


def get_birthplace_coords(birthplace):
    geolocator = Nominatim(user_agent=config.email)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    coords = geocode(birthplace)
    lat_long = ""
    try:
        print(birthplace)
        print(str(coords.latitude)+","+str(coords.longitude))
        lat_long = str(coords.latitude)+","+str(coords.longitude)
    except:
        try:
            coords = get_coords_alt(birthplace)
            print(str(coords.latitude)+","+str(coords.longitude))
            lat_long = str(coords.latitude)+","+str(coords.longitude)
        except:
            print("NO COORDINATES")
            lat_long = ","
    return lat_long


def fill_missing2(league):
    csv = open(league+".csv", "r")
    entries = csv.readlines()
    csv.close()
    for entry in entries:
        parts = entry.split(",")
        if len(parts[1]) < 1:
            coords = ","
            if has_wiki_page(parts[0]):
                print(parts[0])


def has_wiki_page(player):
    player = player.replace(" ", "_")
    url = "https://en.wikipedia.org/wiki/"+player
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}
    request = urllib.request.Request(url, headers=header)
    page = None
    try:
        page = urllib.request.urlopen(request)
    except:
        return False
    pg_bytes = page.read()
    pg_str = pg_bytes.decode("utf8")
    page.close()
    if "NFL" in pg_str:
        return True
    else:
        return False


nhl_names = []
nhl_cities = []
nhl_states = []
nhl_countries = []
for i in range(1,31):
    url = "http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/"+str(i)+"/roster"
    roster_info = get_locations(url)
    nhl_names.extend(roster_info[0])
    nhl_cities.extend(roster_info[1])
    nhl_states.extend(roster_info[2])
    nhl_countries.extend(roster_info[3])
# Golden Knights Roster
roster_info = get_locations("http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/37/roster")
nhl_names.extend(roster_info[0])
nhl_cities.extend(roster_info[1])
nhl_states.extend(roster_info[2])
nhl_countries.extend(roster_info[3])
nhl_coords = get_coords(nhl_names, nhl_cities, nhl_states, nhl_countries)
create_csv("nhl", nhl_names, nhl_cities, nhl_states, nhl_countries, nhl_coords)

nba_names = []
nba_cities = []
nba_states = []
nba_countries = []
for i in range(1,31):
    url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/"+str(i)+"/roster"
    roster_info = get_locations(url)
    nba_names.extend(roster_info[0])
    nba_cities.extend(roster_info[1])
    nba_states.extend(roster_info[2])
    nba_countries.extend(roster_info[3])
nba_coords = get_coords(nba_names, nba_cities, nba_states, nba_countries)
create_csv("nba", nba_names, nba_cities, nba_states, nba_countries, nba_coords)

mlb_names = []
mlb_cities = []
mlb_states = []
mlb_countries = []
for i in range(1,31):
    url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/"+str(i)+"/roster"
    roster_info = get_locations(url)
    mlb_names.extend(roster_info[0])
    mlb_cities.extend(roster_info[1])
    mlb_states.extend(roster_info[2])
    mlb_countries.extend(roster_info[3])
mlb_coords = get_coords(mlb_names, mlb_cities, mlb_states, mlb_countries)
create_csv("mlb", mlb_names, mlb_cities, mlb_states, mlb_countries, mlb_coords)

nfl_names = []
nfl_cities = []
nfl_states = []
nfl_countries = []
for i in range(1,31):
    url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/"+str(i)+"/roster"
    roster_info = get_locations(url)
    nfl_names.extend(roster_info[0])
    nfl_cities.extend(roster_info[1])
    nfl_states.extend(roster_info[2])
    nfl_countries.extend(roster_info[3])
#Texans and Ravens Rosters
roster_info = get_locations("http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/33/roster")
nfl_names.extend(roster_info[0])
nfl_cities.extend(roster_info[1])
nfl_states.extend(roster_info[2])
nfl_countries.extend(roster_info[3])
roster_info = get_locations("http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/34/roster")
nfl_names.extend(roster_info[0])
nfl_cities.extend(roster_info[1])
nfl_states.extend(roster_info[2])
nfl_countries.extend(roster_info[3])
nfl_coords = get_coords(nfl_names, nfl_cities, nfl_states, nfl_countries)
create_csv("nfl", nfl_names, nfl_cities, nfl_states, nfl_countries, nfl_coords)

fill_missing("nhl")
fill_missing("nba")
fill_missing("mlb")
fill_missing("nfl")
