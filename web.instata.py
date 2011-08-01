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
try:
    import json
except ImportError:
    import simplejson as json
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
	
	DEBUG = False
	
	# some config stuff we gonna need:
	TEMPLATES_DIR = 'templates/'
	MAPPINGS_DIR = 'mappings/'
	OUTPUT_DIR = 'output/'
	
	DBPEDIA2SCHEMA = 'dbpedia-2011-07-31.rdf'
	BASE_TEMPLATE = 'base.tpl'
	BASE_STYLE_FILE = 'web.instata-style.css'
	JQUERY_UI_CSS = 'jquery-ui-1.8.4.custom.css'
	DTABLE_CSS = 'd_table.css'
	DTABLE_JUI_CSS = 'd_table_jui.css'
	JQUERY = 'jquery.js'
	JQUERY_DTABLE = 'jquery.dataTables.min.js'
	
	# internal stuff
	NAMESPACES = {	'c' : Namespace('#'), 
					'schema' : Namespace('http://schema.org/'), 
					'scsv' : Namespace('http://purl.org/NET/schema-org-csv#'), 
					'dc' : Namespace('http://purl.org/dc/terms/'),
					'owl' : Namespace('http://www.w3.org/2002/07/owl#'),
					'rdfs' : Namespace('http://www.w3.org/2000/01/rdf-schema#')
	}

	# config query:
	CONFIG_QUERY = """SELECT ?config ?key ?value WHERE {  ?config ?key ?value .}"""


	
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
		self.config = None
		self.doc_url = ""
		self.base_uri = ""
		self.schema_matching = [InstantWebDataPublisher.DBPEDIA2SCHEMA]
		self.matches = {}
		if not os.path.exists(InstantWebDataPublisher.OUTPUT_DIR): # make sure output dir exists
			os.makedirs(InstantWebDataPublisher.OUTPUT_DIR)
			
	def load_config(self, config_file_name):
		self.config = ConjunctiveGraph("IOMemory")
		self.config.parse(location=config_file_name, format="n3")
		res = self.config.query(InstantWebDataPublisher.CONFIG_QUERY, initNs=InstantWebDataPublisher.NAMESPACES)
		self.schema_matching = [] # make sure to reset the default (DBpedia if config is evaluated)
		# ?config ?key ?value
		for r in res:
			key = str(r[1])
			val = str(r[2])
			if 'csv_input' in key: self.doc_url = val
			if 'output_base_uri' in key: self.base_uri = val
			if 'schema_matching' in key: self.schema_matching.append(val)
			if 'templates_dir' in key: InstantWebDataPublisher.TEMPLATES_DIR = val
			if 'mappings_dir' in key: InstantWebDataPublisher.MAPPINGS_DIR = val
			if 'output_dir' in key: InstantWebDataPublisher.OUTPUT_DIR = val
			if 'base_template' in key: InstantWebDataPublisher.BASE_TEMPLATE = val
			if 'base_style_file' in key: InstantWebDataPublisher.BASE_STYLE_FILE = val
		if InstantWebDataPublisher.DEBUG:	
			print('csv_input = %s' %self.doc_url)
			print('output_base_uri = %s' %self.base_uri)
			print('schema_matching = %s' %self.schema_matching)
			print('templates_dir = %s' %InstantWebDataPublisher.TEMPLATES_DIR)
			print('mappings_dir = %s' %InstantWebDataPublisher.MAPPINGS_DIR)
			print('output_dir = %s' %InstantWebDataPublisher.OUTPUT_DIR)
			print('base_template = %s' %InstantWebDataPublisher.BASE_TEMPLATE)
			print('base_style_file = %s' %InstantWebDataPublisher.BASE_STYLE_FILE)

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
		for m in self.schema_matching: # defaults to DBpedia; can be overwritten by c:schema_matching in the config file
			print('[web.instata] loading %s mapping ...' %(InstantWebDataPublisher.MAPPINGS_DIR + m))
			self.dbpedia2schema = ConjunctiveGraph("IOMemory")
			self.dbpedia2schema.parse(location=InstantWebDataPublisher.MAPPINGS_DIR + m)
			print('[web.instata] got %s mapping!' %(InstantWebDataPublisher.MAPPINGS_DIR + m))

			# going through the cell types from the parse and render steps to find matching terms in DBpedia:
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
		tpl = SimpleTemplate(name=InstantWebDataPublisher.TEMPLATES_DIR + InstantWebDataPublisher.BASE_TEMPLATE)
		wi_last_update = datetime.datetime.utcnow().replace(microsecond = 0)
		return tpl.render(ds_name=self.doc_url.split('/')[-1].split('.')[0],
						theader=sorted(self.table_header, key=lambda cell: cell[0]), 
						trows=sorted(self.table_rows, key=lambda cell: cell[1]),
						aliases=self.matches, 
						wi_last_update=str(wi_last_update) + ' (UTC)')

	def instata(self, doc_url, base_uri):
		# get the data and render it
		self.parse(doc_url, base_uri)
		if len(self.schema_matching) > 0 : # schema matching is enabled
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
			
	def validate(self, doc_url, base_uri):
		# make sure we have the column heads available:
		self.parse(doc_url, base_uri)
		# load Schema.org terms (datatypes, properties and types):
		output_json = json.load(open('mappings/schema-org-all.json'))
		detailed_results = {}
		
		columns = sorted(self.table_header, key=lambda cell: cell[0])
		for col in columns:
			test_column = str(col[1])
			detailed_results[test_column] = False
			for toplevel, subdict in output_json.iteritems():
				if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG] scanning all %s ...' %(toplevel))
				if test_column in subdict.keys():
					if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG] %s is a valid Schema.org term.' %(test_column))
					detailed_results[test_column] = True
				else:
					if InstantWebDataPublisher.DEBUG: print('[web.instata:DEBUG] %s is not a valid Schema.org term.' %(test_column))
		
		summary = True
		for v in detailed_results.values():
			if v == False: summary = False
		return (summary, detailed_results)


