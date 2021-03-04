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

    if(localStorage.getItem('tokenID')){
        $.ajax({
            type: "POST",
            url: "/rest/login/verify?username="+localStorage.getItem('username'),
            contentType: "application/json; charset=utf-8",
            crossDomain: true,
            dataType: "json",
            success: function(response) {
                console.log(response);
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

    frms = $('form[name="guardar"]');
    if(frms && frms.length > 0)
        frms[0].onsubmit = changeThings;
};

/*See if fine*/
changeThings = function (event) {
    loadJsonify();
    var data = $('form[name="guardar"]').jsonify();
    data.password = SHA512(data.password);
    data.token = localStorage.getItem('tokenID');
    $.ajax({
        type: "POST",
        url: "/rest/user/update",
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            if (response) {
                bootbox.alert('Perfil actualizado!', function () {
                    redirect('front.html');
                });
            } else {
                bootbox.alert('Não foi possível alterar o seu perfil.');
            }
        },
        error: function () {
            bootbox.alert('Utilizador sem sessão iniciada.', function () {
                redirect('front.html');
            });
        },
        data: JSON.stringify(data)
    });
    event.preventDefault();
};