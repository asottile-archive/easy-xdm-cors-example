<!doctype html>
<html>
<head>
  <%block name="css" />
  <title><%block name="title" /></title>
</head>
<body>
  ${self.body()}
  <%block name="scripts">
    <script src="jquery-1.10.2.js"></script>
  </%block>
</body>
</html>
