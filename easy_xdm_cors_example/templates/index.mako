<%inherit file="base.mako" />

<%block name="title">Index</%block>

Hello World

<button class="cors-now">OMG DO CORS NOW</button>
<div class="cors-status"></div>

<%block name="scripts">
  ${parent.scripts()}
  <script src="/easyXDM.debug.js"></script>
  <script>
    $(function () {
        $('.cors-now').on('click', function () {
            console.log('click');
            var xhr = new easyXDM.Rpc(
                {remote: 'https://localhost:9001/cors/index.html'},
                {remote: {request: {}}}
            );

            xhr.request(
                {
                    url: '/post_endpoint',
                    method: 'POST',
                    data: {
                        firstname: 'Anthony',
                        lastname: 'Sottile',
                        phone: '248-888-8888',
                        email: 'herp.derp@example.com',
                   }
               },
               function (response) {
                   $('.cors-status').text(JSON.stringify(response.data));
               }
           );
        });
    });
  </script>
</%block>
