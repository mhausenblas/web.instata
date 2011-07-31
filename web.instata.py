""" 
 Takes CSV as input and generates a HTML document with the data items marked up with Schema.org terms.

@author: Michael Hausenblas, http://sw-app.org/mic.xhtml#i
@since: 2011-07-30
@status: init
"""

import os
import sys
sys.path.insert(0, os.getcwd() + '/lib/rdflib')
sys.path.insert(0, os.getcwd() + '/lib/rdfextras')
sys.path.insert(0, os.getcwd() + '/lib')
import getopt
import StringIO
import shutil
import datetime
import rdflib
import rdfextras
from rdflib import *
from rdflib.plugin import PluginException
import rdflib_schemaorg_csv
from bottle import SimpleTemplate

rdflib.plugin.register('sparql', rdflib.query.Processor, 'sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result, 'sparql.query', 'SPARQLQueryResult')

class InstantWebDataPublisher(object):
	
	DEBUG = True
	
	# some config stuff we gonna need:
	TEMPLATES_DIR = 'templates/'
	MAPPINGS_DIR = 'mappings/'
	OUTPUT_DIR = 'output/'
	
	DBPEDIA2SCHEMA = 'dbpedia-2011-07-31.rdf'
	BASE_TEMPLATE = TEMPLATES_DIR + 'base.tpl'
	BASE_STYLE_FILE = 'web.instata-style.css'
	JQUERY_UI_CSS = 'jquery-ui-1.8.4.custom.css'
	DTABLE_CSS = 'd_table.css'
	DTABLE_JUI_CSS = 'd_table_jui.css'
	JQUERY = 'jquery.js'
	JQUERY_DTABLE = 'jquery.dataTables.min.js'
	
	# internal stuff
	NAMESPACES = {	'schema' : Namespace('http://schema.org/'), 
					'scsv' : Namespace('http://purl.org/NET/schema-org-csv#'), 
					'dc' : Namespace('http://purl.org/dc/terms/'),
					'owl' : Namespace('http://www.w3.org/2002/07/owl#'),
					'rdfs' : Namespace('http://www.w3.org/2000/01/rdf-schema#')
	}
	
	# content creation queries:
	HEADER_QUERY = """SELECT ?cell ?colTitle WHERE { 
					?table a scsv:Table ;
						   scsv:row ?row .
					?row a scsv:HeaderRow ; 
						 scsv:cell ?cell .
					?cell dc:title ?colTitle .
	}"""
	
	ROWS_QUERY = """SELECT ?row ?cell ?cellType ?val WHERE { 
					?table a scsv:Table ;
						   scsv:row ?row .
					?row a scsv:Row ; 
						scsv:cell ?cell .
					?cell a ?cellType ;
						  rdf:value ?val .
	}"""
	
	MATCHED_TERMS_QUERY = """SELECT ?match ?prop WHERE { 
					 ?match ?prop <%s> .
	}"""
	

	
	def __init__(self):
		self.g = None
		self.doc_url = ""
		self.base_uri = ""
		if not os.path.exists(InstantWebDataPublisher.OUTPUT_DIR): # make sure output dir exists
			os.makedirs(InstantWebDataPublisher.OUTPUT_DIR)

	def parse(self, doc_url, base_uri):
		self.doc_url = doc_url
		self.base_uri = base_uri
		self.g = ConjunctiveGraph("IOMemory")
		self.g.parse(location=doc_url, format="schemaorg_csv", csv_file_URI=base_uri)
		
		# construct the table header and body out of the input data
		if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG] querying input data ...')
		res = self.g.query(InstantWebDataPublisher.HEADER_QUERY, initNs=InstantWebDataPublisher.NAMESPACES)
		self.table_header = []
		# ?cell ?colTitle
		for r in res:
			if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG]  row: %s' %(r))
			self.table_header.append((r[0], r[1]))

		self.table_rows = []
		self.terms = []
		res = self.g.query(InstantWebDataPublisher.ROWS_QUERY, initNs=InstantWebDataPublisher.NAMESPACES)		
		# ?row ?cell ?cellType ?val
		for r in res:
			if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG]  row: %s' %(r))
			self.table_rows.append((r[0], r[1], r[2], r[3]))
			if r[2] not in self.terms:
				self.terms.append(r[2])
		
	def load_mappings(self):
		print('[web.instata] loading DBpedia2Schema.org mapping ...')
		self.dbpedia2schema = ConjunctiveGraph("IOMemory")
		self.dbpedia2schema.parse(location=InstantWebDataPublisher.MAPPINGS_DIR + InstantWebDataPublisher.DBPEDIA2SCHEMA)
		print('[web.instata] got DBpedia2Schema.org mapping!')

		# going through the cell types from the parse and render steps to find matching terms in DBpedia:
		self.matches = {}
		for t in self.terms:
			q = (InstantWebDataPublisher.MATCHED_TERMS_QUERY %(str(t)))
			print('[web.instata] trying to find a match for %s' %(str(t)))
			res = self.dbpedia2schema.query(q, initNs=InstantWebDataPublisher.NAMESPACES)
			# ?match ?prop
			for r in res:
				if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG]  row: %s' %(r))
				self.matches[str(t)] = (str(r[1]), str(r[0]))
		print('[web.instata] match(es) found: %s' %(self.matches))

	def render(self):
		tpl = SimpleTemplate(name=InstantWebDataPublisher.BASE_TEMPLATE)
		wi_last_update = datetime.datetime.utcnow().replace(microsecond = 0)
		return tpl.render(ds_name=self.doc_url.split('/')[-1].split('.')[0],
						theader=sorted(self.table_header, key=lambda cell: cell[0]), 
						trows=sorted(self.table_rows, key=lambda cell: cell[1]),
						aliases=self.matches, 
						wi_last_update=str(wi_last_update) + ' (UTC)')

	def instata(self, doc_url, base_uri):
		# get the data and render it
		self.parse(doc_url, base_uri)
		self.load_mappings() # try to find matches for Schema.org terms in the mapping files
		render_result = self.render()
		
		# output the result
		result_file_name = InstantWebDataPublisher.OUTPUT_DIR + doc_url.split('/')[-1].split('.')[0] + ".html"
		result_file = open(result_file_name, 'w')
		result_file.write(render_result)
		result_file.close()
		
		# copy style files (CSS and JS)
		shutil.copy2(InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.BASE_STYLE_FILE, InstantWebDataPublisher.OUTPUT_DIR + InstantWebDataPublisher.BASE_STYLE_FILE)
		shutil.copy2(InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.JQUERY_UI_CSS, InstantWebDataPublisher.OUTPUT_DIR + InstantWebDataPublisher.JQUERY_UI_CSS)
		shutil.copy2(InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.DTABLE_CSS, InstantWebDataPublisher.OUTPUT_DIR + InstantWebDataPublisher.DTABLE_CSS)
		shutil.copy2(InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.DTABLE_JUI_CSS, InstantWebDataPublisher.OUTPUT_DIR + InstantWebDataPublisher.DTABLE_JUI_CSS)
		shutil.copy2(InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.JQUERY, InstantWebDataPublisher.OUTPUT_DIR + InstantWebDataPublisher.JQUERY)
		shutil.copy2(InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.JQUERY_DTABLE, InstantWebDataPublisher.OUTPUT_DIR + InstantWebDataPublisher.JQUERY_DTABLE)
	
		return result_file_name

	def dump_data(self, format='turtle'):
		if self.g:
			self.g.bind('schema', InstantWebDataPublisher.NAMESPACES['schema'], True)
			self.g.bind('scsv', InstantWebDataPublisher.NAMESPACES['scsv'], True)
			self.g.bind('dc', InstantWebDataPublisher.NAMESPACES['dc'], True)
			return self.g.serialize(format=format)
		else:
			return None

def usage():
	print("Usage: python web.instata.py -p {path to CSV file} {base URI for publishing}")
	print("Example: python web.instata.py -p test/potd_0.csv http://example.org/instata/potd_0")

if __name__ == "__main__":
	iwdp = InstantWebDataPublisher()
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hpd", ["help", "publish", "dump"])
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit()
			elif opt in ("-p", "--publish"):
				(doc_url, base_uri) = (args[0], args[1])
				print("[web.instata] processing [%s] with base URI [%s] " %(doc_url, base_uri))
				r = iwdp.instata(doc_url, base_uri)
				print("[web.instata] result is now available at [%s]" %(r))
			elif opt in ("-d", "--dump"):
				(doc_url, base_uri) = (args[0], args[1])
				print("processing [%s] with base URI [%s] " %(doc_url, base_uri))
				iwdp.parse(doc_url, base_uri)
				print(iwdp.dump_data())
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)