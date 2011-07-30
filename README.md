# web.instata

Turn your plain old tabular data (POTD) into Web data with web.instata: it takes CSV as input and generates a HTML document with the data items marked up with  [Schema.org](http://schema.org) terms.


	                       +--------------------+
	+-------+              |                    |            +--------------+
	|  CSV  |              |                    |            |              |
	|-------|              |                    |            |   HTML5      |
	|       | +----------->|     web.instata    |+---------> |              |
	|       |              |                    |            |   Schema.org |
	|       |              |                    |            |              |
	|       |              |                    |            +--------------+
	+-------+              +--------------------+

Usage:

	python web.instata.py -p {path to CSV file} {base URI for publishing}

Example:

	python web.instata.py -p test/potd_0.csv http://example.org/instata/potd_0


## Kudos

Thanks to http://www.asciiflow.com for providing a useful tool.


## License

This software is Public Domain.






















