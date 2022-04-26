const getFormData = (ele) => {
    if(ele=="#remember" && $("#remember").prop('checked') == true){
        return true
    }
    return $(ele).val()
}

const getStorage = (ele) => {
    return localStorage.getItem(ele)
}

const setStorage = (ele, val) => {
    return localStorage.setItem(ele, val)
}

const removeStorage = (ele) => {
    return localStorage.removeItem(ele)
}

const error_code_mapping = {
    "#101" : "Authentication Successful",
    "#102" : "Account verification Successful",
    "#103" : "Account activation Successful",
    "#104" : "TOTP sent Successfully",
    "#105" : "Authentication Unsuccessful",
    "#106" : "Email id already exists",
    "#107" : "Account not verified",
    "#108" : "Account inactive",
    "#109" : "Connection Error",
    "#110" : "Incorrect TOTP",
    "#111" : "Email id does not exist",
    "#112" : "Initiate MFA "
};

const post = (json_data, url_path, callback, asyncStatus = true) => {
    $.ajax({
            type: "POST",
            async: asyncStatus,
            headers: {
                "Content-Type": "application/json",
              },
            credentials: 'same-origin',
            data: JSON.stringify(json_data),
            timeout: 60000,
            url: "http://localhost:50001/"+url_path
        })
        .done(function(result) {
            callback(result);
        })
        .fail(function(result) {
            callback("ajax_timeout");
            return false;
        });
}

const get = (url_path, callback, asyncStatus = true) => {
    $.ajax({
            type: "GET",
            async: asyncStatus,
            timeout: 60000,
            url: "http://localhost:50001/"+url_path,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Bearer "+getStorage("access_token"));
            },
        })
        .done(function(result) {
            callback(result);
        })
        .fail(function(result) {
            callback("ajax_timeout");
            return false;
        });
}


let base64String = "";
  
const generateBase64String = () => {
    var file = document.querySelector(
        'input[type=file]')['files'][0];
  
    var reader = new FileReader();
    console.log("next");
      
    reader.onload = function () {
        base64String = reader.result.replace("data:", "")
            .replace(/^.+,/, "");
  
        imageBase64Stringsep = base64String;
    }
    reader.readAsDataURL(file);
}

const getBase64String = () => {
    return base64String;
}
  
const getDeviceDetails = () => {
    'use strict';

    var module = {
        options: [],
        header: [navigator.platform, navigator.userAgent, navigator.appVersion, navigator.vendor, window.opera],
        dataos: [
            { name: 'Windows Phone', value: 'Windows Phone', version: 'OS' },
            { name: 'Windows', value: 'Win', version: 'NT' },
            { name: 'iPhone', value: 'iPhone', version: 'OS' },
            { name: 'iPad', value: 'iPad', version: 'OS' },
            { name: 'Kindle', value: 'Silk', version: 'Silk' },
            { name: 'Android', value: 'Android', version: 'Android' },
            { name: 'PlayBook', value: 'PlayBook', version: 'OS' },
            { name: 'BlackBerry', value: 'BlackBerry', version: '/' },
            { name: 'Macintosh', value: 'Mac', version: 'OS X' },
            { name: 'Linux', value: 'Linux', version: 'rv' },
            { name: 'Palm', value: 'Palm', version: 'PalmOS' }
        ],
        databrowser: [
            { name: 'Chrome', value: 'Chrome', version: 'Chrome' },
            { name: 'Firefox', value: 'Firefox', version: 'Firefox' },
            { name: 'Safari', value: 'Safari', version: 'Version' },
            { name: 'Internet Explorer', value: 'MSIE', version: 'MSIE' },
            { name: 'Opera', value: 'Opera', version: 'Opera' },
            { name: 'BlackBerry', value: 'CLDC', version: 'CLDC' },
            { name: 'Mozilla', value: 'Mozilla', version: 'Mozilla' }
        ],
        init: function () {
            var agent = this.header.join(' '),
                os = this.matchItem(agent, this.dataos),
                browser = this.matchItem(agent, this.databrowser);
            
            return { os: os, browser: browser };
        },
        matchItem: function (string, data) {
            var i = 0,
                j = 0,
                html = '',
                regex,
                regexv,
                match,
                matches,
                version;
            
            for (i = 0; i < data.length; i += 1) {
                regex = new RegExp(data[i].value, 'i');
                match = regex.test(string);
                if (match) {
                    regexv = new RegExp(data[i].version + '[- /:;]([\\d._]+)', 'i');
                    matches = string.match(regexv);
                    version = '';
                    if (matches) { if (matches[1]) { matches = matches[1]; } }
                    if (matches) {
                        matches = matches.split(/[._]+/);
                        for (j = 0; j < matches.length; j += 1) {
                            if (j === 0) {
                                version += matches[j] + '.';
                            } else {
                                version += matches[j];
                            }
                        }
                    } else {
                        version = '0';
                    }
                    return {
                        name: data[i].name,
                        version: parseFloat(version)
                    };
                }
            }
            return { name: 'unknown', version: 0 };
        }
    };
    
    var e = module.init();
    
    var device_details = {
        "os.name":e.os.name,
        "os.version":e.os.version,
        "browser.name":e.browser.name,
        "browser.version":e.browser.version,
        "navigator.userAgent":navigator.userAgent,
        "navigator.appVersion":navigator.appVersion,
        "navigator.platform":navigator.platform,
        "navigator.vendor":navigator.vendor

    };
    
    return device_details;
};
