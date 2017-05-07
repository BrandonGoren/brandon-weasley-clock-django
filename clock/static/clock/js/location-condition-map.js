function initMap() {
  $('#form').on('keyup keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    if (keyCode === 13) {
      e.preventDefault();
      return false;
    }
  });
  var lat = parseFloat(document.getElementById('id_lat').value);
  var lng = parseFloat(document.getElementById('id_lng').value);
  var preexistingValue = lat || lng;
  lat = lat || 38.888355;
  lng = lng || -77.023861;
  var latLng = {
    lat: lat,
    lng: lng
  };
  var map = new google.maps.Map(document.getElementById('map'), {
    center: latLng,
    zoom: preexistingValue? 15 : 12,
    streetViewControl: false
  });
  var circle;
  var input = document.getElementById('id_place_name');
  var autocomplete = new google.maps.places.Autocomplete(input, {
    placeIdOnly: true
  });
  autocomplete.setComponentRestrictions({
    'country': ['us', 'pr', 'vi', 'gu', 'mp']
  });
  var geocoder = new google.maps.Geocoder;
  var marker = new google.maps.Marker({
    map: map,
    title: 'hello',
    position: preexistingValue ? latLng : null
  });
  var radius = document.getElementById('id_radius').value;
  if (radius != null) {
    updateCircle();
  }
  autocomplete.addListener('place_changed', function() {
    var place = autocomplete.getPlace();
    if (!place.place_id) {
      return;
    }
    geocoder.geocode({
      'placeId': place.place_id
    }, function(results, status) {
      if (status !== 'OK') {
        window.alert('Geocoder failed due to: ' + status);
        return;
      }
      map.setZoom(15);
      map.setCenter(results[0].geometry.location);
      // Set the position of the marker using the place ID and location.
      marker.setPlace({
        placeId: place.place_id,
        location: results[0].geometry.location
      });
      document.getElementById('id_place_name').setAttribute('value', place.name);
      // Set hidden fields in form
      document.getElementById('id_lat').setAttribute('value', results[0].geometry.location.lat());
      document.getElementById('id_lng').setAttribute('value', results[0].geometry.location.lng());
      marker.setVisible(true);
      if (circle != null) {
        circle.setMap(null);
      }
      var radius = document.getElementById('id_radius').value;
      if (radius != null) {
        updateCircle();
      }
    });
  });

  $('#id_radius').on('input', function() {
    updateCircle();
  });

  function updateCircle() {
    if (circle != null) {
      circle.setMap(null);
    }
    var radius = document.getElementById('id_radius').value; // get the current value of the input field.
    circle = new google.maps.Circle({
      strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: '#FF0000',
      fillOpacity: 0.35,
      map: map,
      center: {
        lat: parseFloat(document.getElementById('id_lat').value),
        lng: parseFloat(document.getElementById('id_lng').value)
      },
      radius: radius * 1609.344 // convert miles to meters
    });
  }
}