def usage():
	print("Usage: python web.instata.py -p {path to CSV file} {base URI for publishing}")
	print("Example: python web.instata.py -p test/potd_0.csv http://example.org/instata/potd_0")

if __name__ == "__main__":
	iwdp = InstantWebDataPublisher()
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hcpdv", ["help", "config-publish", "publish", "dump", "validate"])
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				usage()
				sys.exit()
			elif opt in ("-c", "--config-publish"):
				config_file_name = args[0]
				print("[web.instata] processing config file [%s]" %(config_file_name))
				iwdp.load_config(config_file_name)
				r = iwdp.instata(iwdp.doc_url, iwdp.base_uri)
				print("[web.instata] result is now available at [%s]" %(r))
			elif opt in ("-p", "--publish"):
				(doc_url, base_uri) = (args[0], args[1])
				print("[web.instata] processing [%s] with base URI [%s] " %(doc_url, base_uri))
				r = iwdp.instata(doc_url, base_uri)
				print("[web.instata] result is now available at [%s]" %(r))
			elif opt in ("-d", "--dump"):
				(doc_url, base_uri) = (args[0], args[1])
				print("[web.instata] processing [%s] with base URI [%s] " %(doc_url, base_uri))
				iwdp.parse(doc_url, base_uri)
				print(iwdp.dump_data())
			elif opt in ("-v", "--validate"):
				(doc_url, base_uri) = (args[0], args[1])
				print("[web.instata] validating schema ...")
				(summary, detailed_results) = iwdp.validate(doc_url, base_uri)
				if summary: print("[web.instata] all column headings in the input file %s seem to be valid Schema.org terms :)" %doc_url)
				else:
					print("[web.instata] during the validation at least one column heading in input file %s seems not to be a valid Schema.org term :(" %doc_url)
					print(detailed_results)
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)