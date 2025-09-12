(function() {

    const sensorData = [
        { lat: 48.210033, lng: 16.363449, type: 'happy' },
        { lat: 48.208174, lng: 16.373819, type: 'sad' },
        { lat: 48.20452, lng: 16.3564, type: 'neutral' }
    ];

    // Initialize Leaflet map
    const map = L.map('map').setView([48.208174, 16.373819], 14);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Function to create markers with earth icons
    function addSensorMarkers(data) {
        data.forEach(sensor => {
            let iconFile = 'happy-earth.png';

            if (sensor.type === 'sad') {
                iconFile = 'sad-earth.png';
            } else if (sensor.type === 'neutral') {
                iconFile = 'neutral-earth.png';
            }

            // Create HTML for the marker
            const html = `
                <div class="earth-marker">
                    <img src="assets/${iconFile}" alt="${sensor.type}-earth">
                </div>
            `;

            const icon = L.divIcon({
                html: html,
                className: '',
                iconSize: [48, 48],  // slightly bigger as discussed
                iconAnchor: [24, 24]
            });

            L.marker([sensor.lat, sensor.lng], { icon: icon })
             .addTo(map)
             .bindPopup(`Pollution: ${sensor.type}`);
        });
    }

    addSensorMarkers(sensorData);

    // User location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;

                const userIcon = L.icon({
                    iconUrl: 'assets/user-placeholder.png',
                    iconSize: [48, 48],
                    iconAnchor: [24, 24]
                });

                L.marker([userLat, userLng], { icon: userIcon })
                    .addTo(map)
                    .bindPopup("You are here");

                map.setView([userLat, userLng], 14);
            },
            error => {
                console.error("Error getting user location:", error);
            }
        );
    }

})();

