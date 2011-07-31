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
				%record = 0
				<!-- ?row ?cell ?cellType ?val -->
				%for r in trows:
					%if record == 0:
					<tr itemscope itemtype="{{str(r[2])}}" itemid="{{str(r[0])}}">
						<td><a href="{{str(r[1])}}" itemprop="http://schema.org/url">{{str(r[3])}}</a></td>
					%else:
						<td itemprop="{{str(r[2])}}">{{str(r[3])}}</td>
					%end
					%if record == 3:
					</tr>
					%record = 0
					%else:
					%record = record + 1
					%end
				%end
			</tbody>
		</table>
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