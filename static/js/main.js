const geoBtn = document.getElementById('geoBtn');
if (geoBtn) {
  geoBtn.addEventListener('click', () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported in this browser.');
      return;
    }

    geoBtn.textContent = 'Detecting...';
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        document.getElementById('latitude').value = latitude.toFixed(6);
        document.getElementById('longitude').value = longitude.toFixed(6);
        document.getElementById('location_text').value ||= 'Auto-detected location';
        geoBtn.textContent = 'Location Captured ✓';
      },
      () => {
        geoBtn.textContent = 'Auto Detect Location';
        alert('Unable to fetch location. Please enter manually.');
      }
    );
  });
}

const counters = document.querySelectorAll('.counter');
counters.forEach((counter) => {
  const target = Number(counter.dataset.target || 0);
  let value = 0;
  const step = Math.max(1, Math.ceil(target / 50));
  const timer = setInterval(() => {
    value += step;
    if (value >= target) {
      value = target;
      clearInterval(timer);
    }
    counter.textContent = value;
  }, 20);
});

const mapNode = document.getElementById('map');
if (mapNode) {
  const map = L.map('map').setView([20.5937, 78.9629], 4);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  fetch('/api/plantations')
    .then((r) => r.json())
    .then((rows) => {
      rows.forEach((item) => {
        const marker = L.marker([item.latitude, item.longitude]).addTo(map);
        marker.bindPopup(`
          <b>${item.tree_name}</b><br>
          ${item.location_text}<br>
          By: ${item.username}<br>
          Status: ${item.status}
        `);
      });
    });
}
