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
		answers = yaml.load(open(os.path.join(tabelog_data_dir, "answers.yaml"), encoding = "utf-8"))
		for epath, jpath in zip(epage, jpage):
			# Get the name of the file
			ekey, jkey = os.path.split(epath)[1][:-5], os.path.split(jpath)[1][:-5]
			with open(epath, encoding = "utf-8") as e, open(jpath, encoding = "utf-8") as j:
				epage, jpage = e.read(), j.read()
			location_data = parse_tabelog(epage, jpage)

			if ekey in answers:
				for key in answers[ekey]:
					try:
						assert(location_data.get(key, "en") == answers[ekey][key])
					except:
						print("----------------------")
						print("Using key {}".format(key))
						print("Expected {} in data, got {}".format([answers[ekey][key]], [location_data.get(key, "en")]))
						pprint(location_data.data_dict)
						print("----------------------")

						raise Exception("Dictionaries are not equal")


			if jkey in answers:
				try:
					assert(location_data.get(jkey, "jp") == answers[jkey])
				except:
					print("Data")
					pprint(location_data.data_dict["jp"])
					print("Answer")
					pprint(answers[ekey])
					raise Exception("Dictionaries are not equal")




if __name__ == "__main__":
	t = tabelogNormalizationTest()


	t = tabelogOfflineIntegrationTest()
	t.test_parser()