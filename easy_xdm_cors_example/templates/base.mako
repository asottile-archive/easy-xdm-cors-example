<!doctype html>
<html>
<head>
  <%block name="css">
    <link rel="stylesheet" href="/css/base.css" />
  </%block>
  <title><%block name="title" /></title>
</head>
<body>
  ${self.body()}
  <%block name="scripts">
    <script src="/js/jquery-2.0.3.js"></script>
  </%block>
</body>
</html>
