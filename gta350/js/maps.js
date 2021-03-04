var map, center, zoom;
var t = 0;
var image ="";
function initMap(tp) {
    if(typeof tp == 'undefined')
        tp = 0;

    t = tp;
    if(typeof map != 'undefined') {
        center = map.getCenter();
        zoom = map.getZoom();
        map = new google.maps.Map(document.getElementById('map'), {
            center: center,
            zoom: zoom
        });
    } else {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (pos) {
                map = new google.maps.Map(document.getElementById('map'), {
                        center: {lat: pos.coords.latitude, lng: pos.coords.longitude},
                        zoom: 12
                    }
                );
            }, function () {
                map = new google.maps.Map(document.getElementById('map'),
                    {
                        center: {lat: 38.659784, lng: -9.202765},
                        zoom: 12
                    }
                );
            })
        } else {
            map = new google.maps.Map(document.getElementById('map'),
                {
                    center: {lat: 38.659784, lng: -9.202765},
                    zoom: 12
                }
            );
        }
    }

    setTimeout(initMarker, 500);

    setTimeout(strictBounds, 500);
}

function strictBounds(){

    map.setOptions({ minZoom: 12 });

    // bounds of the desired area
    var allowedBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(38.516803, -9.273483),
        new google.maps.LatLng(38.690666, -9.127213)
    );

    var lastValidCenter = map.getCenter();

    google.maps.event.addListener(map, 'center_changed', function() {
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
        map:map,
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
                new google.maps.LatLng(38.542795, -9.192810)]]});
}

function chooseImage(tp) {
    switch (tp) {
        case "1":
            image = "../img/water.png";
            break;
        case "2":
            image = "../img/tree.png";
            break;
        case "3":
            image = "../img/electricity.png";
            break;
        case "4":
            image = "../img/gas.png";
            break;
        case "5":
            image = "../img/road.png";
            break;
    }
}

function initMarker(){
    markers = [];
    $.ajax({
        type: "GET",
        url: "/rest/task/all?user="+localStorage.getItem('username')+"&token="+localStorage.getItem('tokenID')+"&type="+t,
        contentType: "application/json; charset=utf-8",
        crossDomain: true,
        dataType: "json",
        success: function (response) {
            if (response) {
                for(var i = 0; i < response.length; i++){
                    resp = response[i].propertyMap;
                    name = response[i].key.name;
                    chooseImage(resp.occurrence_type);
                    markers.push(new google.maps.Marker({
                        user: resp.occurrence_user,
                        map: map,
                        icon: image,
                        type: resp.written_type,
                        fullType: resp.written_subtype,
                        img: resp.occurrence_images.value[0],
                        position: {
                            lat: resp.occurrence_place.latitude,
                            lng: resp.occurrence_place.longitude
                        },
                        o_name: name,
                        title: resp.occurrence_name,
                        url: "/rest/task/get?user="+localStorage.getItem('username')+"&token="+localStorage.getItem('tokenID')+"&id="+name
                    }))
                }
                for(i = 0; i < markers.length; i++) {
                    google.maps.event.addListener(markers[i], 'click', function () {
                        $('#deleteOccur').hide();
                        modal = $('#occurrenceModal');

                        mark = this;

                        document.getElementById('myModalLabel').value = mark.title;
                        document.getElementById('myModalType').value = mark.type;
                        document.getElementById('myModalFullType').value = mark.fullType;
                        document.getElementById('myModalImage').src = mark.img;

                        document.getElementById('myModalInfo').onclick = function(){
                            redirect('ocorrencia.jsp?id='+mark.o_name);
                        };

                        modal.on('shown.bs.modal', function() {
                            if (mark.user == localStorage.getItem('username')) {
                                butt = $('#deleteOccur');
                                butt.click(function () {
                                    $.ajax({
                                        type: "DELETE",
                                        url: "/rest/task/delete?user="+localStorage.getItem('username')+"&token="+localStorage.getItem('tokenID')+"&id="+mark.o_name,
                                        contentType: "application/json; charset=utf-8",
                                        crossDomain: true,
                                        dataType: "json",
                                        success: function (response) {
                                            if (response) {
                                                bootbox.alert("Ocorrência removida com sucesso.", function () {
                                                    redirect('map.html');
                                                });
                                            } else {
                                                bootbox.alert("Por favor, tente novamente.", function () {
                                                    redirect('map.html');
                                                });
                                            }
                                        },
                                        error: function (response) {
                                            if(response.status != 200)
                                                bootbox.alert('Por favor, tente novamente.', function () {
                                                    redirect('map.html');
                                                });
                                            else {
                                                bootbox.alert('Ocorrência removida com sucesso.', function () {
                                                    redirect('map.html');
                                                });
                                            }
                                        }
                                    });
                                });
                                butt.show();
                            }

                            q = $('#myModalType');
                            q.height(0);
                            q.height(q[0].scrollHeight);

                            q = $('#myModalFullType');
                            q.height(0);
                            q.height(q[0].scrollHeight);
                        });

                        modal.modal('show');
                    });
                }
            } else {
                bootbox.alert("Por favor, tente novamente.");
            }
        },
        error: function () {
            bootbox.alert("Por favor, tente novamente.");
        }
    });
}
/*
window.onload = function () {
    if(localStorage.getItem('username') == null || localStorage.getItem('tokenID') == null)
        redirect('front.html');
};*/