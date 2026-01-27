# 🎓 OCS Recruitment Portal - IIT Delhi

![Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Backend-Flask-blue)
![Frontend](https://img.shields.io/badge/Frontend-HTML%2FJS-orange)
![Database](https://img.shields.io/badge/Database-Supabase-green)

A secure, role-based recruitment management system developed for the **Office of Career Services (OCS)**. This portal facilitates the recruitment process by connecting students with recruiters while giving admins full oversight.

🔗 **[Live Demo: Click Here: https://ocs-portal-project-7ntm.vercel.app/**

---

## 🚀 Key Features

### 🔐 Security & Authentication
* **Client-Side Hashing:** Passwords are hashed using **MD5** on the browser before transmission, ensuring raw passwords never reach the server.
* **JWT Sessions:** Secure, stateless authentication using JSON Web Tokens (HS256).
* **Role-Based Access Control (RBAC):** Distinct dashboards and permissions for **Students**, **Recruiters**, and **Admins**.

### 🎓 Student Module
* **Selection Lock Logic:** Once a student receives a job offer, they are **automatically locked** from viewing or applying to other companies until they accept/reject the offer.
* **Real-time Dashboard:** View available jobs, application status, and offer letters instantly.

### 💼 Recruiter Module
* **Job Management:** Create and manage job profiles (e.g., Software Engineer, Data Analyst).
* **Applicant Filtering:** View students who have applied specifically to your company.
* **One-Click Hiring:** Select or reject candidates with immediate system updates.

### 🛡️ Admin Module
* **Global Oversight:** View all users, jobs, and applications in the system.
* **Status Override:** Manually update application statuses (e.g., force "Accept" or "Reject") to resolve conflicts.
* **Live Statistics:** Real-time counters for total applications and active jobs.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3 (Flat UI Design), Vanilla JavaScript (Fetch API).
* **Backend:** Python 3.9+, Flask (REST API).
* **Database:** PostgreSQL (Hosted on Supabase).
* **Deployment:** Vercel (Serverless Functions).

--