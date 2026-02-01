document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    document.getElementById('userDisplay').textContent = localStorage.getItem('userid');

    loadApplications();

    // Handle Create Profile
    document.getElementById('createProfileForm').addEventListener('submit', createProfile);
});

async function createProfile(e) {
    e.preventDefault();
    const company = document.getElementById('companyName').value;
    const designation = document.getElementById('designation').value;

    try {
        const response = await fetch(`${API_BASE_URL}/recruiter/create_profile`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                company_name: company,
                designation: designation
            })
        });

        const data = await response.json();
        if (data.success) {
            alert(`Profile created! Code: ${data.profile_code}`);
            document.getElementById('createProfileForm').reset();
            loadApplications(); // Refresh list
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error(error);
        alert("Failed to create profile");
    }
}

async function loadApplications() {
    try {
        const response = await fetch(`${API_BASE_URL}/recruiter/applications`, {
            headers: getAuthHeaders()
        });

        const data = await response.json();
        const tbody = document.getElementById('applications-table-body');
        tbody.innerHTML = '';

        if (data.applications.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No applications yet.</td></tr>';
            return;
        }

        data.applications.forEach(app => {
            const tr = document.createElement('tr');

            // Determine available actions based on status
            let actionButtons = '';

            if (app.status === 'Applied') {
                actionButtons = `
                    <button onclick="updateStatus(${app.profile_code}, '${app.entry_number}', 'Selected')" class="btn-success btn-sm">Select</button>
                    <button onclick="updateStatus(${app.profile_code}, '${app.entry_number}', 'Not Selected')" class="btn-danger btn-sm">Reject</button>
                `;
            } else if (app.status === 'Selected') {
                actionButtons = `<span class="badge status-selected">Waiting for Student</span>`;
                // Option to revert if needed
                actionButtons += ` <button onclick="updateStatus(${app.profile_code}, '${app.entry_number}', 'Applied')" class="btn-sm" style="font-size:0.7rem; margin-left:5px;">Undo</button>`;
            } else {
                actionButtons = `<span class="badge status-${app.status.toLowerCase().replace(' ', '-')}">${app.status}</span>`;
            }

            tr.innerHTML = `
                <td>${app.profile_code}</td>
                <td>${app.company_name}</td>
                <td>${app.designation}</td>
                <td><strong>${app.entry_number}</strong></td>
                <td><span class="badge status-${app.status.toLowerCase().replace(' ', '-')}">${app.status}</span></td>
                <td>${actionButtons}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Error loading apps:", error);
    }
}

async function updateStatus(profileCode, studentId, newStatus) {
    if (!confirm(`Change status of ${studentId} to '${newStatus}'?`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/recruiter/application/change_status`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                profile_code: profileCode,
                entry_number: studentId,
                new_status: newStatus
            })
        });

        const data = await response.json();
        if (data.success) {
            loadApplications(); // Refresh table
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert("Failed to update status");
    }
}