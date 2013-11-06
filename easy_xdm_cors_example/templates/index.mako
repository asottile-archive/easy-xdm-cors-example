<%inherit file="base.mako" />

<%block name="title">Index</%block>

Hello World

<%block name="scripts">
  ${parent.scripts()}
  <script src="/easyXDM.debug.js"></script>
</%block>
