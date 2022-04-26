const initiate_mfa = () => {
    let data = {
        "email":getStorage("email")
    };
    post(data, "users/mfa-login", function(response) {
        if(response.status == "success") {
            window.location.href = "mfa_login.html";
        } else {
            alert(error_code_mapping[response.code]);
        }
    });
}

$(document).on('click','#submit',function() {
    let data = {
        "email":getStorage("email"),
        "image": getBase64String(),
        "device_details": getDeviceDetails()
    };
    post(data, "users/password_less/login", function(response) {
        if(response.status == "success") {
            setStorage("access_token",response.access_token);
            window.location.href = "index.html";
        } else if(response.code == "#112") {
            initiate_mfa();
        } else {
            alert(error_code_mapping[response.code]);
        }
    });
});

$(document).on('click','#change',function() {
    $("#email").attr("readonly", false); 
    $('#submit').prop('disabled', true);
    $(this).prop('id', 'save');
    $(this).html("Save");
});

$(document).on('click','#save',function() {
    setStorage("email",$("#email").val());
    $("#email").attr("readonly", true); 
    $('#submit').prop('disabled', false);
    $(this).prop('id', 'change');
    $(this).html("Change");
});

$( document ).ready(function() {
    if(getStorage("email")) {
        $("#email").val(getStorage("email"));
    } else {
        $("#email").attr("readonly", false); 
        $('#submit').prop('disabled', true);
        $("#change").prop('id', 'save');
        $("#save").html("Save");
    }
});
