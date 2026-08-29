// Global state
let currentMachineId = null;
let authToken = null;

/**
 * Enhanced fetch wrapper that attaches the Bearer token.
 */
async function fetchWithAuth(url, options = {}) {
    if (!options.headers) options.headers = {};
    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(url, options);
    
    if (response.status === 401 || response.status === 403) {
        // Token invalid, expired, or insufficient permissions
        showLoginOverlay();
        throw new Error("Unauthorized or Forbidden");
    }
    
    return response;
}

/**
 * Auth UI flow
 */
function showLoginOverlay() {
    document.getElementById('loginOverlay').style.display = 'flex';
    document.getElementById('logoutBtn').style.display = 'none';
}

function hideLoginOverlay() {
    document.getElementById('loginOverlay').style.display = 'none';
    document.getElementById('logoutBtn').style.display = 'block';
}

document.getElementById('loginForm').onsubmit = async (e) => {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        
        if (!response.ok) throw new Error('Invalid credentials');
        
        const data = await response.json();
        authToken = data.access_token;
        
        hideLoginOverlay();
        document.getElementById('loginError').style.display = 'none';
        
        // Initial load after login
        loadMachines();
        loadMaintenance();
        loadAnalytics();
    } catch (err) {
        const errEl = document.getElementById('loginError');
        errEl.textContent = 'Invalid email or password';
        errEl.style.display = 'block';
    }
};

document.getElementById('logoutBtn').onclick = () => {
    authToken = null;
    document.getElementById('machineList').innerHTML = 'Loading machines...';
    document.getElementById('maintenanceList').innerHTML = 'Loading maintenance schedule...';
    document.getElementById('analyticsSummary').innerHTML = '<div class="summary-box">Loading...</div>';
    document.getElementById('auditLogsBody').innerHTML = '<tr><td colspan="5">Loading logs...</td></tr>';
    document.getElementById('editPanel').style.display = 'none';
    showLoginOverlay();
};

/**
 * Initializes the dashboard by fetching the list of machines.
 */
async function loadMachines() {
    try {
        const response = await fetchWithAuth('/api/machine/');
        const machines = await response.json();
        
        const listEl = document.getElementById('machineList');
        listEl.innerHTML = '';
        
        machines.forEach(machine => {
            const item = document.createElement('div');
            item.className = 'machine-item';
            item.id = `machine-item-${machine.id}`;
            item.onclick = () => selectMachine(machine);
            
            let html = `<strong>${machine.name}</strong>`;
            if (machine.emergency) {
                html += `<span class="emergency-badge">EMERGENCY</span>`;
            }
            
            item.innerHTML = html;
            listEl.appendChild(item);
        });
    } catch (err) {
        showStatus('Failed to load machines', true);
    }
}

/**
 * Fetches and displays upcoming maintenance tasks.
 */
async function loadMaintenance() {
    try {
        const response = await fetchWithAuth('/api/maintenance/');
        if (!response.ok) throw new Error('Maintenance denied');
        
        let records = await response.json();
        
        // Filter out records without a due date and sort by next_due_at ascending
        records = records.filter(r => r.next_due_at).sort((a, b) => new Date(a.next_due_at) - new Date(b.next_due_at));
        
        const listEl = document.getElementById('maintenanceList');
        listEl.innerHTML = '';
        
        if (records.length === 0) {
            listEl.innerHTML = '<em>No upcoming maintenance scheduled.</em>';
            return;
        }
        
        records.forEach(record => {
            const item = document.createElement('div');
            item.className = 'machine-item';
            
            const dueDate = new Date(record.next_due_at).toLocaleDateString();
            item.innerHTML = `<div><strong>${record.machine_id}</strong><br><small style="color: #6b7280">${record.description}</small></div><div style="text-align:right"><small style="font-weight:bold; color: #b45309">Due: ${dueDate}</small></div>`;
            listEl.appendChild(item);
        });
    } catch (err) {
        // Normal behavior if the user is not an Admin or Technician
        document.getElementById('maintenanceList').innerHTML = '<em>Permission denied or error loading maintenance.</em>';
    }
}

