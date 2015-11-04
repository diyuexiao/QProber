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
	webTotal = parse_xml_for_match_count(xml_str)

	return webTotal


def parse_xml_for_match_count(xml_str):
	root = ET.fromstring(xml_str)
	#tree = ET.parse('res.xml')
	#root = tree.getroot()

	ns = root.tag.split('}')[0].strip('{')
	nsmap = {'n':ns}
	entry = root.find('n:entry', namespaces = nsmap)
	content = entry.find('n:content', namespaces = nsmap)
	properties = content.getchildren()[0]

	for item in properties.getchildren():
		tag = item.tag.split('}')[1]
		text = item.text
		if (tag == 'WebTotal'):
			webTotal = text

	return webTotal