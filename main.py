import base64
import subprocess
import sys
import time
import urllib2
import xml.etree.ElementTree as ET

class Node(object):
	def __init__(self, name):
		self.name = name
		self.children = []

	def add_child(self, obj):
		self.children.append(obj)

class SearchResult(object):
	def __init__(self):
		self.web_count = 0
		self.url_set = []

	def add_url(self, url):
		self.url_set.append(url)

	def set_web_count(self, web_count):
		self.web_count = int(web_count)

def build_categorization_scheme_tree():
	"""Build Hierarchical Classification Tree"""
	computers = Node("Computers")
	computers.add_child(Node("Hardware"))
	computers.add_child(Node("Programming"))

	health = Node("Health")
	health.add_child(Node("Diseases"))
	health.add_child(Node("Fitness"))

	sports = Node("Sports")
	sports.add_child(Node("Basketball"))
	sports.add_child(Node("Soccer"))
	
	root = Node("Root")
	root.add_child(computers)
	root.add_child(health)
	root.add_child(sports)

	return root

def parse_queries(cat_file, node_categories):
	file_name = "Probers/" + cat_file + ".txt"
	q_dict = {} # key: category, value: a list of queries for that category.
	file_obj = open(file_name)
	for line in file_obj:
		l = line.strip('\n').split()
		category = l[0]
		query = " ".join(l[1:])
		if category not in q_dict:
			q_dict[category] = [query]
		else:
			q_dict[category].append(query)
	file_obj.close()
	node_categories[cat_file] = q_dict.keys()
	return q_dict

def parse_xml(xml_str):
	root = ET.fromstring(xml_str)
	ns = root.tag.split('}')[0].strip('{')
	nsmap = {'n':ns}
	entry = root.find('n:entry', namespaces = nsmap)
	content = entry.find('n:content', namespaces = nsmap)
	properties = content.getchildren()[0]

	# set search_info_obj.web_count
	search_info_obj = SearchResult()
	for item in properties.getchildren():
		tag = item.tag.split('}')[1]
		text = item.text
		if (tag == 'WebTotal'):
			search_info_obj.set_web_count(text)

	# set search_info_obj.url_set
	link = entry.find('n:link', namespaces = nsmap)
	inline = link.getchildren()[0]
	feed = inline.find('n:feed', namespaces = nsmap)
	subEntries = feed.findall('n:entry', namespaces = nsmap)
	topCount = 0
	for subEntry in subEntries:
		subContent = subEntry.find('n:content', namespaces = nsmap)
		subProperties = subContent.getchildren()[0]
		for item in subProperties.getchildren():
			tag = item.tag.split('}')[1]
			text = item.text
			if tag == 'Url' and topCount < 4:
				search_info_obj.add_url(text)
		topCount = topCount + 1

	return search_info_obj

def request_bing_result(siteInput, queryInput):
	""" 
	Returns: SearchResult object: has web_count & url_set (contain the top-4 pages url).
	"""
	queries = queryInput.split()
	queryUrl = ""
	for q in queries:
		queryUrl = queryUrl + "%20" + q
	bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a' + siteInput + queryUrl + '%27&$top=10&$format=Atom'
	accountKey = account_key
	accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
	headers = {'Authorization': 'Basic ' + accountKeyEnc}
	req = urllib2.Request(bingUrl, headers = headers)
	response = urllib2.urlopen(req)
	xml_str = response.read()
	result = parse_xml(xml_str)
	return result

def ECoverage(category, database_url):
	"""Get the estimated coverage of database for the given category."""
	query_l = query_dict[category] # retreive the list of queries for the given category.
	matches = 0
	for query in query_l:
		matches += request_bing_result(database_url, query).web_count
	return matches

def ESpecificity(ec, parent_es, ec_sum):
	"""Get the estimated specificity of database for category c.

	Args:
		ec: category c's estimated coverage.
		parent_es: parent(category c)'s estimated specificit.
		ec_sum: the sum of estimated coverage of all children of category's parent.
	"""
	es = (parent_es * ec) / float(ec_sum)
	return es

def classify(c, d_url, t_ec, t_es, c_es):
	"""Implement the QProber Algorithm.
	
	Args:
		c (Node): category's node.
		d_url (str): databse's URL.
		t_es (int): the estimated specificity threshold.
		t_ec (int): the estimated coverage threshold.
		c_es (int): the ESpecificity of databse for category c.
	
	Returns:
		result: a list of categories which the database is assigned to.

	"""
	result = [c.name]
	ec_vector = {}
	for child in c.children:
		ec_vector[child.name] = ECoverage(child.name, d_url)
	ec_sum = sum(ec_vector.values())

	for child in c.children:
		ec = ec_vector[child.name]
		es = ESpecificity(ec, c_es, ec_sum)
		print "Specificity for category:%s is %s" % (child.name, str(es))
		print "Coverage for category:%s is %s" % (child.name, str(ec))
		if ec >= t_ec and es >= t_es:
			result.append(classify(child, d_url, t_ec, t_es, es))

	return result