/**
 * Fetches and displays analytics summary and audit logs.
 */
async function loadAnalytics() {
    try {
        const [summaryRes, logsRes] = await Promise.all([
            fetchWithAuth('/api/analytics/summary'),
            fetchWithAuth('/api/analytics/logs?limit=20')
        ]);
        
        if (!summaryRes.ok || !logsRes.ok) {
            throw new Error('Analytics denied');
        }
        
        const summary = await summaryRes.json();
        const logs = await logsRes.json();
        
        // Render Summary
        const totalChats = Object.values(summary.chats_per_machine || {}).reduce((a, b) => a + b, 0);
        document.getElementById('analyticsSummary').innerHTML = `
            <div class="summary-box">
                <strong>${totalChats}</strong>
                Total Chats
            </div>
            <div class="summary-box">
                <strong>${summary.total_emergency_activations || 0}</strong>
                Emergencies
            </div>
            <div class="summary-box">
                <strong>${summary.active_devices || 0}</strong>
                Active Devices
            </div>
        `;
        
        // Render Logs
        const logsBody = document.getElementById('auditLogsBody');
        logsBody.innerHTML = '';
        if (logs.length === 0) {
            logsBody.innerHTML = '<tr><td colspan="5">No actions recorded yet.</td></tr>';
            return;
        }
        
        logs.forEach(log => {
            const tr = document.createElement('tr');
            const time = new Date(log.timestamp).toLocaleString();
            tr.innerHTML = `
                <td>${time}</td>
                <td>${log.user_id || 'Unknown'}</td>
                <td><strong>${log.action}</strong></td>
                <td>${log.target_type}: ${log.target_id}</td>
                <td style="max-width:200px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title='${log.details || ''}'>
                    ${log.details || '-'}
                </td>
            `;
            logsBody.appendChild(tr);
        });
        
    } catch (err) {
        document.getElementById('analyticsSummary').innerHTML = '<div class="summary-box">Analytics access restricted to Admins.</div>';
        document.getElementById('auditLogsBody').innerHTML = '<tr><td colspan="5">Permission denied</td></tr>';
    }
}

/**
 * Handles selecting a machine from the list.

 * Fetches the latest config for the selected machine and populates the edit form.
 */
