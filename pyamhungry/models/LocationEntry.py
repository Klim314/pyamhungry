

class LocationEntry:
	def __init__(self, data_dict, default_lang = "en"):
		self.data_dict = data_dict
		self.default_lang = default_lang

	def get(self, key, lang = None):
		if not lang:
			lang = self.default_lang

			
