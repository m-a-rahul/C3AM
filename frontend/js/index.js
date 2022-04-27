$( document ).ready(function() {
    let data = {
        "device_details": getDeviceDetails()
    };
    jwt_post(data, "users/current-user", function(response) {
        if(response.status == "success") {
            $('#username').html(response.data.username);
            $('#email').html(response.data.email);
            $('#loading').addClass("d-none");
            $('#authenticated').removeClass("d-none");
        } else {
            if(getStorage("email"))
                window.location.href = "passwordless_login.html";
            else
                window.location.href = "registration.html";
        }
    });
});

$(document).on('click','#logout',function() {
    removeStorage("access_token");
    window.location.href = "c3am.html";
});