async function selectMachine(machineStub) {
    currentMachineId = machineStub.id;
    
    // Highlight selected item in the list
    document.querySelectorAll('.machine-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`machine-item-${machineStub.id}`).classList.add('active');
    
    try {
        const response = await fetchWithAuth(`/api/machine/${currentMachineId}/config`);
        const machine = await response.json();
        
        // Show edit panel
        document.getElementById('editPanel').style.display = 'block';
        document.getElementById('machineName').textContent = machine.name;
        document.getElementById('safetyText').value = machine.safety_text;
        
        // Update emergency state UI
        updateEmergencyUI(machine.emergency);
        
        // Render SOP list
        renderSopList(machine.sop);
        
    } catch (err) {
        showStatus('Failed to load machine configuration', true);
    }
}

/**
 * Renders the SOP list with inputs and remove/reorder buttons.
 */
function renderSopList(sopArray) {
    const listEl = document.getElementById('sopList');
    listEl.innerHTML = '';
    
    sopArray.forEach((step, index) => {
        const li = document.createElement('li');
        li.className = 'sop-item';
        
        // Input for the step
        const input = document.createElement('input');
        input.type = 'text';
        input.value = step;
        input.className = 'sop-input';
        
        // Move up button
        const upBtn = document.createElement('button');
        upBtn.textContent = '↑';
        upBtn.type = 'button';
        upBtn.onclick = () => moveSop(index, -1);
        upBtn.disabled = index === 0;
        
        // Move down button
        const downBtn = document.createElement('button');
        downBtn.textContent = '↓';
        downBtn.type = 'button';
        downBtn.onclick = () => moveSop(index, 1);
        downBtn.disabled = index === sopArray.length - 1;
        
        // Remove button
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'X';
        removeBtn.type = 'button';
        removeBtn.onclick = () => removeSop(index);
        
        li.appendChild(input);
        li.appendChild(upBtn);
        li.appendChild(downBtn);
        li.appendChild(removeBtn);
        
        listEl.appendChild(li);
    });
}

/**
 * Helper to get the current SOP array from DOM inputs.
 */
function getSopFromDOM() {
    const inputs = document.querySelectorAll('.sop-input');
    return Array.from(inputs).map(input => input.value);
}

/**
 * Adds a new empty SOP step.
 */
document.getElementById('addSopBtn').onclick = () => {
    const currentSop = getSopFromDOM();
    currentSop.push('');
    renderSopList(currentSop);
};

/**
 * Removes an SOP step at a specific index.
 */
function removeSop(index) {
    const currentSop = getSopFromDOM();
    currentSop.splice(index, 1);
    renderSopList(currentSop);
}

/**
 * Moves an SOP step up or down.
 */
function moveSop(index, direction) {
    const currentSop = getSopFromDOM();
    const targetIndex = index + direction;
    
    // Swap elements
    const temp = currentSop[index];
    currentSop[index] = currentSop[targetIndex];
    currentSop[targetIndex] = temp;
    
    renderSopList(currentSop);
}

/**
 * Saves the SOP and Safety Text changes.
 */
document.getElementById('saveBtn').onclick = async () => {
    if (!currentMachineId) return;
    
    const updateData = {
        sop: getSopFromDOM(),
        safety_text: document.getElementById('safetyText').value
    };
    
    try {
        const response = await fetchWithAuth(`/api/machine/${currentMachineId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });
        
        if (!response.ok) throw new Error('Save failed');
        
        const updatedMachine = await response.json();
        
        // Re-render SOPs to ensure they match backend
        renderSopList(updatedMachine.sop);
        document.getElementById('safetyText').value = updatedMachine.safety_text;
        
        showStatus('Machine updated successfully!', false);
    } catch (err) {
        showStatus('Failed to update machine', true);
    }
};

/**
 * Toggles the emergency state for the current machine.
 */
document.getElementById('emergencyBtn').onclick = async () => {
    if (!currentMachineId) return;
    
    // Determine the new state based on current UI
    const isCurrentlyEmergency = document.getElementById('emergencyBanner').style.display === 'block';
    const newState = !isCurrentlyEmergency;
    
    try {
        const response = await fetchWithAuth(`/api/machine/${currentMachineId}/emergency`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emergency: newState })
        });
        
        if (!response.ok) throw new Error('Emergency toggle failed');
        
        const updatedMachine = await response.json();
        
        // Visibly reflect new state using actual API response
        updateEmergencyUI(updatedMachine.emergency);
        
        // Also reload the machine list to update the badges
        loadMachines();
        
        showStatus('Emergency state updated successfully!', false);
    } catch (err) {
        showStatus('Failed to update emergency state', true);
    }
};

/**
 * Updates the UI (Banner and Button) based on emergency state.
 */
function updateEmergencyUI(isEmergency) {
    const banner = document.getElementById('emergencyBanner');
    const btn = document.getElementById('emergencyBtn');
    
    if (isEmergency) {
        banner.style.display = 'block';
        btn.textContent = 'DEACTIVATE EMERGENCY';
    } else {
        banner.style.display = 'none';
        btn.textContent = 'TRIGGER EMERGENCY';
    }
}

/**
 * Shows a status message for 3 seconds.
 */
function showStatus(message, isError) {
    const el = document.getElementById('statusMessage');
    el.textContent = message;
    el.className = 'status-message ' + (isError ? 'status-error' : 'status-success');
    el.style.display = 'block';
    
    setTimeout(() => {
        el.style.display = 'none';
    }, 3000);
}

// Start by showing login (we don't load data until auth'd)
showLoginOverlay();
