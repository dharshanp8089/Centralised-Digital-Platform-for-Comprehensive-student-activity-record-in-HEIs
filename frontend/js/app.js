const API_URL = "http://localhost:8000/api";

// Global Application State
let currentUser = null;
let currentToken = null;
let charts = {}; // Holds Chart.js instances

// ----------------- Initialization -----------------
document.addEventListener("DOMContentLoaded", () => {
    initApp();
    setupEventListeners();
});

function initApp() {
    currentToken = localStorage.getItem("access_token");
    const userStr = localStorage.getItem("user_data");
    
    if (currentToken && userStr) {
        try {
            currentUser = JSON.parse(userStr);
            renderSidebarAndNav();
            
            // Redirect to appropriate dashboard based on role
            if (currentUser.role === "admin") {
                showView("admin-dashboard");
            } else if (currentUser.role === "faculty") {
                showView("faculty-dashboard");
            } else {
                showView("student-dashboard");
            }
        } catch (e) {
            console.error("Failed to parse user details:", e);
            logout();
        }
    } else {
        // Not logged in -> Show login view
        logout();
    }
}

// ----------------- Sidebar & Nav Rendering -----------------
function renderSidebarAndNav() {
    if (!currentUser) return;
    
    // Show sidebar & main app structure, hide auth containers
    document.getElementById("sidebar-element").style.display = "flex";
    document.getElementById("top-header").style.display = "flex";
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("main-container").style.marginLeft = ""; // Use CSS default

    // Set user card details in sidebar
    document.getElementById("sb-user-name").textContent = currentUser.name;
    document.getElementById("sb-user-role").textContent = currentUser.role.toUpperCase();
    document.getElementById("sb-avatar-letters").textContent = currentUser.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();

    // Show role-specific links
    document.querySelectorAll(".role-link").forEach(el => el.style.display = "none");
    document.querySelectorAll(`.role-${currentUser.role}`).forEach(el => el.style.display = "flex");
}

// ----------------- Router / View Manager -----------------
function showView(viewId) {
    // Hide all views
    document.querySelectorAll(".view-section").forEach(el => {
        el.style.display = "none";
        el.classList.remove("animated-view");
    });

    // Show target view
    const targetView = document.getElementById(viewId);
    if (targetView) {
        targetView.style.display = "block";
        targetView.classList.add("animated-view");
    }

    // Set active link style in sidebar
    document.querySelectorAll(".nav-link-custom").forEach(el => el.classList.remove("active"));
    const activeLink = document.querySelector(`.nav-link-custom[data-view="${viewId}"]`);
    if (activeLink) {
        activeLink.classList.add("active");
    }

    // Load view-specific data
    if (viewId === "admin-dashboard") {
        loadAdminDashboard();
    } else if (viewId === "admin-users") {
        loadAdminUsers();
    } else if (viewId === "admin-departments") {
        loadAdminDepartments();
    } else if (viewId === "faculty-dashboard") {
        loadFacultyDashboard();
    } else if (viewId === "faculty-attendance") {
        loadFacultyAttendanceSheet();
    } else if (viewId === "student-dashboard") {
        loadStudentDashboard();
    } else if (viewId === "student-attendance") {
        loadStudentAttendanceLogs();
    }
}

// ----------------- Setup Action Listeners -----------------
function setupEventListeners() {
    // Navigation link clicks
    document.querySelectorAll(".nav-link-custom").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const viewId = link.getAttribute("data-view");
            if (viewId) showView(viewId);
        });
    });

    // Auth forms
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }
    
    const regForm = document.getElementById("register-form");
    if (regForm) {
        regForm.addEventListener("submit", handleRegistration);
    }

    // Student: Edit Profile details
    const studentProfileForm = document.getElementById("student-profile-form");
    if (studentProfileForm) {
        studentProfileForm.addEventListener("submit", updateStudentProfile);
    }

    // Student: Submit Activity Form
    const uploadActivityForm = document.getElementById("upload-activity-form");
    if (uploadActivityForm) {
        uploadActivityForm.addEventListener("submit", handleActivityUpload);
    }

    // Admin: Department creation form
    const addDeptForm = document.getElementById("add-dept-form");
    if (addDeptForm) {
        addDeptForm.addEventListener("submit", handleCreateDepartment);
    }

    // Admin: User creation form
    const addUserForm = document.getElementById("add-user-form");
    if (addUserForm) {
        addUserForm.addEventListener("submit", handleAdminCreateUser);
    }

    // Logout actions
    document.getElementById("btn-logout").addEventListener("click", logout);

    // Broadcast Announcement Form Submit
    const postAnnForm = document.getElementById("post-announcement-form");
    if (postAnnForm) {
        postAnnForm.addEventListener("submit", handlePostAnnouncement);
    }

    // Modal show listener to load department options
    const postAnnModal = document.getElementById("postAnnouncementModal");
    if (postAnnModal) {
        postAnnModal.addEventListener("show.bs.modal", setupAnnouncementsModal);
    }
    
    // Toggle login/register switch
    const toggleToReg = document.getElementById("link-to-register");
    if (toggleToReg) {
        toggleToReg.addEventListener("click", (e) => {
            e.preventDefault();
            document.getElementById("login-box").style.display = "none";
            document.getElementById("register-box").style.display = "block";
            loadRegisterDepartments();
        });
    }

    const toggleToLog = document.getElementById("link-to-login");
    if (toggleToLog) {
        toggleToLog.addEventListener("click", (e) => {
            e.preventDefault();
            document.getElementById("register-box").style.display = "none";
            document.getElementById("login-box").style.display = "block";
        });
    }

    // Dynamic role layout on registration form
    const regRoleSelect = document.getElementById("reg-role");
    if (regRoleSelect) {
        regRoleSelect.addEventListener("change", () => {
            const role = regRoleSelect.value;
            if (role === "student") {
                document.getElementById("student-fields").style.display = "block";
                document.getElementById("faculty-fields").style.display = "none";
                document.getElementById("reg-roll").setAttribute("required", "required");
                document.getElementById("reg-fac-id").removeAttribute("required");
            } else {
                document.getElementById("student-fields").style.display = "none";
                document.getElementById("faculty-fields").style.display = "block";
                document.getElementById("reg-roll").removeAttribute("required");
                document.getElementById("reg-fac-id").setAttribute("required", "required");
            }
        });
    }

    // Dynamic role layout on admin register user modal
    const adminUserRoleSelect = document.getElementById("admin-add-role");
    if (adminUserRoleSelect) {
        adminUserRoleSelect.addEventListener("change", () => {
            const role = adminUserRoleSelect.value;
            if (role === "student") {
                document.getElementById("admin-student-fields").style.display = "block";
                document.getElementById("admin-faculty-fields").style.display = "none";
                document.getElementById("admin-reg-roll").setAttribute("required", "required");
                document.getElementById("admin-reg-fac-id").removeAttribute("required");
            } else if (role === "faculty") {
                document.getElementById("admin-student-fields").style.display = "none";
                document.getElementById("admin-faculty-fields").style.display = "block";
                document.getElementById("admin-reg-roll").removeAttribute("required");
                document.getElementById("admin-reg-fac-id").setAttribute("required", "required");
            } else {
                // Admin role
                document.getElementById("admin-student-fields").style.display = "none";
                document.getElementById("admin-faculty-fields").style.display = "none";
                document.getElementById("admin-reg-roll").removeAttribute("required");
                document.getElementById("admin-reg-fac-id").removeAttribute("required");
            }
        });
    }
}

