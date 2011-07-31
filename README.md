# web.instata

Turn your plain old tabular data (POTD) into Web data with web.instata: it takes CSV as input and generates a HTML document with the data items marked up with  [Schema.org](http://schema.org) terms.

	                       +--------------------+
	+-------+              |                    |            +--------------+
	|  CSV  |              |                    |            |              |
	|-------|              |                    |            |   HTML5      |
	|       | +----------->|     web.instata    |+---------> |              |
	|       |              |                    |            |   Schema.org |
	|       |              |                    |            |              |
	+-------+              |                    |            +--------------+
	                       +--------------------+

**Note**: web.instata only works for [CSV files](http://tools.ietf.org/html/rfc4180) that use [Schema.org types or properties](http://schema.org/docs/full.html) as column names.


## Usage

### Publishing

In order to publish a HTML+microdata document from a CSV file:

	python web.instata.py -p {path to CSV file} {base URI for publishing}

Example:

	python web.instata.py -p test/potd_0.csv http://example.org/instata/potd_0
	
... and you should see the following on the command line:

	[web.instata] processing [test/potd_0.csv] with base URI [http://example.org/instata/potd_0] 
	[web.instata] loading DBpedia2Schema.org mapping ...
	[web.instata] got DBpedia2Schema.org mapping!
	[web.instata] trying to find a match for http://schema.org/Recipe
	[web.instata] trying to find a match for http://schema.org/publishDate
	[web.instata] trying to find a match for http://schema.org/name
	[web.instata] trying to find a match for http://schema.org/author
	[web.instata] match(es) found: {'http://schema.org/author': ('http://www.w3.org/2002/07/owl#equivalentProperty', 'http://dbpedia.org/ontology/author')}
	[web.instata] result is now available at [output/potd_0.html]

	
As a result of the above command, an HTML+microdata document [potd_0.html](https://raw.github.com/mhausenblas/web.instata/master/doc/example_output_html.txt) is created that should look like the following:

![example output screenshot](https://github.com/mhausenblas/web.instata/raw/master/doc/example_output_screenshot.png "Example web.instata output for the input file test/potd_0.csv")

The generated HTML document, [potd_0.html](https://raw.github.com/mhausenblas/web.instata/master/doc/example_output_html.txt), contains Schema.org terms marked up in [microdata](http://www.w3.org/TR/microdata/) as follows:

	<table id="instatable">
		<thead>
			<tr itemscope itemtype="http://purl.org/NET/schema-org-csv#HeaderRow">
				<th itemscope itemtype="http://schema.org/Thing" itemid="http://example.org/instata/potd_0#row:1,col:1">Recipe</th>
				<th itemscope itemtype="http://schema.org/Thing" itemid="http://example.org/instata/potd_0#row:1,col:2">name</th>
				...
			</tr>
		</thead>
		<tbody>
			<tr itemscope itemtype="http://schema.org/Recipe" itemid="http://example.org/instata/potd_0#row:2">
				<td><a href="http://example.org/instata/potd_0#row:2" itemprop="http://schema.org/url">bb</a></td>
				<td itemprop="http://schema.org/name">Mom's World Famous Banana Bread</td>
				<td itemprop="http://schema.org/author">John Smith</td>
				<td itemprop="http://schema.org/publishDate">May 8, 2009</td>
			</tr>
			...
		</tbody>
	</table>	

### Data dump

In order to get a RDF/Turtle data dump from a CSV file:

	python web.instata.py -d {path to CSV file} {base URI for publishing}

Example:

	python web.instata.py -d test/potd_0.csv http://example.org/instata/potd_0

... and you should see something like the following on the command line:

	@prefix dc: <http://purl.org/dc/terms/> .
	@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
	@prefix scsv: <http://purl.org/NET/schema-org-csv#> .
	
	<http://example.org/instata/potd_0#table> a <http://purl.org/NET/schema-org-csv#Table>;
	    scsv:row <http://example.org/instata/potd_0#row:1>,
	        <http://example.org/instata/potd_0#row:2>,
	        <http://example.org/instata/potd_0#row:3>;
	    dc:source <http://example.org/instata/potd_0>;
	    dc:title "potd_0" .
	
	<http://example.org/instata/potd_0#row:1> a <http://purl.org/NET/schema-org-csv#HeaderRow>;
	    scsv:cell <http://example.org/instata/potd_0#row:1,col:1>,
	        <http://example.org/instata/potd_0#row:1,col:2>,
	        <http://example.org/instata/potd_0#row:1,col:3>,
	        <http://example.org/instata/potd_0#row:1,col:4>;
	    dc:title "header" .
		
	<http://example.org/instata/potd_0#row:1,col:1> dc:title "Recipe" .
	
	<http://example.org/instata/potd_0#row:2> a <http://purl.org/NET/schema-org-csv#Row>;
	    scsv:cell <http://example.org/instata/potd_0#row:2,col:1>,
	        <http://example.org/instata/potd_0#row:2,col:2>,
	        <http://example.org/instata/potd_0#row:2,col:3>,
	        <http://example.org/instata/potd_0#row:2,col:4>;
	    dc:title "row 2" .
	
	<http://example.org/instata/potd_0#row:2,col:1> a <http://schema.org/Recipe>;
	    rdf:value "bb" .


## Kudos

Thanks to [asciiflow.com](http://www.asciiflow.com) for providing a useful tool.

## To do

* DONE: use [Bottle](http://bottlepy.org/docs/dev/) as templating system for output
* DONE: use [DBpedia2Schema.org](http://mappings.dbpedia.org/server/ontology/export) mapping to enrich output (related link, etc.)
* Use the [JS dump](http://schema.rdfs.org/all.json) from Schema.RDF.org to check if term exists
* Provide new option `-c` to check input data
* Provide new option `-d` to create data dump in RDF

## License

This software is Public Domain.






















