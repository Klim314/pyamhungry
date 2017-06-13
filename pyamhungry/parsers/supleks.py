from lxml.html import fromstring
import requests
from collections import defaultdict
from urllib.parse import urlparse, urlunparse
import re
import json

# TODO
# Handle url when given another page (photos, etc)


# All the xpaths 

# Shared stuff
TEST          = """//*[@id="data-table"]/tr"""
STORE_NAME    = """.//*/td/strong/span"""
ADDRESS       = """.//td/span"""
PHONE         = """.//td"""
OPENING_HOURS = """.//td"""
REST          = """.//td"""
SEATS         = """.//td"""
SMOKING       = """.//td"""
STATION       = """.//td/div"""
MENU          = """//*[@id="shop-data-menu"]/p[1]"""
RATING = """//*[@id="shop-status"]/div/div[1]"""

key_re = re.compile(r"""(\w+)db\.supleks.jp\/s\/(\d+)""")


def from_url_supleks(url):
    url = urlparse(url)
    if not url.netloc.endswith("supleks.jp"):
        raise ("url does not target suplecks or no store present")
    store_path = re.search(r"(/s/\d+)", url.path)
    keys = key_re.search(url).groups()
    if not all(keys):
        raise (missing)
    url = url._replace(path = store_path.group() + ".html") 
    url = urlunparse(url)
    print(url)
    resp = requests.get(url)
    data = resp.content.decode("UTF-8")
    res = parse_supleks(data)
    res["key"] = key
    return res


def parse_supleks(data):
    tree = fromstring(data)

    json_data = defaultdict(str, json.loads(tree.xpath(r'//*[@id="contents-basic"]/div/script[3]/text()')[0]))

    city = "Tokyo"
    dat = {i.findall(".//th")[0].text_content():i for i in tree.xpath(TEST) if i.findall(".//th")}

    keys = {"最寄り駅": ("station", STATION),
            "住所"   : ("address", ADDRESS),
            "定休日" : ("rest",    REST),
            "喫煙"   : ("smoking", SMOKING)
    }
    for key, (json_key, xpath) in keys.items():
        if key in dat:
            #print(key, dat[key].findall(".//td")[0], dat[key].findall(xpath))
            json_data[json_key] = dat[key].findall(xpath)[0].text_content()
    
    menu = [i.text for i in tree.xpath(MENU)]

    return {"source": "suplecks",
            "en": defaultdict(str, {

                                }),
            "jp": defaultdict(str, {"title"        : json_data["name"],
                                    "rating_total" : json_data["aggregateRating"]["ratingValue"],
                                    "rating_dinner": json_data["aggregateRating"]["ratingValue"], 
                                    "rating_lunch" : json_data["aggregateRating"]["ratingValue"],
                                    "city"         : city,
                                    "station"      : json_data["station"], 
                                    "address"      : json_data["address"],
                                    "rest"         : json_data["rest"],
                                    "smoking"      : json_data["smoking"],
                                    "menu"         : menu,
                                    "price"        : json_data["priceRange"],
                                    "genre"        : json_data["servesCuisine"]

                                }),
            }


# def parse_supleks(url):
#     if "supleks.jp" not in url:
#         raise ("url does not target suplecks or no store present")
#     resp = requests.get(url)
#     data = resp.content.decode("UTF-8")
    
#     tree = fromstring(data)
#     title = tree.xpath(STORE_NAME)[0].text
#     rating_dinner = rating_lunch = rating_total = tree.xpath(RATING)[0].text
#     city = "Tokyo"
#     station = tree.xpath(STATION)[0].text_content()
#     address = tree.xpath(ADDRESS)[0].text_content()
#     rest = tree.xpath(REST)[0].text
#     smoking = tree.xpath(SMOKING)[0].text
#     menu = [i.text for i in tree.xpath(MENU)]

#     json_data = json.loads(tree.xpath(r'//*[@id="contents-basic"]/div/script[3]/text()')[0])

#     return {"source": "suplecks",
#             "en": defaultdict(str, {

#                                 }),
#             "jp": defaultdict(str, {"title"        : title,
#                                     "rating_total" : rating_total,
#                                     "rating_dinner": rating_dinner, 
#                                     "rating_lunch" : rating_lunch,
#                                     "city"         : city,
#                                     "station"      : station, 
#                                     "address"      : address,
#                                     "rest"         : rest,
#                                     "smoking"      : smoking,
#                                     "menu"         : menu,
#                                     "price"        : json_data["priceRange"],
#                                     "genre"        : json_data["servesCuisine"]

#                                 }),
#             }

if __name__ == "__main__":    
    print(from_url_supleks("https://currydb.supleks.jp/s/72899.html"))
    a = from_url_supleks("https://ramendb.supleks.jp/s/81832.html")
    print(a)

    print(from_url_supleks("https://currydb.supleks.jp/s/97141.html"))
    



    print(from_url_supleks("https://currydb.supleks.jp/s/72899/photo/exterior"))