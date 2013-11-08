<!doctype html>
<html>
<head>
  <%block name="css" />
  <title><%block name="title" /></title>
</head>
<body>
  ${self.body()}
  <%block name="scripts">
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.js"></script>
    <script src="json2.js"></script>
  </%block>
</body>
</html>
