(function () {
    const container = document.getElementById("auth-map");
    if (!container || typeof L === "undefined") return;

    const map = L.map(container, {
        center: [-6.758, -38.233],
        zoom: 15,
        zoomControl: false,
        dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        touchZoom: false,
        keyboard: false,
        attributionControl: true,
        preferCanvas: true
    });

    L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        {
            maxZoom: 19,
            attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics"
        }
    ).addTo(map);

    let locationMarker;
    map.on("click", event => {
        if (!locationMarker) {
            locationMarker = L.marker(event.latlng, {
                interactive: false,
                icon: L.divIcon({
                    className: "auth-location-marker",
                    html: '<span class="auth-location-pulse"></span><span class="auth-location-pin"></span>',
                    iconSize: [40, 40],
                    iconAnchor: [20, 36]
                })
            }).addTo(map);
            return;
        }

        locationMarker.setLatLng(event.latlng);
    });

    window.addEventListener("resize", () => map.invalidateSize());
    window.setTimeout(() => map.invalidateSize(), 100);
})();
