var recaptcha_verif = "";

window.onload = function () {
    $('.btn').on('click', function () {
        var $this = $(this);
        $this.button('loading');
        setTimeout(function () {
            $('.btn').button('reset');
        }, 10000);
    });

    $('.modal').on('hidden.bs.modal', function () {
        $('.btn').button('reset');
    });

    not_logged_in = $('.not_logged_in');
    logged_in = $('.logged_in');
    is_admin = $('.is_admin');

    not_logged_in.hide();
    logged_in.hide();
    is_admin.hide();

    var frms = $('form[name="login"]');
    if(frms && frms.length > 0) {
        frms[0].onsubmit = captureData;
    }

    frms = $('form[name="myform"]');
    if(frms && frms.length > 0) {
        frms[0].onsubmit = contactus;
    }

    frms = $('form[name="recoverpass"]');
    if(frms && frms.length > 0) {
        frms[0].onsubmit = recover;
    }

    if(localStorage.getItem('tokenID')){
        $.ajax({
            type: "POST",
            url: "/rest/login/verify?username="+localStorage.getItem('username'),
            contentType: "application/json; charset=utf-8",
            crossDomain: true,
            dataType: "json",
            success: function(response) {
                if(response) {
                    logged_in.show();
                    $('#username-fill').html(localStorage.getItem('username')+'<span class="caret"></span>');
                    if(response.admin)
                        is_admin.show();
                } else {
                    not_logged_in.show();
                }
            },
            error: function () {
                not_logged_in.show();
            },
            data: localStorage.getItem('tokenID')
        })
    } else {
        not_logged_in.show();
    }


    frms = $('form[name="register"]');
    if(frms && frms.length > 0)
        frms[0].onsubmit = registerData;
};

recover = function(event){
    loadJsonify();

    var data = $('form[name="recoverpass"]').jsonify();
    username = data.usernamer;
    $.ajax({
        type: "GET",
        url: "/rest/recover/new?username="+username,
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            console.log(response);
            $('.btn').button('reset');
            if (response) {
                bootbox.alert('Email foi enviado com instruções de recuperação', function () {
                    redirect('front.html');
                });
            } else {
                bootbox.alert('Por favor, tente novamente.');
            }
        },
        error: function () {
            $('.btn').button('reset');
            bootbox.alert('Por favor, tente novamente.');
        }
    });
    event.preventDefault();
};

captureData = function(event) {

    loadJsonify();

    var data = $('form[name="login"]').jsonify();
    username = data.username;
    data.password = SHA512(data.password);
    $.ajax({
        type: "POST",
        url: "/rest/login/login",
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            $('.btn').button('reset');
            if (response) {
                localStorage.setItem('tokenID', response.verif);
                localStorage.setItem('username', data.username);
                bootbox.alert('Bem-vindo!', function () {
                    redirect('front.html');
                });
            } else {
                bootbox.alert('Por favor, tente novamente.');
            }
        },
        error: function () {
            $('.btn').button('reset');
            bootbox.alert('Nome de utilizador ou password errada.');
        },
        data: JSON.stringify(data)
    });
    event.preventDefault();
};

function loadJsonify(){ //HACK TO FORCE JSONIFY
    !function(i){i.fn.jsonify=function(t){var n=i.extend({stringify:!1},t),s={}
        return i.each(this.serializeArray(),function(){s[this.name]?(s[this.name].push||(s[this.name]=[s[this.name]]),s[this.name].push(this.value||"")):s[this.name]=this.value||""}),n.stringify?JSON.stringify(s):s},i.fn.dejsonify=function(t){"string"==typeof t&&(t=JSON.parse(t)),i.each(this.find("*[name]"),function(){var n=i(this).attr("type"),s=t[i(this).attr("name")]
        "radio"===n||"checkbox"===n?i.isArray(s)?i(this).prop("checked",i.inArray(i(this).val(),s)>-1):i(this).prop("checked",i(this).val()===s):i(this).val(s)})}}(jQuery)
}

registerData = function(event) {

    loadJsonify();

    var data = $('form[name="register"]').jsonify();
    username = data.username;
    data.password = SHA512(data.password);
    data.recaptcha = recaptcha_verif;
    data.android = false;
    delete data["g-recaptcha-response"];
    $.ajax({
        type: "POST",
        url: "/rest/register/register",
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            if (response) {
                bootbox.alert("O utilizador " + data.username + " foi registado com sucesso.", function () {
                    redirect('front.html');
                });
            } else {
                bootbox.alert("Por favor, tente novamente.");
            }
        },
        error: function () {
            bootbox.alert('Não preencheu o registo corretamente.');
        },
        data: JSON.stringify(data)
    });
    event.preventDefault();
};

contactus = function(event) {
    loadJsonify();
    var data = $('form[name="myform"]').jsonify();

    data.email = data.emailc;
    data.username = data.namec;
    data.content = data.textc;
    delete data.emailc;
    delete data.namec;
    delete data.textc;
    $.ajax({
        type: "POST",
        url: "/rest/message/new",
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            bootbox.alert("Agradecemos a sua mensagem. O mais breve possível, receberá a resposta no email indicado.", function () {
                    redirect('front.html');
            });
        },
        error: function () {
            bootbox.alert("Por favor, tente novamente.");
        },
        data: JSON.stringify(data)
    });

    event.preventDefault();
}

var captchaContainer = null;
var loadCaptcha = function() {
    captchaContainer = grecaptcha.render('captcha_container', {
        //'sitekey' : '6LcYrSQUAAAAAJxDVL05ygkRgVp7vu9koYtn-Uq7',
        'sitekey': '6LeS7yUUAAAAAIEzMHvsOoi97LWiyx813qQOQheO',
        'callback' : function(response) {
            recaptcha_verif = response;
        }
    });
};