def get_sample_queries(category_node, classify_result):
	"""Get queries for sample-C-D, where C is the category node, D is the database."""
	queries = []
	if category_node == "Root": # level-0 node.
		for visited_node in classify_result[::-1]: # all visited node are subcategories of "Root".
			if visited_node in node_categories:
				for category in node_categories[visited_node]:
					queries += query_dict[category]
	elif category_node in ["Computers", "Health", "Sports"]: # level-1 nodes.
		for category in node_categories[category_node]:
			queries += query_dict[category]
	return queries

def get_words_lynx(url):
	"""
	Returns:
		a set of words. e.g. ["a", "word", "mum"], no duplicate.
	"""
	# Get page content using lynx.
	try:
		content = subprocess.check_output(['lynx', '--dump', url])
	except subprocess.CalledProcessError, e:
		return False
	end = content.find('Reference')
	content = content[:end]

	# Remove unwanted characters from content.
	output = ''
	recording = True
	wrotespace = False
	for i in range(len(content)):
		c = content[i]
		if recording:
			if c == '[':
				recording = False # stop recording when occur with '['.
				if not wrotespace:
					output += ' '
					wrotespace = True
			elif c.isalpha():
				output += c.lower() # convert all words to lowercase.
				wrotespace = False
			elif not wrotespace:
				output += ' '
				wrotespace = True
		else:
			if c == ']':
				recording = True

	# remove duplicate words, sort them alphabetically. 
	words = list(set(output.split()))
	words.sort()

	return words

def docs_to_inverted_file(category, database, urls):
	inverted_file = {}
	for q_urls in urls:
		for url in q_urls:
			words = get_words_lynx(url)
			if not words: # can't access url.
				continue
			for term in words:
				if term not in inverted_file:
					inverted_file[term] = 1
				else:
					inverted_file[term] += 1
	output_file(category, database, inverted_file)

def output_file(category, database, inverted_file):
	file_name = category + "-" + database + ".txt"
	txt_file = open(file_name, "w")
	key_list = inverted_file.keys()
	key_list.sort()
	for term in key_list:
		output = term + "#" + str(inverted_file[term]) + "#\n"
		txt_file.write(output)
	txt_file.close()

def get_path_list(result):
	if len(result) == 1:
		return result
	paths = []
	for i in range(1, len(result)):
		child_paths = get_path_list(result[i])
		for path in child_paths:
			paths.append(result[0] + '/' + path)
	return paths
	
def content_summary(visited_cnodes, database):
	for category in visited_cnodes:
		print "Creating Content Summary for:%s" % category
		# Get category associated queries.
		query_l = get_sample_queries(category, visited_cnodes)
		# Retrive top-4 pages for each query.
		existed_urls = []
		inverted_file = {}
		num = len(query_l)
		for i in range(0, num):
			print "%s/%s" % (str(i + 1), str(num))
			# get each query's top-4 page's urls.
			top4_page_urls = request_bing_result(database, query_l[i]).url_set
			for url in top4_page_urls:
				if url not in existed_urls:
					if isinstance(url, unicode):
						url = url.encode('ascii', 'ignore')
					print "Getting page: %s\n\n" % url
					existed_urls.append(url)
					words = get_words_lynx(url)
					if not words: # can't access url.
						continue
					for term in words:
						if term not in inverted_file:
							inverted_file[term] = 1
						else:
							inverted_file[term] += 1
		output_file(category, database, inverted_file)

if __name__ == "__main__":
	# Get command line arguments.
	if len(sys.argv) != 5:
		raise Exception("Invalid command line arguments.")
	account_key = sys.argv[1] # Bing API Account Key.
	t_es = float(sys.argv[2]) # Estimated Specificity Threshold.
	t_ec = float(sys.argv[3]) # Estimated Coverage Threshold.
	db_url = sys.argv[4] # Database's URL.
	
	# Define the hierachical categorization scheme's tree.
	root = build_categorization_scheme_tree()

	# Build query dictionary.
	category_files = ["Root", "Computers", "Health", "Sports"]
	node_categories = {}
	query_dict = {}
	for cat_file in category_files:
		dic = parse_queries(cat_file, node_categories)
		query_dict = dict(query_dict.items() + dic.items())

	# Get classification result and print it.
	print "\n\nClassifying..."
	result = classify(root, db_url, t_ec, t_es, 1) # ESpecificity(D, "root") = 1.
	print "\n\nClassification:"
	paths = get_path_list(result)
	for path in paths:
		print path

	# get visited category nodes.
	visited_cnodes = []
	for path in paths:
		cnode_l = path.split('/')
		for cnode in cnode_l:
			if cnode in node_categories:
				visited_cnodes.append(cnode)
	visited_cnodes = list(set(visited_cnodes))

	# Build Content Summary for Database
	print "\n\nExtracting topic content summaries..."
	content_summary(visited_cnodes, db_url)

