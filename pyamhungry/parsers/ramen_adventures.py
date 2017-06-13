from lxml.html import fromstring
import requests


# All the xpaths 

# Shared stuff
# Use japanese data for shared stuff 
TABELOG_PRICE         = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[2]/dl[1]/dd/div/p/span/a"""
TABELOG_RATING_TOTAL  = """//*[@id="js-detail-score-open"]/p/b/span"""
TABELOG_RATING_DINNER = """//*[@id="js-header-rating"]/ul/li[1]/div[2]/span[1]/em"""
TABELOG_RATING_LUNCH  = """//*[@id="js-header-rating"]/ul/li[1]/div[2]/span[2]/em"""
TABELOG_HOURS         = """//*[@id="contents-rstdata"]/div[3]/table[1]/tbody/tr[6]/td/p"""
TABELOG_CREDIT        = """//*[@id="contents-rstdata"]/div[3]/table[1]/tbody/tr[9]/td/p"""


# Japanese site xpaths
TABELOG_TITLE_JP      = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[1]/div[1]/div/h2/a/span"""
TABELOG_REST_JP       = """//*[@id="short-comment"]""" # Rest days for restaurant
TABELOG_GENRE_JP      = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[1]/dl[2]/dd/div/div[1]/a/span"""
TABELOG_STATION_JP    = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[1]/dl[1]/dd/div/div[1]/a/span"""
TABELOG_CITY_JP       = """//*[@id="rstdtl-head"]/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div[1]/a/span"""
TABELOG_ADDRESS_JP       = """//*[@id="contents-rstdata"]/div[3]/table[1]/tbody/tr[4]/td/p/span[2]"""

# English site xpaths
TABELOG_TITLE_EN      = """/html/body/article/header/div[1]/div/div[1]/h2/a"""
TABELOG_REST_EN       = """//*[@id="anchor-rd-detail"]/section[1]/table/tbody/tr[7]/td/p"""
TABELOG_GENRE_EN      = """//*[@id="anchor-rd-detail"]/section[1]/table/tbody/tr[2]/td/p/span"""
TABELOG_STATION_EN    = """/html/body/article/header/div[1]/div/div[2]/div/div/dl[1]/dd"""
TABELOG_CITY_EN       = """/html/body/article/header/div[1]/div/div[2]/div/div/dl[1]/dd/div/p/a/span"""
TABELOG_ADDRESS_EN       = """//*[@id="anchor-rd-detail"]/section[1]/table/tbody/tr[4]/td/p[1]"""

def parse_tabelog(url):
	#make sure url points to tabelog
	if len(url.split("/")) <6 or not "tabelog" in url:
		raise ("url does not target tabelog or no store present")
	en_tabe = "http://tabelog.com/en/" + "/".join(url.split("/")[-5:])
	jp_tabe = "http://tabelog.com/" + "/".join(url.split("/")[-5:])
	
	eresp = requests.get(en_tabe)
	edata = eresp.content
	etree = fromstring(edata)

	jresp = requests.get(jp_tabe)
	jdata = jresp.content
	jtree = fromstring(jdata)
	price =  jtree.xpath(TABELOG_PRICE)[0].text.strip("\n ")
	rating_total = jtree.xpath(TABELOG_RATING_TOTAL)[0].text
	rating_dinner = jtree.xpath(TABELOG_RATING_DINNER)[0].text
	rating_lunch = jtree.xpath(TABELOG_RATING_LUNCH)[0].text

	title_jp = jtree.xpath(TABELOG_TITLE_JP)[0].text.strip("\n ")
	genre_jp = [i.text for i in jtree.xpath(TABELOG_GENRE_JP)]
	address_jp = jtree.xpath(TABELOG_ADDRESS_JP)[0].text_content()
	station_jp = jtree.xpath(TABELOG_STATION_JP)[0].text_content()
	city_jp = jtree.xpath(TABELOG_CITY_JP)[0].text_content()
	rest_jp = jtree.xpath(TABELOG_REST_JP)[0].text_content().strip("\n ")

	title_en = etree.xpath(TABELOG_TITLE_EN)[0].text.strip("\n ")
	genre_en = [i.text for i in etree.xpath(TABELOG_GENRE_EN)]
	address_en = etree.xpath(TABELOG_ADDRESS_EN)[0].text_content().strip("\n ")
	station_en = etree.xpath(TABELOG_STATION_EN)[0].text.strip("\n ")
	city_en = etree.xpath(TABELOG_CITY_EN)[0].text_content()
	rest_en = etree.xpath(TABELOG_REST_EN)[0].text_content()

	print("title: {}\n".format(title_jp) + 
		  "Price: {}\n".format(price) + 
		  "Rating: {}, {}, {}\n".format(rating_total, rating_dinner, rating_lunch))

	return {"en": {"title": title_en,
				   "price": price,
				   "rating_total": rating_total,
				   "rating_dinner": rating_dinner, 
				   "rating_lunch": rating_lunch,
				   "genre": genre_en,
				   "city": city_en,
				   "station": station_en, 
				   "address": address_en,
				   "rest"   : rest_en
				}, 
			"jp": {"title": title_jp,
				   "price": price,
				   "rating_total": rating_total,
				   "rating_dinner": rating_dinner, 
				   "rating_lunch": rating_lunch,
				   "genre": genre_jp,
				   "city": city_jp,
				   "station": station_jp, 
				   "address": address_jp,
				   "rest"   : rest_jp
				}
		}

a = parse_tabelog("https://tabelog.com/kyoto/A2601/A260503/26004989/")
print(a)
