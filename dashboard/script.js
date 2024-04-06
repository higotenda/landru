document.getElementById("locationForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var location = document.getElementById("locationInput").value;

    // Initialize the Leaflet map (if needed)
    if (!map) {
      var map = L.map('map').setView([41.4549665, -70.5606838], 13); 
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map); 
    }

    // Search for the location using Nominatim
    fetch('https://nominatim.openstreetmap.org/search?q=' + encodeURIComponent(location) + '&format=json')
      .then(response => response.json())
      .then(data => {
        if (data.length > 0) {
          var lat = data[0].lat;
          var lon = data[0].lon;
          map.setView([lat, lon], 13); 
          L.marker([lat, lon]).addTo(map); 
        } else {
          alert("Location not found."); 
        }
      }); 
  });
