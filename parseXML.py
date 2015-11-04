import xml.etree.ElementTree as ET

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