// ----------------- Auth API Connectors -----------------
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed");
        }
        
        // Save state
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_data", JSON.stringify(data));
        
        showToast("Success", "Welcome back! Login successful.", "success");
        initApp();
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function handleRegistration(e) {
    e.preventDefault();
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const name = document.getElementById("reg-name").value;
    const role = document.getElementById("reg-role").value;
    const department_id = parseInt(document.getElementById("reg-dept").value);
    
    let url = `${API_URL}/auth/register/student`;
    let payload = { email, password, name, department_id };
    
    if (role === "student") {
        payload.roll_number = document.getElementById("reg-roll").value;
        payload.semester = parseInt(document.getElementById("reg-semester").value);
        payload.phone = document.getElementById("reg-phone").value;
    } else {
        url = `${API_URL}/auth/register/faculty`;
        payload.faculty_id = document.getElementById("reg-fac-id").value;
        payload.designation = document.getElementById("reg-designation").value;
    }
    
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Registration failed");
        }
        
        showToast("Success", "Registration completed! Please log in.", "success");
        document.getElementById("register-box").style.display = "none";
        document.getElementById("login-box").style.display = "block";
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_data");
    currentUser = null;
    currentToken = null;

    // Reset layout view
    document.getElementById("sidebar-element").style.display = "none";
    document.getElementById("top-header").style.display = "none";
    document.getElementById("main-container").style.marginLeft = "0";
    
    document.getElementById("auth-view").style.display = "flex";
    document.getElementById("login-box").style.display = "block";
    document.getElementById("register-box").style.display = "none";
}

