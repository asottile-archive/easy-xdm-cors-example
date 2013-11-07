<%inherit file="base.mako" />

<%block name="title">Index</%block>

<form>
  <label>
    <div>First:</div>
    <input class="first-name">
  </label>
  <label>
    <div>Last:</div>
    <input class="last-name">
  </label>
  <label>
    <div>Email:</div>
    <input class="email">
  </label>
  <label>
    <div>Phone:</div>
    <input class="phone">
  </label>
</form>
<button class="cors-now">OMG DO CORS NOW</button>
<div class="cors-status"></div>

<%block name="scripts">
  ${parent.scripts()}
  <script src="/easyXDM.debug.js"></script>
  <script>
    $(function () {
        $('.cors-now').on('click', function () {
            var firstName = $('.first-name').val(),
                lastName = $('.last-name').val(),
                email = $('.email').val(),
                phone = $('.phone').val();

            if (!firstName || !lastName || !email || !phone) {
                alert('Missing stuff');
                return;
            }

            var xhr = new easyXDM.Rpc(
                {remote: 'https://${host}:9001/cors/index.html'},
                {remote: {request: {}}}
            );

            xhr.request(
                {
                    url: '/post_endpoint',
                    method: 'POST',
                    data: {
                        first_name: firstName,
                        last_name: lastName,
                        email: email,
                        phone: phone,
                   }
               },
               function (response) {
                   var responseElement = $('<div>').text(response.data);
                   $('.cors-status').empty().append(responseElement);
               }
           );
        });
    });
  </script>
</%block>
