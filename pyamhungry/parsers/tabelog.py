from lxml.html import fromstring
import requests
from collections import defaultdict
from pandas import read_html
import re



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
NORMALIZE_DINNER_BUDGET_REGEX = re.compile(r"""Dinner:\s+.([\d,]+)..([\d,]+)""")
NORMALIZE_LUNCH_BUDGET_REGEX = re.compile(r"""Lunch:\s+.([\d,]+)..([\d,]+)""")

NROMALIZE_GENERIC_HOURS_REGEX = re.compile(r"""(\d+:\d+).(\d+:\d+)""")
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
# All normalization functions assume that the jdata is being passed
def normalize_budget(string):
    """
    Handles a budget string, producing a structure as per below:
    {dinner_low: (1000, "yen"),
     dinner_high: (2000, "yen"),
     dinner_mean: (1500, "yen"),
     lunch_low: (1000, "yen"),
     lunch_high: (2000, "yen"),
     lunch_mean: (1500, "yen"),
    }
    """
    dinner = NORMALIZE_DINNER_BUDGET_REGEX.search(string)
    lunch = NORMALIZE_LUNCH_BUDGET_REGEX.search(string)
    res = dict()
    if dinner:
        datum = dinner.groups()
        datum = [int(i.replace(",", "")) for i in datum]
        res["dinner"] = (datum[0], datum[1], "yen")

    if lunch:
        datum = lunch.groups()
        datum = [int(i.replace(",", "")) for i in datum]
        res["lunch"] = (datum[0], datum[1], "yen")

    return res

def normalize_hours(string):
    res = {"dinner" : None,
           "lunch"  : None,
           "generic": None}
    # Try grabbing day/night first, then just grab any
    dinner = NORMALIZE_DINNER_HOURS_REGEX.search(string)
    lunch = NORMALIZE_LUNCH_HOURS_REGEX.search(string)
    # Use a generic finder if not split by time
    if not dinner and not lunch:
        generic = NROMALIZE_GENERIC_HOURS_REGEX.findall(string)
        if not generic:
            return res
        res["generic"] = generic
        return res
    if dinner:
        res["dinner"] = dinner.groups()
    if lunch:
        res["lunch"] = lunch.groups()
    return res
    

def normalize_address(string):
    pass

def normalize_tel(string):
    datum = NORMALIZE_TEL_REGEX.findall(string)
    return datum


def normalize(data_dict):
    """
    Normalizes the data dict in a new "normalized" key, converting the unstructured data to structured data
        Probably a better idea to normalize to
    """
    normalized = dict()
    for key, item in data_dict["jp"].items():
        normalized[key] = item
    normalized["budget"] = normalize_budget(data_dict["jp"]["budget"])
    normalized["hours"] = normalize_hours(data_dict["jp"]["hours"])
    normalized["tel"] = normalize_tel(data_dict["jp"]["tel"])
    data_dict["normalized"] = normalized


def get_budget(df):
    """
    Given a tabelog_english data frame, extracts the first budget row found
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
    Takes in english and japanese html data
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

    budget = get_budget(estore_data)


    # Key for dict, rowname for japanese and english sites
    categories = (("title", "店名", "Restaurant name"),
                  ("genre", "ジャンル", "Categories"),
                  ("tel", "TEL", "TEL/reservation"),
                  ("address", "住所", "Addresses"),
                  ("transport", "交通手段", "Transportation"),
                  ("hours", "営業時間", "Operating Hours"),
                  ("rest", "定休日", "Shop holidays"),
                  ("smoking", "禁煙・喫煙", "Non-smoking/smoking"))

    res = {"en": defaultdict(str, {"budget": budget,
                   "rating_total": rating_total,
                   "rating_dinner": rating_dinner, 
                   "rating_lunch": rating_lunch,
                   "city": city_en,
                }), 
            "jp": defaultdict(str, {"budget": budget,
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
    normalize(res)
    return res["normalized"]
    return res

if __name__ == "__main__":
    from pprint import pprint

    print(from_url_tabelog("https://tabelog.com/kyoto/A2601/A260503/26013688/"))

    a = from_url_tabelog("https://tabelog.com/kyoto/A2601/A260503/26004989/")
    pprint(a)

    pprint(from_url_tabelog("https://tabelog.com/en/tokyo/A1305/A130503/13114695/"))
