$(document).on('click','#submit',function() {
    let data = {
        "email":getStorage("email"),
        "totp": getFormData("#totp"),
        "remember_device": getFormData("#remember"),
        "device_details": getDeviceDetails()
    };
    post(data, "users/complete-mfa", function(response) {
        if(response.status == "success") {
            setStorage("access_token",response.access_token);
            window.location.href = "index.html";
        } else {
            alert(error_code_mapping[response.code]);
        }
    });
});

$(document).on('click','#resend',function() {
    let data = {
        "email":getStorage("email")
    };
    post(data, "users/resend", function(response) {
        if(response.status == "success") {
            alert("OTP resent successfully");
        }
    });
});

$( document ).ready(function() {
    $("#email").val(getStorage("email"));
});