// ----------------- Student Module Functions -----------------
async function loadStudentDashboard() {
    if (!currentToken) return;
    
    try {
        // 1. Load Profile details
        const profRes = await fetch(`${API_URL}/students/profile`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const prof = await profRes.json();
        if (profRes.ok) {
            document.getElementById("stud-dashboard-title").textContent = `Welcome, ${prof.name}`;
            document.getElementById("stud-roll").textContent = prof.roll_number;
            document.getElementById("stud-dept").textContent = prof.department_name || "N/A";
            document.getElementById("stud-sem").textContent = `Semester ${prof.semester}`;
            
            // Set input values for editing
            document.getElementById("edit-phone").value = prof.phone || "";
            document.getElementById("edit-semester").value = prof.semester || 1;
            document.getElementById("edit-cgpa").value = prof.cgpa.toFixed(2);
            
            // Animate CGPA Progress
            const cgpaPercent = (prof.cgpa / 10.0) * 100;
            document.getElementById("cgpa-value").textContent = prof.cgpa.toFixed(2);
            document.getElementById("cgpa-bar").style.width = `${cgpaPercent}%`;
            
            // Animate Attendance Progress
            document.getElementById("att-value").textContent = `${prof.attendance_percentage.toFixed(1)}%`;
            document.getElementById("att-bar").style.width = `${prof.attendance_percentage}%`;
            
            // Color attendance based on threshold
            const attBar = document.getElementById("att-bar");
            attBar.className = "progress-bar-custom"; // reset
            if (prof.attendance_percentage < 75) {
                attBar.style.background = "var(--color-danger)";
            } else if (prof.attendance_percentage < 85) {
                attBar.style.background = "var(--color-warning)";
            } else {
                attBar.style.background = "linear-gradient(90deg, var(--color-success), var(--accent-cyan))";
            }
        }
        
        // 2. Load Activities Logs
        const actRes = await fetch(`${API_URL}/students/activities`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const acts = await actRes.json();
        
        const grid = document.getElementById("student-activities-grid");
        grid.innerHTML = "";
        
        if (actRes.ok && acts.length > 0) {
            acts.forEach(act => {
                const col = document.createElement("div");
                col.className = "col-md-6 col-lg-4 mb-4";
                
                const badgeClass = act.status === "approved" ? "approved" : act.status === "rejected" ? "rejected" : "pending";
                
                let iconClass = "bi-journal-code";
                if (act.category === "internship") iconClass = "bi-briefcase";
                else if (act.category === "certification") iconClass = "bi-patch-check";
                else if (act.category === "extracurricular") iconClass = "bi-trophy";
                else if (act.category === "placement") iconClass = "bi-building-up";

                const viewBtn = act.certificate_url 
                    ? `<button class="btn btn-secondary-custom btn-sm-custom w-100 mt-3 py-1" onclick="viewCertificate('${act.certificate_url}')"><i class="bi bi-file-earmark-pdf"></i> View Certificate</button>`
                    : "";

                const commentMarkup = act.status === "rejected" && act.rejection_comment
                    ? `<div class="text-danger small mt-2 p-2 rounded" style="background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.3);"><strong>Reason:</strong> ${escapeHTML(act.rejection_comment)}</div>`
                    : "";
                    
                col.innerHTML = `
                    <div class="glass-card h-100 d-flex flex-column" style="padding: 1.25rem;">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge-custom ${badgeClass}">${act.status.toUpperCase()}</span>
                            <div><i class="bi ${iconClass} fs-5 text-info"></i></div>
                        </div>
                        <h5 class="text-white mb-2" style="font-size: 1.05rem; font-weight: 600;">${escapeHTML(act.title)}</h5>
                        <p class="text-capitalize small mb-2"><span class="badge-custom text-info text-capitalize py-0 px-2" style="background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.2);">${act.category}</span></p>
                        <p class="text-secondary small mb-3 flex-grow-1" style="display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;">${escapeHTML(act.description) || "No description provided."}</p>
                        
                        <div class="mt-auto border-top pt-2" style="border-color: var(--border-color) !important;">
                            <div class="d-flex justify-content-between text-secondary small mb-1">
                                <span>Duration:</span>
                                <span class="text-white">${formatDate(act.start_date)} - ${formatDate(act.end_date)}</span>
                            </div>
                            <div class="d-flex justify-content-between text-secondary small">
                                <span>Verified By:</span>
                                <span class="text-white">${act.verifier_name || "-"}</span>
                            </div>
                            ${commentMarkup}
                            ${viewBtn}
                        </div>
                    </div>
                `;
                grid.appendChild(col);
            });
        } else {
            grid.innerHTML = `<div class="col-12 text-center text-muted py-4">No activities logged yet. Click "Add Activity Record" to upload one.</div>`;
        }

        // Fetch announcements for Student
        loadAnnouncements();
    } catch (e) {
        showToast("Error", "Failed to retrieve student dashboard data.", "danger");
    }
}

async function updateStudentProfile(e) {
    e.preventDefault();
    const phone = document.getElementById("edit-phone").value;
    const semester = parseInt(document.getElementById("edit-semester").value);
    const cgpa = parseFloat(document.getElementById("edit-cgpa").value);
    
    try {
        const response = await fetch(`${API_URL}/students/profile`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentToken}`
            },
            body: JSON.stringify({ phone, semester, cgpa })
        });
        
        if (response.ok) {
            showToast("Success", "Profile details successfully updated.", "success");
            // Hide Bootstrap modal programmatically
            const modalEl = document.getElementById("editProfileModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            loadStudentDashboard();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update profile");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function handleActivityUpload(e) {
    e.preventDefault();
    const title = document.getElementById("act-title").value;
    const category = document.getElementById("act-category").value;
    const description = document.getElementById("act-desc").value;
    const start_date = document.getElementById("act-start").value;
    const end_date = document.getElementById("act-end").value;
    const fileInput = document.getElementById("act-file");
    
    if (fileInput.files.length === 0) {
        showToast("Validation Error", "Please select a certificate document to upload.", "warning");
        return;
    }
    
    const formData = new FormData();
    formData.append("title", title);
    formData.append("category", category);
    formData.append("description", description);
    if (start_date) formData.append("start_date", start_date);
    if (end_date) formData.append("end_date", end_date);
    formData.append("file", fileInput.files[0]);
    
    // Show spinner loading
    const submitBtn = e.target.querySelector("button[type='submit']");
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...`;
    
    try {
        const response = await fetch(`${API_URL}/students/activities`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${currentToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            showToast("Success", "Activity record submitted for verification.", "success");
            document.getElementById("upload-activity-form").reset();
            
            // Close modal
            const modalEl = document.getElementById("addActivityModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            loadStudentDashboard();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Failed to submit activity");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

async function loadStudentAttendanceLogs() {
    if (!currentToken) return;
    
    try {
        const response = await fetch(`${API_URL}/students/attendance`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const logs = await response.json();
        
        // Render Heatmap Grid
        renderAttendanceHeatmap(logs);
        
        const grid = document.getElementById("student-attendance-grid");
        grid.innerHTML = "";
        
        if (response.ok && logs.length > 0) {
            logs.forEach(log => {
                const div = document.createElement("div");
                const badgeClass = log.status === "present" ? "present" : log.status === "absent" ? "absent" : "late";
                
                const logDate = new Date(log.date);
                const dayStr = logDate.toLocaleDateString("en-US", { day: "numeric" });
                const monthStr = logDate.toLocaleDateString("en-US", { month: "short" });
                
                div.className = `attendance-tile ${badgeClass}`;
                div.title = `Date: ${formatDate(log.date)} | Status: ${log.status.toUpperCase()}`;
                
                div.innerHTML = `
                    <div style="font-size: 1.15rem; font-weight: 700; line-height: 1;">${dayStr}</div>
                    <div style="font-size: 0.65rem; text-transform: uppercase; margin-top: 2px; opacity: 0.85;">${monthStr}</div>
                `;
                grid.appendChild(div);
            });
        } else {
            grid.innerHTML = `<div class="text-center text-muted py-4 w-100">No attendance records registered yet.</div>`;
        }
    } catch (e) {
        showToast("Error", "Failed to retrieve attendance logs.", "danger");
    }
}

// ----------------- Faculty Module Functions -----------------
async function loadFacultyDashboard() {
    if (!currentToken) return;
    
    try {
        // 1. Load pending verification queue
        const pendRes = await fetch(`${API_URL}/faculty/pending-activities`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const queue = await pendRes.json();
        
        const container = document.getElementById("faculty-verification-queue");
        container.innerHTML = "";
        
        if (pendRes.ok && queue.length > 0) {
            queue.forEach(act => {
                const col = document.createElement("div");
                col.className = "col-md-6 col-lg-4 mb-4";
                
                col.innerHTML = `
                    <div class="glass-card h-100 d-flex flex-column">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="badge-custom pending text-uppercase">${act.category}</span>
                            <span class="text-muted small">${formatDate(act.created_at)}</span>
                        </div>
                        <h5 class="mb-1 text-truncate">${escapeHTML(act.title)}</h5>
                        <p class="text-secondary small mb-3">Submitted by <strong>${escapeHTML(act.student_name)}</strong> (${act.student_roll})</p>
                        <p class="text-muted small flex-grow-1 text-truncate-3">${escapeHTML(act.description) || "No description provided."}</p>
                        
                        <div class="mt-auto pt-3 border-top d-flex gap-2">
                            <button class="btn btn-secondary-custom btn-sm-custom flex-fill" onclick="viewCertificate('${act.certificate_url}')">
                                <i class="bi bi-eye"></i> View Doc
                            </button>
                            <button class="btn btn-primary-custom btn-sm-custom flex-fill" onclick="openApprovalModal(${act.id}, '${escapeHTML(act.title)}')">
                                <i class="bi bi-check-circle"></i> Verify
                            </button>
                        </div>
                    </div>
                `;
                container.appendChild(col);
            });
        } else {
            container.innerHTML = `<div class="col-12 text-center text-muted py-5">
                <i class="bi bi-file-earmark-check fs-1"></i>
                <p class="mt-2">Verification queue is empty. No pending certificates.</p>
            </div>`;
        }
        
        // 2. Load Department Student list
        const studRes = await fetch(`${API_URL}/faculty/students`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const students = await studRes.json();
        
        const tbody = document.getElementById("faculty-students-tbody");
        tbody.innerHTML = "";
        
        if (studRes.ok && students.length > 0) {
            students.forEach(s => {
                const tr = document.createElement("tr");
                
                // Color code low attendance values
                const attClass = s.attendance_percentage < 75 ? "text-danger font-weight-bold" : s.attendance_percentage < 85 ? "text-warning" : "text-success";
                
                tr.innerHTML = `
                    <td><strong>${s.roll_number}</strong></td>
                    <td>${escapeHTML(s.name)}</td>
                    <td>Semester ${s.semester}</td>
                    <td>${s.phone || "-"}</td>
                    <td>${s.cgpa.toFixed(2)}</td>
                    <td class="${attClass}">${s.attendance_percentage.toFixed(1)}%</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No student records registered in your department.</td></tr>`;
        }

        // Fetch announcements for Faculty
        loadAnnouncements();
    } catch (e) {
        showToast("Error", "Failed to retrieve faculty dashboard data.", "danger");
    }
}

let activeVerificationId = null;

function openApprovalModal(activityId, title) {
    activeVerificationId = activityId;
    document.getElementById("verify-modal-title").textContent = title;
    
    // Clear comment field
    document.getElementById("verify-comment").value = "";
    document.getElementById("verify-reject-reason-box").style.display = "none";
    
    const verifyModal = new bootstrap.Modal(document.getElementById("verifyActivityModal"));
    verifyModal.show();
}

// Handle dynamic status switch in verification modal
document.querySelectorAll('input[name="verify-status"]').forEach(radio => {
    radio.addEventListener("change", (e) => {
        const commentBox = document.getElementById("verify-reject-reason-box");
        if (e.target.value === "rejected") {
            commentBox.style.display = "block";
            document.getElementById("verify-comment").setAttribute("required", "required");
        } else {
            commentBox.style.display = "none";
            document.getElementById("verify-comment").removeAttribute("required");
        }
    });
});

async function submitActivityVerification() {
    if (!activeVerificationId || !currentToken) return;
    
    const statusVal = document.querySelector('input[name="verify-status"]:checked').value;
    const comment = document.getElementById("verify-comment").value;
    
    try {
        const response = await fetch(`${API_URL}/faculty/verify-activity/${activeVerificationId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                status: statusVal,
                rejection_comment: statusVal === "rejected" ? comment : null
            })
        });
        
        if (response.ok) {
            showToast("Success", `Activity successfully ${statusVal}.`, "success");
            const modalEl = document.getElementById("verifyActivityModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            // Reload views
            loadFacultyDashboard();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Verification post failed");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

// ----------------- Interactive Attendance Sheet -----------------
let facultyStudentCache = []; // Caches student records to log attendance

async function loadFacultyAttendanceSheet() {
    if (!currentToken) return;
    
    // Initialize date selector to today
    const dateInput = document.getElementById("att-mark-date");
    if (!dateInput.value) {
        dateInput.value = new Date().toISOString().substring(0, 10);
    }
    
    try {
        const response = await fetch(`${API_URL}/faculty/students`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        facultyStudentCache = await response.json();
        
        renderAttendanceSheet();
    } catch (e) {
        showToast("Error", "Failed to retrieve student roster.", "danger");
    }
}

function renderAttendanceSheet() {
    const listContainer = document.getElementById("faculty-attendance-list");
    listContainer.innerHTML = "";
    
    if (facultyStudentCache.length > 0) {
        facultyStudentCache.forEach(student => {
            // Set default present state
            student.marked_status = student.marked_status || "present";
            
            const div = document.createElement("div");
            div.className = "col-12 col-md-6 mb-3";
            div.innerHTML = `
                <div class="attendance-grid-item">
                    <div class="student-info">
                        <h6 class="mb-0 text-white">${escapeHTML(student.name)}</h6>
                        <span class="text-muted small">${student.roll_number} | Sem ${student.semester}</span>
                    </div>
                    <div class="attendance-options" data-student-id="${student.id}">
                        <button type="button" class="attendance-btn p ${student.marked_status === "present" ? "active" : ""}" onclick="setStudentAttendanceStatus(${student.id}, 'present')">P</button>
                        <button type="button" class="attendance-btn a ${student.marked_status === "absent" ? "active" : ""}" onclick="setStudentAttendanceStatus(${student.id}, 'absent')">A</button>
                        <button type="button" class="attendance-btn l ${student.marked_status === "late" ? "active" : ""}" onclick="setStudentAttendanceStatus(${student.id}, 'late')">L</button>
                    </div>
                </div>
            `;
            listContainer.appendChild(div);
        });
    } else {
        listContainer.innerHTML = `<div class="col-12 text-center text-muted py-4">No student records in this department.</div>`;
    }
}

function setStudentAttendanceStatus(studentId, status) {
    const student = facultyStudentCache.find(s => s.id === studentId);
    if (student) {
        student.marked_status = status;
        
        // Redraw active button styles directly
        const container = document.querySelector(`.attendance-options[data-student-id="${studentId}"]`);
        if (container) {
            container.querySelectorAll(".attendance-btn").forEach(btn => btn.classList.remove("active"));
            
            const activeClass = status === "present" ? "p" : status === "absent" ? "a" : "l";
            const btn = container.querySelector(`.attendance-btn.${activeClass}`);
            if (btn) btn.classList.add("active");
        }
    }
}

async function saveAttendanceSheet() {
    if (facultyStudentCache.length === 0 || !currentToken) return;
    
    const attDate = document.getElementById("att-mark-date").value;
    if (!attDate) {
        showToast("Validation Error", "Please select a valid date.", "warning");
        return;
    }
    
    const records = facultyStudentCache.map(student => ({
        student_id: student.id,
        status: student.marked_status || "present"
    }));
    
    try {
        const response = await fetch(`${API_URL}/faculty/attendance`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentToken}`
            },
            body: JSON.stringify({
                date: attDate,
                records: records
            })
        });
        
        if (response.ok) {
            showToast("Success", "Attendance logged and overall percentages updated.", "success");
            showView("faculty-dashboard");
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Failed to log attendance");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

// ----------------- Admin Module Functions -----------------
async function loadAdminDashboard() {
    if (!currentToken) return;
    
    try {
        // 1. Fetch KPI metrics stats
        const response = await fetch(`${API_URL}/admin/dashboard-stats`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const stats = await response.json();
        
        if (response.ok) {
            document.getElementById("stat-total-students").textContent = stats.total_students;
            document.getElementById("stat-total-faculty").textContent = stats.total_faculty;
            document.getElementById("stat-pending-verify").textContent = stats.pending_activities;
            document.getElementById("stat-avg-attendance").textContent = `${stats.average_attendance.toFixed(1)}%`;
            
            // Build Charts
            renderAnalyticsCharts(stats);
        }
    } catch (e) {
        showToast("Error", "Failed to retrieve admin dashboard stats.", "danger");
    }
}

function renderAnalyticsCharts(stats) {
    if (typeof Chart === "undefined") {
        console.warn("Chart.js is not loaded.");
        return;
    }
    
    // Destroy previous chart instances to avoid overlays
    if (charts.categoryChart) charts.categoryChart.destroy();
    if (charts.deptChart) charts.deptChart.destroy();
    
    // Chart 1: Category Breakdown (Doughnut)
    const ctxCat = document.getElementById("chart-categories").getContext("2d");
    const catLabels = stats.category_breakdown.map(c => c.category.toUpperCase());
    const catValues = stats.category_breakdown.map(c => c.count);
    
    charts.categoryChart = new Chart(ctxCat, {
        type: "doughnut",
        data: {
            labels: catLabels,
            datasets: [{
                data: catValues,
                backgroundColor: [
                    "#6366f1", // Indigo
                    "#06b6d4", // Cyan
                    "#10b981", // Emerald
                    "#f59e0b", // Amber
                    "#f43f5e"  // Rose
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#94a3b8", font: { family: "Inter", size: 11 } }
                }
            }
        }
    });

    // Chart 2: Department Student Count (Bar)
    const ctxDept = document.getElementById("chart-departments").getContext("2d");
    const deptLabels = stats.department_distribution.map(d => d.code);
    const deptValues = stats.department_distribution.map(d => d.student_count);
    
    charts.deptChart = new Chart(ctxDept, {
        type: "bar",
        data: {
            labels: deptLabels,
            datasets: [{
                label: "Students",
                data: deptValues,
                backgroundColor: "rgba(6, 182, 212, 0.4)",
                borderColor: "#06b6d4",
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: "#94a3b8", font: { family: "Inter" } }
                },
                y: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8", font: { family: "Inter" }, precision: 0 }
                }
            }
        }
    });
}

async function loadAdminUsers() {
    if (!currentToken) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/users`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const users = await response.json();
        
        const tbody = document.getElementById("admin-users-tbody");
        tbody.innerHTML = "";
        
        if (response.ok && users.length > 0) {
            users.forEach(u => {
                const tr = document.createElement("tr");
                
                let detailsMarkup = "-";
                if (u.role === "student") {
                    detailsMarkup = `<div><strong>${escapeHTML(u.details.name)}</strong> (${u.details.roll_number})</div>
                                     <div class="text-muted small">Dept: ${u.details.department || "N/A"} | Sem ${u.details.semester}</div>`;
                } else if (u.role === "faculty") {
                    detailsMarkup = `<div><strong>${escapeHTML(u.details.name)}</strong> (${u.details.faculty_id})</div>
                                     <div class="text-muted small">${escapeHTML(u.details.designation) || "Faculty"} | Dept: ${u.details.department || "N/A"}</div>`;
                } else {
                    detailsMarkup = `<div class="text-white">Admin Account</div>`;
                }
                
                // Allow deleting only other users (prevent self deletion)
                const isSelf = u.email === currentUser.email;
                const delBtn = isSelf 
                    ? `<span class="badge bg-secondary">Current User</span>`
                    : `<button class="btn btn-danger-custom btn-sm-custom py-1" onclick="deleteUser(${u.id}, '${escapeHTML(u.email)}')"><i class="bi bi-trash"></i> Delete</button>`;
                
                tr.innerHTML = `
                    <td>${u.id}</td>
                    <td>${escapeHTML(u.email)}</td>
                    <td><span class="badge bg-secondary text-uppercase">${u.role}</span></td>
                    <td>${detailsMarkup}</td>
                    <td>${formatDate(u.created_at)}</td>
                    <td>${delBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No accounts registered in the database.</td></tr>`;
        }
        
        // Populates creation modal dropdowns
        loadAdminModalDepartments();
    } catch (e) {
        showToast("Error", "Failed to retrieve user accounts directory.", "danger");
    }
}

async function handleAdminCreateUser(e) {
    e.preventDefault();
    const email = document.getElementById("admin-add-email").value;
    const password = document.getElementById("admin-add-password").value;
    const role = document.getElementById("admin-add-role").value;
    
    let url = `${API_URL}/auth/register/student`;
    let payload = { email, password };
    
    if (role === "student") {
        payload.name = document.getElementById("admin-reg-name").value;
        payload.roll_number = document.getElementById("admin-reg-roll").value;
        payload.department_id = parseInt(document.getElementById("admin-reg-dept").value);
        payload.semester = parseInt(document.getElementById("admin-reg-semester").value);
        payload.phone = document.getElementById("admin-reg-phone").value;
    } else if (role === "faculty") {
        url = `${API_URL}/auth/register/faculty`;
        payload.name = document.getElementById("admin-reg-name").value;
        payload.faculty_id = document.getElementById("admin-reg-fac-id").value;
        payload.department_id = parseInt(document.getElementById("admin-reg-dept").value);
        payload.designation = document.getElementById("admin-reg-designation").value;
    } else {
        // Admin
        showToast("Validation Error", "Self administration creation is restricted from this dashboard panel.", "warning");
        return;
    }
    
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentToken}`
            },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            showToast("Success", "User account successfully registered.", "success");
            document.getElementById("add-user-form").reset();
            
            // Hide modal
            const modalEl = document.getElementById("addUserModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            
            loadAdminUsers();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Account registration failed");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function deleteUser(userId, email) {
    if (!confirm(`Are you sure you want to permanently delete user account "${email}"? This action removes all profile data and records and cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        
        if (response.ok) {
            showToast("Success", "User account and related files successfully deleted.", "success");
            loadAdminUsers();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Deletion failed");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function loadAdminDepartments() {
    if (!currentToken) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/departments`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const depts = await response.json();
        
        const tbody = document.getElementById("admin-depts-tbody");
        tbody.innerHTML = "";
        
        if (response.ok && depts.length > 0) {
            depts.forEach(d => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${d.id}</strong></td>
                    <td>${escapeHTML(d.name)}</td>
                    <td><code>${d.code}</code></td>
                    <td>
                        <button class="btn btn-danger-custom btn-sm-custom py-1" onclick="deleteDepartment(${d.id}, '${escapeHTML(d.name)}')">
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No departments registered.</td></tr>`;
        }
    } catch (e) {
        showToast("Error", "Failed to retrieve department listings.", "danger");
    }
}

async function handleCreateDepartment(e) {
    e.preventDefault();
    const name = document.getElementById("dept-name").value;
    const code = document.getElementById("dept-code").value.toUpperCase();
    
    try {
        const response = await fetch(`${API_URL}/admin/departments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentToken}`
            },
            body: JSON.stringify({ name, code })
        });
        
        if (response.ok) {
            showToast("Success", "Department successfully created.", "success");
            document.getElementById("add-dept-form").reset();
            loadAdminDepartments();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Department creation failed");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function deleteDepartment(deptId, deptName) {
    if (!confirm(`Are you sure you want to delete department "${deptName}"? Connected faculty and student profiles will keep their profiles but their department links will clear.`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/departments/${deptId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        
        if (response.ok) {
            showToast("Success", "Department deleted.", "success");
            loadAdminDepartments();
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Failed to remove department");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

// ----------------- Report Generation & Excel/CSV Exports -----------------
async function exportCSVReport() {
    if (!currentToken) return;
    
    try {
        const response = await fetch(`${API_URL}/admin/reports/export`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const records = await response.json();
        
        if (!response.ok) {
            throw new Error("Failed to fetch reports dataset");
        }
        
        if (records.length === 0) {
            showToast("Export Notice", "No student records found to export.", "warning");
            return;
        }
        
        // Define CSV headers
        const headers = [
            "Roll Number", "Name", "Email", "Department", "Semester", 
            "Phone", "CGPA", "Attendance %", "Approved Activities Count"
        ];
        
        // Map records to CSV rows
        const csvRows = [
            headers.join(","), // Headers Row
            ...records.map(r => [
                `"${escapeCSV(r.roll_number)}"`,
                `"${escapeCSV(r.name)}"`,
                `"${escapeCSV(r.email)}"`,
                `"${escapeCSV(r.department)}"`,
                r.semester,
                `"${escapeCSV(r.phone)}"`,
                r.cgpa,
                r.attendance_percentage,
                r.approved_activities_count
            ].join(","))
        ];
        
        const csvContent = "data:text/csv;charset=utf-8," + csvRows.join("\n");
        const encodedUri = encodeURI(csvContent);
        
        // Create trigger link download
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `student_activity_report_${new Date().toISOString().substring(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast("Success", "Student records exported successfully as CSV.", "success");
    } catch (e) {
        showToast("Error", e.message, "danger");
    }
}

function escapeCSV(val) {
    if (val === null || val === undefined) return "";
    return val.toString().replace(/"/g, '""');
}

// ----------------- Database Seeding & Backups -----------------
async function triggerBackup() {
    if (!currentToken) return;
    
    const consoleText = document.getElementById("backup-console");
    consoleText.style.display = "block";
    consoleText.textContent = "Triggering database snapshot backup in progress...\n";
    
    try {
        const response = await fetch(`${API_URL}/admin/backup`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const data = await response.json();
        
        if (response.ok) {
            consoleText.textContent += `Backup complete!\n`;
            consoleText.textContent += `File: ${data.filename}\n`;
            consoleText.textContent += `Path: ${data.filepath}\n`;
            consoleText.textContent += `Timestamp: ${data.timestamp}\n`;
            showToast("Success", "System database backup complete.", "success");
        } else {
            throw new Error(data.detail || "Backup process failed");
        }
    } catch (e) {
        consoleText.textContent += `ERROR: ${e.message}\n`;
        showToast("Backup Failed", e.message, "danger");
    }
}

// ----------------- Dropdown Load Helpers -----------------
async function loadRegisterDepartments() {
    try {
        const response = await fetch(`${API_URL}/auth/departments`);
        const depts = await response.json();
        
        const select = document.getElementById("reg-dept");
        if (select) {
            select.innerHTML = '<option value="" disabled selected>Select Department</option>';
            depts.forEach(d => {
                select.innerHTML += `<option value="${d.id}">${d.name} (${d.code})</option>`;
            });
        }
    } catch (e) {
        console.error("Failed to load departments in dropdown:", e);
    }
}

async function loadAdminModalDepartments() {
    try {
        const response = await fetch(`${API_URL}/admin/departments`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const depts = await response.json();
        
        const select = document.getElementById("admin-reg-dept");
        if (select) {
            select.innerHTML = '<option value="" disabled selected>Select Department</option>';
            depts.forEach(d => {
                select.innerHTML += `<option value="${d.id}">${d.name} (${d.code})</option>`;
            });
        }
    } catch (e) {
        console.error("Failed to load departments in admin modal:", e);
    }
}

// ----------------- Global Helper Utilities -----------------
function viewCertificate(url) {
    if (!url) return;
    const fullUrl = `http://localhost:8000${url}`;
    
    const iframe = document.getElementById("iframe-cert-viewer");
    iframe.src = fullUrl;
    
    const viewerModal = new bootstrap.Modal(document.getElementById("certificateViewerModal"));
    viewerModal.show();
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
    } catch (e) {
        return dateStr;
    }
}

function escapeHTML(str) {
    if (!str) return "";
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

function showToast(title, message, type = "success") {
    // Check if toast container exists
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        container.className = "toast-container position-fixed bottom-0 end-0 p-3";
        container.style.zIndex = "1100";
        document.body.appendChild(container);
    }
    
    const toastId = `toast-${Date.now()}`;
    const bgClass = type === "success" ? "bg-success" : type === "danger" ? "bg-danger" : type === "warning" ? "bg-warning text-dark" : "bg-info";
    const textClass = type === "warning" ? "text-dark" : "text-white";
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} ${textClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="4000">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong>: ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML("beforeend", toastHTML);
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    
    // Clean up DOM after toast hides
    toastEl.addEventListener("hidden.bs.toast", () => {
        toastEl.remove();
    });
}
// ----------------- Announcements System Handlers -----------------

async function loadAnnouncements() {
    if (!currentToken) return;

    try {
        const response = await fetch(`${API_URL}/announcements`, {
            headers: { "Authorization": `Bearer ${currentToken}` }
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to retrieve bulletins");
        }

        const isStudent = currentUser.role === 'student';
        const cardId = isStudent ? 'student-announcements-card' : 'faculty-announcements-card';
        const listId = isStudent ? 'student-announcements-list' : 'faculty-announcements-list';

        const card = document.getElementById(cardId);
        const list = document.getElementById(listId);

        if (!list) return;
        list.innerHTML = "";

        if (data.length > 0) {
            card.style.display = "block";
            data.forEach(ann => {
                const col = document.createElement("div");
                col.className = "col-12 mb-2";

                const isDept = ann.department_code != null;
                const scopeBadge = isDept 
                    ? `<span class="badge-custom text-info py-0 px-2 small" style="background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.2);">${ann.department_code} Dept</span>`
                    : `<span class="badge-custom text-success py-0 px-2 small" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2);">Global Notice</span>`;

                const canDelete = currentUser.role === 'admin' || (currentUser.role === 'faculty' && ann.created_by === currentUser.name);
                const deleteBtn = canDelete
                    ? `<button class="btn btn-link text-danger p-0 border-0 ms-2 small" style="text-decoration:none; font-size:0.75rem;" onclick="deleteAnnouncementRecord(${ann.id})"><i class="bi bi-trash"></i> Delete</button>`
                    : "";

                col.innerHTML = `
                    <div class="announcement-item p-3 ${isDept ? 'dept-targeted' : ''}">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <h6 class="text-white mb-0" style="font-weight:600; font-size:0.95rem;">${escapeHTML(ann.title)}</h6>
                            <div class="d-flex align-items-center small text-secondary" style="font-size:0.8rem;">
                                <span>${formatDate(ann.created_at)}</span>
                                ${deleteBtn}
                            </div>
                        </div>
                        <p class="text-secondary small mb-2" style="line-height:1.4;">${escapeHTML(ann.content)}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="text-muted" style="font-size:0.78rem;">By <strong>${escapeHTML(ann.created_by)}</strong></span>
                            ${scopeBadge}
                        </div>
                    </div>
                `;
                list.appendChild(col);
            });
        } else {
            card.style.display = "none";
        }
    } catch (e) {
        console.error("Failed to load announcements:", e);
    }
}

async function handlePostAnnouncement(e) {
    e.preventDefault();
    const title = document.getElementById("ann-title").value;
    const content = document.getElementById("ann-content").value;
    const targetVal = document.getElementById("ann-dept-target").value;
    const department_id = targetVal === "global" ? null : parseInt(targetVal);

    try {
        const response = await fetch(`${API_URL}/announcements`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${currentToken}`
            },
            body: JSON.stringify({ title, content, department_id })
        });

        if (response.ok) {
            showToast("Success", "Announcement broadcasted successfully.", "success");
            document.getElementById("post-announcement-form").reset();
            
            // Close modal
            const modalEl = document.getElementById("postAnnouncementModal");
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            // Refresh current dashboards
            if (currentUser.role === "admin") {
                loadAdminDashboard();
            } else if (currentUser.role === "faculty") {
                loadFacultyDashboard();
            }
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Broadcast announcement failed");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function deleteAnnouncementRecord(id) {
    if (!confirm("Are you sure you want to delete this announcement bulletin?")) return;

    try {
        const response = await fetch(`${API_URL}/announcements/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${currentToken}` }
        });

        if (response.ok) {
            showToast("Success", "Announcement deleted.", "success");
            // Refresh
            if (currentUser.role === "student") {
                loadStudentDashboard();
            } else if (currentUser.role === "faculty") {
                loadFacultyDashboard();
            } else {
                loadAdminDashboard();
            }
        } else {
            const err = await response.json();
            throw new Error(err.detail || "Failed to remove notice");
        }
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

async function setupAnnouncementsModal() {
    const select = document.getElementById("ann-dept-target");
    if (!select) return;

    // Reset fields
    document.getElementById("ann-title").value = "";
    document.getElementById("ann-content").value = "";

    if (currentUser.role === "faculty") {
        // Locked to faculty's department
        select.innerHTML = `<option value="${currentUser.department_id || ''}" selected>${currentUser.department_name || 'My Department'}</option>`;
        select.disabled = true;
    } else if (currentUser.role === "admin") {
        select.disabled = false;
        try {
            const res = await fetch(`${API_URL}/admin/departments`, {
                headers: { "Authorization": `Bearer ${currentToken}` }
            });
            const depts = await res.json();
            select.innerHTML = '<option value="global" selected>Global (All Departments)</option>';
            depts.forEach(d => {
                select.innerHTML += `<option value="${d.id}">${d.name} (${d.code})</option>`;
            });
        } catch (e) {
            console.error("Failed to populate target departments:", e);
        }
    }
}

// ----------------- Visual Heatmap Calendar Renderer -----------------

function renderAttendanceHeatmap(logs) {
    const container = document.getElementById("attendance-heatmap");
    if (!container) return;
    container.innerHTML = "";

    // Map logs for fast matching
    const attendanceMap = {};
    logs.forEach(log => {
        attendanceMap[log.date] = log.status;
    });

    const today = new Date();
    const cells = [];
    
    // We want a grid of 53 columns (weeks) by 7 rows (days) representing 364 days ago to today.
    // Start date is 364 days ago
    const startDate = new Date();
    startDate.setDate(today.getDate() - 364);

    // Adjust start date to the previous Sunday so columns align correctly
    const startDayOfWeek = startDate.getDay();
    startDate.setDate(startDate.getDate() - startDayOfWeek);

    const totalDays = 371; // 53 weeks * 7 days
    
    for (let i = 0; i < totalDays; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);

        if (currentDate > today) {
            // Future cells are displayed as empty
            const cell = document.createElement("div");
            cell.className = "heatmap-cell level-none";
            cell.style.opacity = "0.2";
            cells.push(cell);
            continue;
        }

        const dateStr = currentDate.toISOString().substring(0, 10);
        const status = attendanceMap[dateStr];
        
        const cell = document.createElement("div");
        cell.className = "heatmap-cell";
        
        let statusText = "No Record";
        if (status) {
            cell.classList.add(`level-${status}`);
            statusText = status.toUpperCase();
        } else {
            cell.classList.add("level-none");
        }
        
        const formattedDate = currentDate.toLocaleDateString("en-US", { year: 'numeric', month: 'short', day: 'numeric' });
        cell.title = `Date: ${formattedDate} | Status: ${statusText}`;
        cells.push(cell);
    }

    // Insert all cells in order. The CSS grid-auto-flow: column aligns columns vertically
    cells.forEach(c => container.appendChild(c));
}
