$( document ).ready(function() {
    get("users/current-user", function(response) {
        if(response.status == "success") {
            $('#username').html(response.data.username);
            $('#email').html(response.data.email);
        } else {
            window.location.href = "passwordless_login.html";
        }
    });
});

$(document).on('click','#logout',function() {
    removeStorage("access_token");
    window.location.href = "c3am.html";
});