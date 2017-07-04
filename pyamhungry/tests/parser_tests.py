import unittest
import os
import yaml
import logging
import sys

from pprint import pprint
import pyamhungry.parsers.tabelog as tabelog

class tabelogNormalizationUnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #setup the answers
        tabelog_data_dir = "test_data/tabelog"
        cls.answers = yaml.load(open(os.path.join(tabelog_data_dir, "answers.yaml"), encoding = "utf-8"))

        # Parse the base tabelog files and generate "raw" data
        epaths = [os.path.join(tabelog_data_dir, i) for i in  os.listdir(tabelog_data_dir) if i.endswith("e.html")]
        jpaths = [os.path.join(tabelog_data_dir, i) for i in  os.listdir(tabelog_data_dir) if i.endswith("j.html")]
        cls.raw_tabelog_parsings = dict()
        for epath, jpath in zip(epaths, jpaths):
            with open(epath, encoding = "utf-8") as e, open(jpath, encoding = "utf-8") as j:
                epage, jpage = e.read(), j.read()
                try:
                    location_data = tabelog.parse_tabelog(epage, jpage)
                except:
                    raise Exception("Failed to parse {}".format(epath))
            cls.raw_tabelog_parsings[os.path.basename(epath[:-6])] = location_data
        print(cls.raw_tabelog_parsings["test1"])

    def test_normalize_price(self):
        log = logging.getLogger("test_normalize_price")
        test1_normalized_price = tabelog.normalize_price(self.raw_tabelog_parsings["test1"])
        log.debug("price_lunch: norm = {}, ans = {}".format(test1_normalized_price["price_lunch"], self.answers["test1"]["en"]["price_lunch"]))
        assert(test1_normalized_price["price_lunch"] == self.answers["test1"]["en"]["price_lunch"])
        log.debug("price_dinner: norm = {}, ans = {}".format(test1_normalized_price["price_dinner"], self.answers["test1"]["en"]["price_dinner"]))
        assert(test1_normalized_price["price_dinner"] == self.answers["test1"]["en"]["price_dinner"])

    def test_normalize_hours(self):
        log = logging.getLogger("test_normalize_hours")
        test1_normalized_hours = tabelog.normalize_hours(self.raw_tabelog_parsings["test1"])
        log.debug("hours: norm = {}, ans = {}".format(test1_normalized_hours, self.answers["test1"]["en"]["hours"]))
        assert(test1_normalized_hours == self.answers["test1"]["en"]["hours"])


    def test_normalize_tel(self):
        log = logging.getLogger("test_normalize_tel")
        test1_normalized_tel = tabelog.normalize_tel(self.raw_tabelog_parsings["test1"])
        log.debug("tel: norm = {}, ans = {}".format(test1_normalized_tel, self.answers["test1"]["en"]["tel"]))
        assert(test1_normalized_tel == self.answers["test1"]["en"]["tel"])

    def test_normalize_address(self):
        log = logging.getLogger("test_normalize_address")
        test1_normalized_address = tabelog.normalize_address_lang(self.raw_tabelog_parsings["test1"])
        log.debug("address: norm = {}, ans = {}".format(test1_normalized_address, 
                                                        {lang: {"address": self.answers["test1"][lang]["address"]} for lang in self.answers["test1"]}))
        for language in self.answers["test1"]:
            res, ans = test1_normalized_address[language]["address"], self.answers["test1"][language]["address"]
            log.debug("address: norm = {}, ans = {}".format(res, ans))
            assert(res == ans)

class tabelogOfflineIntegrationTest(unittest.TestCase):
    def setup(self):
        pass
    
        
    # def test_parser(self):
    #     from pyamhungry.parsers.tabelog import parse_tabelog
    #     tabelog_data_dir = "test_data/tabelog"
    #     epage = [os.path.join(tabelog_data_dir, i) for i in  os.listdir(tabelog_data_dir) if i.endswith("e.html")]
    #     jpage = [os.path.join(tabelog_data_dir, i) for i in  os.listdir(tabelog_data_dir) if i.endswith("j.html")]
    #     answers = yaml.load(open(os.path.join(tabelog_data_dir, "answers.yaml"), encoding = "utf-8"))
    #     for epath, jpath in zip(epage, jpage):
    #         # Get the name of the file
    #         ekey, jkey = os.path.split(epath)[1][:-5], os.path.split(jpath)[1][:-5]
    #         with open(epath, encoding = "utf-8") as e, open(jpath, encoding = "utf-8") as j:
    #             epage, jpage = e.read(), j.read()
    #             try:
    #                 location_data = parse_tabelog(epage, jpage)
    #             except:
    #                 raise Exception("Failed to parse {}".format(epath))

    #         if ekey in answers:
    #             for key in answers[ekey]:
    #                 try:
    #                     assert(location_data.get(key, "en") == answers[ekey][key])
    #                 except:
    #                     print("----------------------")
    #                     print("Using key {}".format(key))
    #                     print("Expected {} in data, got {}".format([answers[ekey][key]], [location_data.get(key, "en")]))
    #                     pprint(location_data.data_dict)
    #                     print("----------------------")

    #                     raise Exception("Dictionaries are not equal")


    #         if jkey in answers:
    #             try:
    #                 assert(location_data.get(jkey, "jp") == answers[jkey])
    #             except:
    #                 print("Data")
    #                 pprint(location_data.data_dict["jp"])
    #                 print("Answer")
    #                 pprint(answers[ekey])
    #                 raise Exception("Dictionaries are not equal")




if __name__ == "__main__":
    logging.basicConfig(stream = sys.stderr)
    #logging.getLogger("test_normalize_price").setLevel(logging.DEBUG)
    logging.getLogger("test_normalize_address").setLevel(logging.DEBUG)
    unittest.main()
    # t = tabelogNormalizationTest()


    # t = tabelogOfflineIntegrationTest()
    # t.test_parser()