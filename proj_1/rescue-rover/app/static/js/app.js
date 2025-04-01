document.addEventListener('DOMContentLoaded', function() {
    // Get UI elements
    const batteryLevel = document.getElementById('battery-level');
    const batteryFill = document.getElementById('battery-fill');
    const position = document.getElementById('position');
    const status = document.getElementById('status');
    const communication = document.getElementById('communication');
    const survivors = document.getElementById('survivors');
    
    // Control buttons
    const btnForward = document.getElementById('btn-forward');
    const btnBackward = document.getElementById('btn-backward');
    const btnLeft = document.getElementById('btn-left');
    const btnRight = document.getElementById('btn-right');
    const btnStop = document.getElementById('btn-stop');
    
    // Add event listeners to buttons
    btnForward.addEventListener('click', () => sendCommand('forward'));
    btnBackward.addEventListener('click', () => sendCommand('backward'));
    btnLeft.addEventListener('click', () => sendCommand('left'));
    btnRight.addEventListener('click', () => sendCommand('right'));
    btnStop.addEventListener('click', () => sendCommand('stop'));
    
    // Send command to the rover
    function sendCommand(command) {
        fetch('/api/rover/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            }
        });
    }
    
    // Update UI with rover status
    function updateStatus() {
        fetch('/api/rover/status')
            .then(response => response.json())
            .then(data => {
                // Update battery
                batteryLevel.textContent = `${data.battery}%`;
                batteryFill.style.width = `${data.battery}%`;
                
                // Change battery color based on level
                if (data.battery < 10) {
                    batteryFill.style.backgroundColor = 'red';
                } else if (data.battery < 30) {
                    batteryFill.style.backgroundColor = 'orange';
                } else {
                    batteryFill.style.backgroundColor = 'green';
                }
                
                // Update position
                position.textContent = `(${data.position[0].toFixed(2)}, ${data.position[1].toFixed(2)})`;
                
                // Update status
                if (data.is_charging) {
                    status.textContent = 'Charging';
                } else if (data.is_moving) {
                    status.textContent = 'Moving';
                } else {
                    status.textContent = 'Idle';
                }
                
                // Update communication
                communication.textContent = data.has_communication ? 'Connected' : 'Disconnected';
                
                // Update survivors count
                survivors.textContent = data.survivors_found;
                
                // Disable buttons if charging or no communication
                const buttons = [btnForward, btnBackward, btnLeft, btnRight, btnStop];
                buttons.forEach(btn => {
                    btn.disabled = data.is_charging || !data.has_communication;
                });
            });
    }
    
    // Update status every second
    updateStatus();
    setInterval(updateStatus, 1000);
    
    // Initialize map visualization
    initMap();
});

function initMap() {
    // Map visualization code goes here
    // This will render the rover, obstacles, and survivors on the canvas
}
