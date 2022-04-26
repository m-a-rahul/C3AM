$(document).on('click','#submit',function() {
    let data = {
        "email":getStorage("email"),
        "image": getBase64String(),
        "device_details": getDeviceDetails()
    };
    post(data, "users/password_less/activation", function(response) {
        if(response.status == "success") {
            setStorage("access_token",response.access_token);
            window.location.href = "index.html";
        } else {
            alert(error_code_mapping[response.code]);
        }
    });
});

$( document ).ready(function() {
    $("#email").val(getStorage("email"));
});