from .tabelog import parse_tabelog, from_url_tabelog
from .supleks import parse_supleks, from_url_supleks
from urllib.parse import urlparse, urlunparse

def from_url(url):
	url = urlparse(url)
	if url.netloc.endswith(".supleks.jp"):
		return from_url_supleks(urlunparse(url))
	elif url.netloc.endswith("tabelog.com"):
		return from_url_tabelog(urlunparse(url))
	else:
		print("No handler found for URL : {}".format(url))

