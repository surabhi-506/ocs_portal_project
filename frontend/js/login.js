document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const loginBtn = document.getElementById('loginBtn');

    // Clear any existing session
    localStorage.clear();

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reset error
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
        loginBtn.disabled = true;
        loginBtn.textContent = 'Logging in...';

        const userid = document.getElementById('userid').value.trim();
        const rawPassword = document.getElementById('password').value;

        try {
            // CONSTRAINT: Client-side MD5 Hashing
            // We use CryptoJS (loaded in index.html) to hash the password
            const password_md5 = CryptoJS.MD5(rawPassword).toString();

            console.log("Attempting login for:", userid);
            console.log("Sending Hash:", password_md5);

            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userid: userid,
                    password_md5: password_md5
                })
            });

            const data = await response.json();

            if (data.success) {
                // Store session data
                localStorage.setItem('token', data.token);
                localStorage.setItem('role', data.role);
                localStorage.setItem('userid', data.userid);

                // Redirect based on role
                if (data.role === 'student') {
                    window.location.href = 'student.html';
                } else if (data.role === 'recruiter') {
                    window.location.href = 'recruiter.html';
                } else if (data.role === 'admin') {
                    window.location.href = 'admin.html';
                }
            } else {
                throw new Error(data.error || 'Login failed');
            }

        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
            loginBtn.disabled = false;
            loginBtn.textContent = 'Login';
        }
    });
});