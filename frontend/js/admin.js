document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadAdminData();
});

async function loadAdminData() {
    try {
        const headers = getAuthHeaders();

        // 1. Fetch Users
        const usersRes = await fetch(`${API_BASE_URL}/admin/users`, { headers });
        const usersData = await usersRes.json();
        renderUsers(usersData.users);

        // 2. Fetch Profiles (for stats only)
        const profilesRes = await fetch(`${API_BASE_URL}/api/admin/profiles`, { headers });
        const profilesData = await profilesRes.json();

        // 3. Fetch Applications
        const appsRes = await fetch(`${API_BASE_URL}/api/admin/applications`, { headers });
        const appsData = await appsRes.json();
        renderApplications(appsData.applications);

        // Update Stats
        document.getElementById('count-users').textContent = usersData.users.length;
        document.getElementById('count-profiles').textContent = profilesData.profiles.length;
        document.getElementById('count-applications').textContent = appsData.applications.length;

    } catch (error) {
        console.error("Admin load error:", error);
    }
}

function renderUsers(users) {
    const tbody = document.getElementById('admin-users-table');
    tbody.innerHTML = '';

    users.forEach(user => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.userid}</td>
            <td><span class="badge" style="background:#eee">${user.role}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderApplications(apps) {
    const tbody = document.getElementById('admin-apps-table');
    tbody.innerHTML = '';

    apps.forEach(app => {
        const tr = document.createElement('tr');

        // Admin dropdown to force status change
        const statusOptions = ['Applied', 'Selected', 'Not Selected', 'Accepted'];
        let selectHtml = `<select onchange="adminChangeStatus(this, '${app.profile_code}', '${app.entry_number}')" class="admin-select">`;

        statusOptions.forEach(status => {
            const selected = app.status === status ? 'selected' : '';
            selectHtml += `<option value="${status}" ${selected}>${status}</option>`;
        });
        selectHtml += `</select>`;

        tr.innerHTML = `
            <td><strong>${app.entry_number}</strong></td>
            <td>${app.company_name}</td>
            <td>${app.designation}</td>
            <td><span class="badge status-${app.status.toLowerCase().replace(' ', '-')}">${app.status}</span></td>
            <td>${selectHtml}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function adminChangeStatus(selectElem, profileCode, studentId) {
    const newStatus = selectElem.value;
    const originalValue = selectElem.getAttribute('data-original'); // You'd need to store this to be perfect, but skipping for simplicity

    if(!confirm(`⚠️ ADMIN OVERRIDE:\nForce change ${studentId}'s status to '${newStatus}'?`)) {
        // user cancelled, reload to reset dropdown
        loadAdminData();
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/recruiter/application/change_status`, {
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
            // refresh to show correct badges
            loadAdminData();
        } else {
            alert("Error: " + data.error);
        }
    } catch (error) {
        console.error(error);
        alert("Failed to update");
    }
}