$(document).on('click','#submit',function() {
    let data = {
        "email":getStorage("email"),
        "totp": getFormData("#totp")
    };
    post(data, "users/activate", function(response) {
        if(response.status == "success") {
            window.location.href = "passwordless_activation.html";
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
        } else {
            alert(error_code_mapping[response.code]);
        }
    });
});

$( document ).ready(function() {
    $("#email").val(getStorage("email"));
});
