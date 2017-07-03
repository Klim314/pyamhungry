class LocationEntry:
	def __init__(self, data_dict, default_lang = "en"):
		# Data dict containing the following indices:
		# default (default values), <en, jp, etc language codes>
		self.data_dict = data_dict
		self.default_lang = default_lang
		self.normalized = self.data_dict["normalized"]

	def __repr__(self):
		return ("<Class LocationEntry \n"
			    "{}>".format(self.data_dict))
	def __getitem__(self, key):
		return self.get(key)

	def get(self, key, lang = None):
		if not lang:
			lang = self.default_lang
		if key in self.normalized:
			return self.normalized[key]
		else:
			return self.data_dict[lang][key]


			
