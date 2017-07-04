from lxml.html import fromstring
import requests
from collections import defaultdict
from pandas import read_html
import re
from ..models.LocationEntry import LocationEntry
from pprint import pprint



# All the xpaths 

# Shared stuff
# Use japanese data for shared stuff 
TABELOG_PRICE         = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[2]/dl[1]/dd/div/p/span/a"""
TABELOG_RATING_TOTAL  = """//*[@id="js-detail-score-open"]/p/b/span"""
TABELOG_RATING_DINNER = """//*[@id="js-header-rating"]/ul/li[1]/div[2]/span[1]/em"""
TABELOG_RATING_LUNCH  = """//*[@id="js-header-rating"]/ul/li[1]/div[2]/span[2]/em"""


# Japanese site xpaths
TABELOG_TITLE_JP      = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[1]/div[1]/div/h2/a/span"""
TABELOG_STATION_JP    = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[1]/dl[1]/dd/div/div[1]/a/span"""
TABELOG_CITY_JP       = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div[1]/a/span"""

# English site xpaths
TABELOG_TITLE_EN      = """/html/body/article/header/div[1]/div/div[1]/h2/a"""
TABELOG_STATION_EN    = """/html/body/article/header/div[1]/div/div[2]/div/div/dl[1]/dd"""
TABELOG_CITY_EN       = """/html/body/article/header/div[1]/div/div[2]/div/div/dl[1]/dd/div/p/a/span"""

key_regex = re.compile(r"""tabelog\.com\/(\w+)\/(\w+)\/(\w+)\/(\w+)""")


# Normalization regexes
NORMALIZE_DINNER_PRICE_REGEX = re.compile(r"""Dinner:\s+.([\d,]+)..([\d,]+)""")
NORMALIZE_LUNCH_PRICE_REGEX = re.compile(r"""Lunch:\s+.([\d,]+)..([\d,]+)""")

NORMALIZE_GENERIC_HOURS_REGEX = re.compile(r"""(\d+:\d+).(\d+:\d+)""")
NORMALIZE_DINNER_HOURS_REGEX = re.compile(r"""夜\s(\d+:\d+).(\d+:\d+)""")
NORMALIZE_LUNCH_HOURS_REGEX = re.compile(r"""昼\s(\d+:\d+).(\d+:\d+)""")

NORMALIZE_TEL_REGEX = re.compile(r"""\d+-\d+-\d+""")

def from_url_tabelog(url):
    if len(url.split("/")) <6 or not "tabelog" in url:
        raise ("url does not target tabelog or no store present")
    en_tabe = "http://tabelog.com/en/" + "/".join(url.split("/")[-5:])
    jp_tabe = "http://tabelog.com/" + "/".join(url.split("/")[-5:])
    key = key_regex.search(jp_tabe).groups()
    if not all(key):
        print(key)
        raise
    eresp = requests.get(en_tabe)
    edata = eresp.content

    jresp = requests.get(jp_tabe)
    jdata = jresp.content

    
    res = parse_tabelog(edata, jdata)
    res["key"] = key
    return res

# Normalization functions. These handle the textual data, converting them into a more structured form
# Normalization functions assume that the jdata is being passed unless the function ends with _lang
def normalize_price(data_dict):
    """
    normalize_price:
    Given a data_dict, generates structured price values from the japanese data
    args:

    returns
    dictionary object of structure:
        {"price_dinner": (<num low>, <num hight>, <str currencyunit>),
         "price_lunch": (<num low>, <num hight>, <str currencyunit>)
        }
    if no price is given, store None instead
    """
    dinner = NORMALIZE_DINNER_PRICE_REGEX.search(data_dict["jp"]["price"])
    lunch = NORMALIZE_LUNCH_PRICE_REGEX.search(data_dict["jp"]["price"])
    res = {"price_dinner": None,
           "price_lunch" : None}
    if dinner:
        datum = dinner.groups()
        datum = [int(i.replace(",", "")) for i in datum]
        res["price_dinner"] = (datum[0], datum[1], "yen")

    if lunch:
        datum = lunch.groups()
        datum = [int(i.replace(",", "")) for i in datum]
        res["price_lunch"] = (datum[0], datum[1], "yen")
    return res

def normalize_hours(data_dict):
    string = data_dict["jp"]["hours"]
    res = {"dinner" : None,
           "lunch"  : None,
           "generic": None}
    # Try grabbing day/night first, then just grab any
    dinner = NORMALIZE_DINNER_HOURS_REGEX.search(string)
    lunch = NORMALIZE_LUNCH_HOURS_REGEX.search(string)
    # Use a generic finder if not split by time
    if not dinner and not lunch:
        generic = NORMALIZE_GENERIC_HOURS_REGEX.findall(string)
        if not generic:
            data_dict["normalized"]["hours"] = res
            return
        res["generic"] = generic
    if dinner:
        res["dinner"] = dinner.groups()
    if lunch:
        res["lunch"] = lunch.groups()
    return res
    
def normalize_tel(data_dict):
    datum = NORMALIZE_TEL_REGEX.findall(data_dict["jp"]["tel"])
    return datum[0]

def normalize_generic(data_dict, key, func):
    for lang in data_dict:
        if lang == "normalized":
            continue
        data_dict[lang][key] = func(data_dict[lang][key])


def normalize_address_lang(data_dict):
    res = {language: dict() for language in data_dict}
    for language in data_dict:
        res[language]["address"] = data_dict[language]["address"].split()[0]
    return res


def normalize(data_dict):
    """
    Normalizes the data dict in a new "normalized" key, converting the unstructured data to structured data
        Probably a better idea to normalize to
    """

    #Create a normalized dataset to hold all fields that will be normalized
    normalized = dict()
    # Normalize_price
    normalized.update(normalize_price(data_dict))


    # normalize_hours(data_dict)
    # normalize_tel(data_dict)
    # # Revamp the normalization system later
    # normalize_address(data_dict)
    # pprint(data_dict)
    # normalize_generic(data_dict, "rating_total", lambda x: float(x) if x != "-" else 0)
    # normalize_generic(data_dict, "rating_lunch", lambda x: float(x) if x != "-" else 0)
    # normalize_generic(data_dict, "rating_dinner", lambda x: float(x) if x != "-" else 0)

    location_data = LocationEntry(data_dict)
    return location_data


def get_price(df):
    """
    Given a tabelog_english data frame, extracts the first price row found
        This was done because of multiple potential keys
    """
    #print(list(df.index))
    for key in df.index:
        if key.startswith("Budget"):
            if df.loc[key][1]:
                return df.loc[key][1]
    return ""


def parse_tabelog(edata, jdata):
    """
    Takes in english and japanese html data and returns a raw, parsing of
    the data within
    """

    jtree = fromstring(jdata)
    etree = fromstring(edata)

    # All the various Xpaths to things which are easier grabbed here
    rating_total = jtree.xpath(TABELOG_RATING_TOTAL)[0].text
    rating_dinner = jtree.xpath(TABELOG_RATING_DINNER)[0].text
    rating_lunch = jtree.xpath(TABELOG_RATING_LUNCH)[0].text
    city_en = etree.xpath(TABELOG_CITY_EN)[0].text
    city_jp = jtree.xpath(TABELOG_CITY_JP)[0].text


    jtabelog_tables = read_html(jdata, match = '店名|席数', index_col = 0)
    jstore_data = jtabelog_tables[0].append(jtabelog_tables[1])

    etabelog_tables = read_html(edata, match = 'TEL/reservation|Private use', index_col = 0)
    estore_data = etabelog_tables[0].append(etabelog_tables[1])

    price = get_price(estore_data)


    # Key for dict, rowname for japanese and english sites
    categories = (("title", "店名", "Restaurant name"),
                  ("genre", "ジャンル", "Categories"),
                  ("tel", "TEL", "TEL/reservation"),
                  ("address", "住所", "Addresses"),
                  ("transport", "交通手段", "Transportation"),
                  ("hours", "営業時間", "Operating Hours"),
                  ("rest", "定休日", "Shop holidays"),
                  ("smoking", "禁煙・喫煙", "Non-smoking/smoking"))

    res = {"en": defaultdict(str, {"price": price,
                   "rating_total": rating_total,
                   "rating_dinner": rating_dinner, 
                   "rating_lunch": rating_lunch,
                   "city": city_en,
                }), 
            "jp": defaultdict(str, {"price": price,
                   "rating_total": rating_total,
                   "rating_dinner": rating_dinner, 
                   "rating_lunch": rating_lunch,
                   "city": city_jp,
                })
        }

    for key, jcat, ecat in categories:
        try:
            res["en"][key] = estore_data.loc[ecat][1]
        except:
            print(estore_data)
            raise
        try:
            res["jp"][key] = jstore_data.loc[jcat][1]
        except:
            print(jstore_data)
            raise

    # Various cleanup steps to be added in the future
    return res
    

if __name__ == "__main__":
    from pprint import pprint

    print(from_url_tabelog("https://tabelog.com/kyoto/A2601/A260503/26013688/"))

    a = from_url_tabelog("https://tabelog.com/kyoto/A2601/A260503/26004989/")
    pprint(a)

    pprint(from_url_tabelog("https://tabelog.com/en/tokyo/A1305/A130503/13114695/"))
