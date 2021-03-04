window.onload = function () {
    /*if(localStorage.getItem('username') == null || localStorage.getItem('tokenID') == null)
     redirect('front.html');

     $('#username-fill').html(localStorage.getItem('username')+'<span class="caret"></span>');*/

    is_admin = $('.is_admin');
    is_admin.hide();

    if (localStorage.getItem('tokenID')) {
        $.ajax({
            type: "POST",
            url: "/rest/login/verify?username=" + localStorage.getItem('username'),
            contentType: "application/json; charset=utf-8",
            crossDomain: true,
            dataType: "json",
            success: function (response) {
                if (response) {
                    $('#username-fill').html(localStorage.getItem('username') + '<span class="caret"></span>');
                    if (response.admin)
                        is_admin.show();
                } else {
                    bootbox.alert('Por favor, tente novamente.');
                }
            },
            error: function () {
                bootbox.alert('Por favor, tente novamente.');
            },
            data: localStorage.getItem('tokenID')
        })
    } else {
        redirect('front.html');
    }

    var frms = $('form[name="task"]');
    if (frms && frms.length > 0)
        frms[0].onsubmit = registerData;
};

registerData = function (event) {
    var data = $('form[name="task"]').jsonify();

    if (typeof marker == 'undefined') {
        bootbox.alert("Clique no mapa para definir a localização.");
        event.preventDefault();
        return;
    }
    if (document.getElementById('file').files[0].size > 10000000){
        bootbox.alert("A sua imagem não pode exceder os 10Mbs, por favor escolha outra.");
        event.preventDefault();
        return;
    }

    if (document.getElementById('file').files.length != 0) {
        var form = new FormData();
        form.append("files", document.getElementById('file').files[0]);
        form.append("username", localStorage.getItem('username'));
        form.append("token", localStorage.getItem('tokenID'));
        $.ajax({
            type: "POST",
            url: "/rest/file/upload",
            contentType: false,
            processData: false,
            cache: false,
            crossDomain: true,
            success: function (response) {
                if (response) {
                    data.link = response.responseText;
                    bootbox.alert("Imagem adicionada com sucesso.", function () {
                        sendData(data);
                    });
                } else {
                    bootbox.alert("Por favor, tente novamente.");
                }
            },
            error: function (response) {
                if (response.status != 200)
                    bootbox.alert("Por favor, tente novamente.");
                else {
                    data.link = response.responseText;
                    bootbox.alert('Imagem adicionada com sucesso.', function () {
                        sendData(data);
                    });
                }
            },
            data: form
        });
        event.preventDefault();
    } else {
        sendData(data);
    }
};

function getQueryParams(qs) {
    qs = qs.split('+').join(' ');

    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
}

function sendData(data) {

    if (typeof data.link == 'undefined' || data.link === "") {
        bootbox.alert("Tem que adicionar uma imagem ou um link.");
        event.preventDefault();
        return;
    }

    //TODO add verification that data.link is a url

    data.user = localStorage.getItem('username');
    data.token = localStorage.getItem('tokenID');

    data.lat = marker.position.lat();
    data.lon = marker.position.lng();

    //I THINK ITS THIS:
    data.fullType = $(document.getElementById('selectType')).find("option:selected").val();
    //params = getQueryParams(document.location.search);
    //data.type = params.type;
    $.ajax({
        type: "POST",
        url: "/rest/task/new",
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            if (response) {
                bootbox.alert("Agradecemos a sua contribuição. A ocorrência será analisada.", function () {
                    redirect('map.html');
                });
            } else {
                bootbox.alert("Por favor, tente novamente.");
            }
        },
        error: function (response) {
            if (response.status != 200)
                bootbox.alert("Por favor, tente novamente.");
            else {
                bootbox.alert('Agradecemos a sua contribuição. A ocorrência será analisada.', function () {
                    redirect('map.html');
                });
            }
        },
        data: JSON.stringify(data)
    });
    event.preventDefault();
}

