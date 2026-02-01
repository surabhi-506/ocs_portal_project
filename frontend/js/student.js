document.addEventListener('DOMContentLoaded', () => {
    checkAuth(); // From utils.js
    loadDashboard();


    document.getElementById('userDisplay').textContent = localStorage.getItem('userid');
});

async function loadDashboard() {
    const loading = document.getElementById('loading');
    const offerView = document.getElementById('offer-view');
    const browsingView = document.getElementById('browsing-view');

    try {
        // 1. First, check my own status (Are we locked?)
        const myAppsResponse = await fetch(`${API_BASE_URL}/student/applications/mine`, {
            headers: getAuthHeaders()
        });
        const myAppsData = await myAppsResponse.json();

        // Find if we have any 'Selected' or 'Accepted' offer
        const activeOffer = myAppsData.applications.find(app =>
            app.status === 'Selected' || app.status === 'Accepted'
        );

        loading.style.display = 'none';

        if (activeOffer) {

            console.log("User is locked by offer:", activeOffer);
            browsingView.style.display = 'none';
            offerView.style.display = 'block';
            renderOfferView(activeOffer);
        } else {

            console.log("User is free to browse");
            offerView.style.display = 'none';
            browsingView.style.display = 'block';


            loadProfiles(myAppsData.applications);
        }

    } catch (error) {
        console.error("Dashboard error:", error);
        loading.textContent = "Error loading dashboard. Please login again.";
    }
}

function renderOfferView(offer) {
    document.getElementById('offer-company').textContent = offer.company_name;
    document.getElementById('offer-role').textContent = offer.designation;

    const statusBadge = document.getElementById('offer-status');
    const actionsDiv = document.getElementById('offer-actions');
    const title = document.getElementById('offer-title');

    statusBadge.textContent = offer.status;
    statusBadge.className = `status-badge status-${offer.status.toLowerCase().replace(' ', '-')}`;

    if (offer.status === 'Accepted') {
        // If Accepted: Show Success, Hide Buttons
        title.textContent = "✅ Offer Accepted";
        actionsDiv.style.display = 'none';
    } else {
        // If Selected: Show Buttons
        title.textContent = "🎉 You have been Selected!";
        actionsDiv.style.display = 'flex';

        // Bind buttons
        document.getElementById('btn-accept').onclick = () => respondToOffer(offer.profile_code, 'accept');
        document.getElementById('btn-reject').onclick = () => respondToOffer(offer.profile_code, 'reject');
    }
}

async function loadProfiles(myApplications) {
    try {
        const response = await fetch(`${API_BASE_URL}/student/profiles`, {
            headers: getAuthHeaders()
        });

        if (response.status === 403) {
            // Safety fallback if backend blocks us
            return;
        }

        const data = await response.json();
        const tbody = document.getElementById('profiles-table-body');
        tbody.innerHTML = '';

        data.profiles.forEach(profile => {
            const tr = document.createElement('tr');

            // Check if I already applied to this profile
            const myApp = myApplications.find(app => app.profile_code === profile.profile_code);

            let actionHtml = '';
            if (myApp) {
                // Already applied
                actionHtml = `<span class="badge status-${myApp.status.toLowerCase().replace(' ', '-')}">${myApp.status}</span>`;
            } else {
                // Can apply
                actionHtml = `<button onclick="applyToJob(${profile.profile_code})" class="btn-apply">Apply</button>`;
            }

            tr.innerHTML = `
                <td>${profile.company_name}</td>
                <td>${profile.designation}</td>
                <td>${actionHtml}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("Error loading profiles:", error);
    }
}

// === ACTIONS ===

async function applyToJob(profileCode) {
    if(!confirm("Are you sure you want to apply?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/student/apply`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ profile_code: profileCode })
        });

        const data = await response.json();

        if (data.success) {
            alert("Applied successfully!");
            loadDashboard(); // Refresh UI
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert("Failed to apply");
    }
}

async function respondToOffer(profileCode, action) {
    // action is 'accept' or 'reject'
    if(!confirm(`Are you sure you want to ${action.toUpperCase()} this offer? This cannot be undone.`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/student/application/${action}`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ profile_code: profileCode })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadDashboard(); // Refresh UI
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert("Action failed");
    }
}