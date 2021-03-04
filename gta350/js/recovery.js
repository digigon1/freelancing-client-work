window.onload = function () {
    var frms = $('form[name="recovery"]');
    if(frms && frms.length > 0) {
        frms[0].onsubmit = sendRecovery;
    }
};

sendRecovery = function (event) {
    var data = $('form[name="recovery"]').jsonify();
    if(data["password"] != data["password2"]){
        bootbox.alert("As passwords não correspondem.");
        event.preventDefault();
        return;
    }
    delete data["password2"];
    data.password = SHA512(data.password);
    $.ajax({
        type: "POST",
        url: "/rest/recover/reset",
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            if (response) {
                bootbox.alert("A password foi alterada com sucesso.", function () {
                    redirect('front.html');
                });
            } else {
                bootbox.alert("Por favor, tente novamente.");
            }
        },
        error: function () {
            bootbox.alert("Por favor, tente novamente.");
        },
        data: JSON.stringify(data)
    });

    event.preventDefault();
};