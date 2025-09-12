// Component-specific JavaScript functions with 'sm_' prefix
let sm_sensors = [
    { id: '1', name: 'Living Room', status: 'online', lastSeen: new Date(Date.now() - 5000), location: '1st Floor' },
    { id: '2', name: 'Kitchen', status: 'online', lastSeen: new Date(Date.now() - 15000), location: '1st Floor' },
    { id: '3', name: 'Office', status: 'offline', lastSeen: new Date(Date.now() - 1800000), location: '2nd Floor' },
    { id: '4', name: 'Bedroom', status: 'online', lastSeen: new Date(Date.now() - 120000), location: '2nd Floor' },
];

const sm_sensorList = document.getElementById('sm-sensor-list');
const sm_renameModal = document.getElementById('sm-rename-modal');
const sm_deleteModal = document.getElementById('sm-delete-modal');
const sm_locationModal = document.getElementById('sm-location-modal');
let sm_currentSensorId = null;

function sm_formatLastSeen(timestamp) {
    const now = new Date();
    const diffMs = now - timestamp;
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMinutes < 1) {
        return "Just now";
    } else if (diffMinutes < 60) {
        return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
        return timestamp.toLocaleString();
    }
}

function sm_renderSensors() {
    sm_sensorList.innerHTML = '';
    sm_sensors.forEach(sensor => {
        const statusClass = sensor.status === 'online' ? 'sm-status-online' : 'sm-status-offline';
        const statusText = sensor.status.charAt(0).toUpperCase() + sensor.status.slice(1);
        const locationText = sensor.location ? `<p class="text-gray-500 text-sm mb-1">Location: <span class="font-medium text-gray-600">${sensor.location}</span></p>` : '';

        const cardHtml = `
            <div class="sm-sensor-card bg-white p-6 rounded-xl border border-gray-200 flex flex-col">
                <div class="flex-grow">
                    <div class="flex items-start justify-between mb-2">
                        <h3 class="text-2xl font-bold text-gray-800 pr-2 overflow-hidden whitespace-nowrap overflow-ellipsis">${sensor.name}</h3>
                        <span class="sm-status-badge flex-shrink-0 ${statusClass}">${statusText}</span>
                    </div>
                    <p class="text-gray-500 text-xs mb-1">ID: ${sensor.id}</p>
                    ${locationText}
                    <p class="text-gray-500 text-sm mb-4">Last Seen: <span class="font-medium text-gray-600">${sm_formatLastSeen(sensor.lastSeen)}</span></p>
                </div>
                <div class="flex justify-end space-x-2 mt-auto">
                    <button onclick="sm_openLocationModal('${sensor.id}')" class="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors">Set Location</button>
                    <button onclick="sm_openRenameModal('${sensor.id}')" class="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors">Rename</button>
                    <button onclick="sm_openDeleteModal('${sensor.id}')" class="px-3 py-1 text-xs font-medium bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors">Delete</button>
                </div>
            </div>
        `;
        sm_sensorList.insertAdjacentHTML('beforeend', cardHtml);
    });
}

function sm_openRenameModal(sensorId) {
    sm_currentSensorId = sensorId;
    const sensor = sm_sensors.find(s => s.id === sensorId);
    document.getElementById('sm-new-sensor-name-input').value = sensor.name;
    sm_renameModal.style.display = 'block';
}

function sm_closeRenameModal() {
    sm_renameModal.style.display = 'none';
}

function sm_saveRename() {
    const newName = document.getElementById('sm-new-sensor-name-input').value;
    if (newName.trim() === '') {
        sm_showMessageBox("Sensor name cannot be empty.");
        return;
    }
    const sensorIndex = sm_sensors.findIndex(s => s.id === sm_currentSensorId);
    if (sensorIndex !== -1) {
        sm_sensors[sensorIndex].name = newName;
        sm_renderSensors();
        sm_closeRenameModal();
    }
}

function sm_openDeleteModal(sensorId) {
    sm_currentSensorId = sensorId;
    const sensor = sm_sensors.find(s => s.id === sensorId);
    document.getElementById('sm-sensor-name-to-delete').textContent = sensor.name;
    sm_deleteModal.style.display = 'block';
}

function sm_closeDeleteModal() {
    sm_deleteModal.style.display = 'none';
}

function sm_confirmDelete() {
    sm_sensors = sm_sensors.filter(s => s.id !== sm_currentSensorId);
    sm_renderSensors();
    sm_closeDeleteModal();
}

function sm_openLocationModal(sensorId) {
    sm_currentSensorId = sensorId;
    const sensor = sm_sensors.find(s => s.id === sensorId);
    document.getElementById('sm-new-location-input').value = sensor.location || '';
    sm_locationModal.style.display = 'block';
}

function sm_closeLocationModal() {
    sm_locationModal.style.display = 'none';
}

function sm_saveLocation() {
    const newLocation = document.getElementById('sm-new-location-input').value;
    const sensorIndex = sm_sensors.findIndex(s => s.id === sm_currentSensorId);
    if (sensorIndex !== -1) {
        sm_sensors[sensorIndex].location = newLocation.trim();
        sm_renderSensors();
        sm_closeLocationModal();
    }
}

function sm_showMessageBox(message) {
    const msgBox = document.createElement('div');
    msgBox.className = 'fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg shadow-lg p-6 z-50 text-center border-t-4 border-blue-500';
    msgBox.innerHTML = `
        <p class="mb-4 text-lg text-gray-800">${message}</p>
        <button onclick="this.parentNode.remove()" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">OK</button>
    `;
    document.body.appendChild(msgBox);
}

document.addEventListener('DOMContentLoaded', () => {
    sm_renderSensors();
});

