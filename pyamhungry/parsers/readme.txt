This folder contains the parsers for the various food websites
Each parser is named parse_<target> and returns a dictionary of the following structure
	Note. Empty fields will return an empty string

	{"source": "<source>",
	"en": {"title"        : title,
	       "rating_total" : rating_total,
           "rating_dinner": rating_dinner, 
	       "rating_lunch" : rating_lunch,
	       "city"         : city,
	       "station"      : station, 
	       "address"      : address,
	       "rest"         : rest,
	       "smoking"      : smoking,
	       "menu"         : menu,
	       "price"        : json_data["priceRange"],
	       "genre"        : json_data["servesCuisine"]
	                    }
	"jp": {"title"        : title,
	       "rating_total" : rating_total,
	       "rating_dinner": rating_dinner, 
	       "rating_lunch" : rating_lunch,
	       "city"         : city,
	       "station"      : station, 
	       "address"      : address,
	       "rest"         : rest,
	       "smoking"      : smoking,
	       "menu"         : menu,
	       "price"        : json_data["priceRange"],
	       "genre"        : json_data["servesCuisine"]
	                    }
	}