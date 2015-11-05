import urllib2
import base64
import xml.etree.ElementTree as ET

def request_bing_result(siteInput, queryInput):
#	siteInput = "fifa.com"
#	queryInput = "avi file"
	queries = queryInput.split()
	queryUrl = ""

	for q in queries:
		queryUrl = queryUrl + "%20" + q

	bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + siteInput + queryUrl + '%27&$top=10&$format=Atom'
	#Provide your account key here
	accountKey = 'QXWZenjIChRK55ligQ1BjQEJBEEsHXvZ1b4E3PGUkJY='

	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	xml_str = response.read()
	#content contains the xml/json response from Bing. 
	#print content
	searched_info = {}

	searched_info[queryInput] = parse_xml(xml_str)

	return searched_info



def parse_xml(xml_str):
	root = ET.fromstring(xml_str)
	ns = root.tag.split('}')[0].strip('{')
	nsmap = {'n':ns}
	entry = root.find('n:entry', namespaces = nsmap)

#	import pdb;pdb.set_trace()
	content = entry.find('n:content', namespaces = nsmap)
	properties = content.getchildren()[0]
	search_info_obj = Search_result()

	for item in properties.getchildren():
		tag = item.tag.split('}')[1]
		text = item.text
		if (tag == 'WebTotal'):
			search_info_obj.set_web_count(text)

	link = entry.find('n:link', namespaces = nsmap)
	inline = link.getchildren()[0]
	feed = inline.find('n:feed', namespaces = nsmap)
	subEntries = feed.findall('n:entry', namespaces = nsmap)
	url_set = []
	topCount = 0

	for subEntry in subEntries:
		subContent = subEntry.find('n:content', namespaces = nsmap)
		subProperties = subContent.getchildren()[0]

		for item in subProperties.getchildren():
			tag = item.tag.split('}')[1]
			text = item.text
			if tag == 'Url' and text not in url_set and topCount < 4:
				search_info_obj.add_url(text)
		topCount = topCount + 1

	return search_info_obj

class Search_result(object):
	def __init__(self):
		self.web_count = 0
		self.url_set = []

	def add_url(self, url):
		self.url_set.append(url)

	def set_web_count(self, web_count):
		self.web_count = web_count