function afterLoad() {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (pos) {
            map = new google.maps.Map(document.getElementById('map'),
                {
                    center: {lat: pos.coords.latitude, lng: pos.coords.longitude},
                    zoom: 16
                }
            );

            map.addListener('click', function (e) {
                if (typeof marker != 'undefined')
                    marker.setMap(null);

                marker = new google.maps.Marker({
                    position: e.latLng,
                    map: map
                });
            });

            setTimeout(strictBounds, 500);
            return;
        });
    }

    map = new google.maps.Map(document.getElementById('map'),
        {
            center: {lat: 38.659784, lng: -9.202765}, //centro de almada
            zoom: 16
        }
    );

    map.addListener('click', function (e) {
        if (typeof marker != 'undefined')
            marker.setMap(null);

        marker = new google.maps.Marker({
            position: e.latLng,
            map: map
        });
    });


    setTimeout(strictBounds, 500);
}

function strictBounds() {
    map.setOptions({minZoom: 12});

    // bounds of the desired area
    var allowedBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(38.516803, -9.273483),
        new google.maps.LatLng(38.690666, -9.127213)
    );

    var lastValidCenter = map.getCenter();

    google.maps.event.addListener(map, 'center_changed', function () {
        if (allowedBounds.contains(map.getCenter())) {
            // still within valid bounds, so save the last valid position
            //console.log("Before: "+ lastValidCenter);
            lastValidCenter = map.getCenter();
            //console.log("After: "+ lastValidCenter);
            return;
        }

        // not valid anymore => return to last valid position
        map.panTo(lastValidCenter);
    });

    var polygonMask = new google.maps.Polygon({
        map: map,
        strokeColor: '#6eabbf',
        strokeOpacity: 0.8,
        strokeWeight: 3,
        fillColor: '#CACACA',
        fillOpacity: 0.7,
        paths: [[new google.maps.LatLng(-78.163101, -173.025704),
            new google.maps.LatLng(84.884253, -174.646187),
            new google.maps.LatLng(84.118584, 3.695564),
            new google.maps.LatLng(84.647516, 174.824104),
            new google.maps.LatLng(19.506170, 174.390144),
            new google.maps.LatLng(-83.196105, 169.034309),
            new google.maps.LatLng(-82.244934, -0.852776),
            new google.maps.LatLng(-78.163101, -173.025704)],
            [new google.maps.LatLng(38.542795, -9.192810),
                new google.maps.LatLng(38.571253, -9.156761),
                new google.maps.LatLng(38.626795, -9.164314),
                new google.maps.LatLng(38.655354, -9.117279),
                new google.maps.LatLng(38.693281, -9.140282),
                new google.maps.LatLng(38.674789, -9.278297),
                new google.maps.LatLng(38.542795, -9.192810)]]
    });

    /*
     if (navigator.geolocation) {
     navigator.geolocation.getCurrentPosition(function (pos) {
     marker = new google.maps.Marker({
     position: {lat: pos.coords.latitude, lng: pos.coords.longitude},
     map: map
     });
     });
     }*/
}
/*
 function deleteTask(id) { // TODO verificar se o utilizador é dono da ocorrência
 $.ajax({
 type: "DELETE",
 url: "/rest/task/delete?user="+localStorage.getItem('username')+"&token="+localStorage.getItem('tokenID')+"&id="+id,
 contentType: "application/json; charset=utf-8",
 crossDomain: true,
 dataType: "json",
 success: function (response) {
 if (response) {
 bootbox.alert('Ocorrência removida com sucesso.', function () {
 redirect('/map.html');
 });
 } else {
 bootbox.alert('Por favor, tente novamente.');
 }
 },
 error: function (response) {
 if(response.status != 200)
 bootbox.alert('Por favor, tente novamente.');
 else {
 bootbox.alert('Ocorrência removida com sucesso.', function () {
 redirect('/map.html');
 });
 }
 }
 });
 }*/