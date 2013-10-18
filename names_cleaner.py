"""This app cleans up the names given a csv file. 
Modify the variable CSV_FILE in the code to 
specify the filename"""

__author__ = 'Ajay Ranipeta'

# imports
import urllib
import json
import csv

CSV_FILE = 'names_and_ref.csv'

SEARCH_BASE_URL = 'http://eol.org/api/search/1.0.json?q=%s'
PAGES_BASE_URL = 'http://eol.org/api/pages/1.0/%s.json'

names_input = []
names_output = []
names_status = []
names_array = []

def read_csv():
	with open(CSV_FILE, 'rb') as csvfile:
		namesreader = csv.reader(csvfile)
		for row in namesreader:
			names_input.append(row[0])

def check_name_with_eol(name):
	try:
		encoded_name = urllib.quote(name)
		search_url = SEARCH_BASE_URL % encoded_name
		name_search = json.load(urllib.urlopen(search_url))

		if name_search['totalResults'] == 0:
			return None

		page_id = name_search['results'][0]['id']
		page_url = PAGES_BASE_URL % page_id
		page_search = json.load(urllib.urlopen(page_url))

		return page_search['taxonConcepts'][0]['canonicalForm']
	except Exception, e:
		return None


def clean_name(name):
	# 1. get rid of the "1", "2" and "." along with a combination of " v " and " a "
	name = name.strip('12.').replace(' v ', '').replace(' a ', '')

	# 2. now get rid of the trailing " sp" after a Genus name
	if name.endswith(' sp'):
		name = name[0:-3]

	# 3. Let's return it
	return name.strip(' .')

def remove_author_name(name):
	try:
		# 1. remove the last word first 
		name = (name[0:name.rindex(' ')]).strip()

		# 2. check if we now end up with an "&" at the end
		#    in that case, we have 2 authors.
		#    Let's remove the second one now
		if name.endswith('&'):
			name = name[0:-2]
			name = (name[0:name.rindex(' ')]).strip()

		# 3. check if we now end up with an " (ref" at the end
		#    in that case, we have 2 authors.
		#    Let's remove the second one now
		if name.endswith('(ref'):
			name = name[0:-5]
			name = (name[0:name.rindex(' ')]).strip()

		# 4. Let's return it
		return name
	except Exception, e:
		# We have a single name. Let's return that.
		return name.strip()

def process_names():
	for name in names_input:
		print 'Checking ' + name

		initial_name = name
		
		# 1. Let's do a first pass and remove random chars 
		name = clean_name(name)

		valid_name = None

		var = 1
		while var == 1:
			# print ' checking with: ' + name
			valid_name = check_name_with_eol(name)
			if valid_name != None:
				names_output.append(valid_name)
				names_array.append([ initial_name, valid_name ])
				# print '  got name: ' + valid_name
				break

			name = remove_author_name(name)

			if name.find(' ') < 0:
				break

def write_csv():
	with open('cleanedup.csv', 'wb') as csvfile:
		outfile = csv.writer(csvfile)
		outfile.writerow([ 'Initial name', 'Cleaned up' ])
		for row in names_array:
			outfile.writerow(row)



print '\n\nReading names...\n'
read_csv()
process_names()
print '\n\nWriting names...'
write_csv()
print 'Done'
