<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>{{ds_name}}</title>
	<link rel="stylesheet" href="web.instata-style.css" type="text/css" />
	<link rel="stylesheet" href="jquery-ui-1.8.4.custom.css" type="text/css" />
	<link rel="stylesheet" href="d_table.css" type="text/css" />
	<link rel="stylesheet" href="d_table_jui.css" type="text/css" />
</head>
<body>
	<div id="header">
		<h1>{{ds_name}}</h1>
	</div>
	
	<div id="main">
		<table id="instatable">
			<thead>
				<tr itemscope itemtype="http://purl.org/NET/schema-org-csv#HeaderRow">
					<!-- ?cell ?colTitle -->
					%for h in theader:
						<th itemscope itemtype="http://schema.org/Thing" itemid="{{str(h[0])}}">{{str(h[1])}}</th>
					%end
				</tr>
			</thead>
			<tbody>
				<!-- ?row ?cell ?cellType ?val -->
				%for rec in trows:
					%if 'col:1' in rec[1]:
						<tr itemscope itemtype="{{rec[2]}}" itemid="{{rec[0]}}">
						<td><a href="{{rec[0]}}" itemprop="http://schema.org/url">{{rec[3]}}</a></td>
					%else:
						<td itemprop="{{rec[2]}}">{{rec[3]}}</td>
					%end
					%if int(rec[1].split('#')[1].split(',')[1].split(':')[1]) == len(theader):
						</tr>
					%end
				%end
			</tbody>
		</table>
		
		<div id="related">
			Related terms from other vocabularies:
			<ul>
			%for schemaTerm, match in aliases.items():
				<li>DBpedia: <a href="{{match[1]}}">{{schemaTerm.split('/')[-1]}}</li>
			%end
			</ul>
		</div>
	</div>

	<div id="footer">
		Last update on: {{wi_last_update}} | Created with <a href="https://github.com/mhausenblas/web.instata">web.instata</a> 
	</div>
	</body>
	<script type="text/javascript" src="jquery.js"></script>
	<script type="text/javascript" src="jquery.dataTables.min.js"></script>
	<script type='text/javascript'>
		$(document).ready(function() {
			$('#instatable').dataTable({
				"bJQueryUI": true
			});
		});
	</script>
</html>