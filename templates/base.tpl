<!DOCTYPE HTML>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
	<title>{{ds_name}}</title>
	<link rel="stylesheet" href="web.instata-style.css" type="text/css" />
</head>
<body>
	<div id="header">
		<h1>{{ds_name}}</h1>
	</div>
	
	<div id="main">
		%for h in theader:
			<div class="header">{{h}}</div>
		%end
		%for r in trows:
			<div class="row">{{r}}</div>
		%end
	</div>

	<div id="footer">
		Last update on: {{wi_last_update}} | Created with <a href="https://github.com/mhausenblas/web.instata">web.instata</a> 
	</div>
	</body>
</html>