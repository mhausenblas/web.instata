""" 
 Takes CSV as input and generates a HTML document with the data items marked up with Schema.org terms.

@author: Michael Hausenblas, http://sw-app.org/mic.xhtml#i
@since: 2011-07-30
@status: init
"""
import sys
sys.path.insert(0, 'lib')
import getopt
import StringIO
import urllib
import urllib2
import uuid
import rdflib
import rdflib_schemaorg_csv

class InstantWebDataPublisher(object):
	def __init__(self):
		self.g = None
		self.doc_url = ""

	def parse(self, doc_url, base_uri):
		self.doc_url = doc_url
		self.g = rdflib.Graph()
		self.g.parse(location=doc_url, format="schemaorg_csv", csv_file_URI=base_uri)

	def dump_data(self, format='turtle'):
		if self.g:
			self.g.bind('schema', 'http://schema.org/', True)
			self.g.bind('scsv', 'http://purl.org/NET/schema-org-csv#', True)
			self.g.bind('dcterms', 'http://purl.org/dc/terms/', True)
			return self.g.serialize(format=format)
		else:
			return None

def usage():
	print("Usage: python web.instata.py -p {path to CSV file} {base URI for publishing} ")
	print("Example: python web.instata.py -p test/potd_0.csv http://example.org/instata/potd_0")

if __name__ == "__main__":
	iwdp = InstantWebDataPublisher()
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hp", ["help", "publish"])
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit()
			elif opt in ("-p", "--publish"):
				(doc_url, base_uri) = (args[0], args[1])
				print("processing [%s] with base URI [%s] " %(doc_url, base_uri))
				iwdp.parse(doc_url, base_uri)
				print(iwdp.dump_data())
				pass
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)