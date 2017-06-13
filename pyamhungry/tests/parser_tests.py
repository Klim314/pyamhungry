import pyamhungry
import unittest
import os
import yaml
from pprint import pprint

class tabelogNormalizationTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_hours_parser(self):
		pass

	def test_budget_parser(self):
		pass

class tabelogOfflineIntegrationTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_parser(self):
		from pyamhungry.parsers.tabelog import parse_tabelog
		tabelog_data_dir = "test_data/tabelog"
		epage = [os.path.join(tabelog_data_dir, i) for i in  os.listdir(tabelog_data_dir) if i.endswith("e.html")]
		jpage = [os.path.join(tabelog_data_dir, i) for i in  os.listdir(tabelog_data_dir) if i.endswith("j.html")]
		answers = yaml.load(open(os.path.join(tabelog_data_dir, "answers.yaml")))
		for epath, jpath in zip(epage, jpage):
			with open(epath, encoding = "utf-8") as e, open(jpath, encoding = "utf-8") as j:
				epage, jpage = e.read(), j.read()
			data_dict = parse_tabelog(epage, jpage)
			pprint(data_dict)



if __name__ == "__main__":
	t = tabelogNormalizationTest()


	t = tabelogOfflineIntegrationTest()
	t.test_parser()