$(document).on('click','#submit',function() {
    let data = {
        "user_details": {
            "username": getFormData("#username"),
            "email": getFormData("#email")        
        },
        "remember_device": getFormData("#remember"),
        "device_details": getDeviceDetails()
    };
    setStorage("email", data["user_details"]["email"]);
    post(data, "users/register", function(response) {
        if(response.status == "success") {
            window.location.href = "verification.html";
        } else {
            alert(error_code_mapping[response.code]);
            removeStorage("email");
        }
    });
});
