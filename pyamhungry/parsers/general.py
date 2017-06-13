from urllib.parse import urlparse
from supleks import parse_supleks
from tabelog import parse_tabelog


def parse(url):
	print("TESTING THIS SHIT")
	url = urlparse(url)
	print(url.netloc)
	if url.netloc.endswith(".supleks.jp"):
		return parse_supleks(url)
	elif url.netloc.endswith("tabelog.jp"):
		print(url.netloc)
		return parse_tabelog(url)
	else:
		print("No handler found for URL : {}".format(url))
		return None