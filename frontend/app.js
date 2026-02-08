const API = "http://127.0.0.1:8000";

/* ======================
   TOKEN HELPERS
====================== */

function saveToken(token) {
  localStorage.setItem("token", token);
}

function getToken() {
  return localStorage.getItem("token");
}

function logout() {
  localStorage.removeItem("token");
  location = "index.html";
}

/* ======================
   AUTH
====================== */

function login() {
  fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username.value,
      password: password.value
    })
  })
    .then(r => r.json())
    .then(d => {
      if (!d.access_token) {
        alert("Login failed");
        return;
      }

      saveToken(d.access_token);

      // decode JWT payload
      const payload = JSON.parse(
        atob(d.access_token.split(".")[1])
      );

      if (payload.role === "admin") {
        location = "admin.html";
      } else {
        location = "user.html";
      }
    });
}

function register() {
  fetch(`${API}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: regUsername.value,
      password: regPassword.value
    })
  })
    .then(r => r.json())
    .then(() => {
      alert("Account created. Please login.");
      showLogin();
    });
}

/* ======================
   LOGIN / REGISTER UI
====================== */

function showLogin() {
  document.getElementById("loginForm").style.display = "block";
  document.getElementById("registerForm").style.display = "none";
  document.querySelectorAll(".tab")[0].classList.add("active");
  document.querySelectorAll(".tab")[1].classList.remove("active");
}

function showRegister() {
  document.getElementById("loginForm").style.display = "none";
  document.getElementById("registerForm").style.display = "block";
  document.querySelectorAll(".tab")[1].classList.add("active");
  document.querySelectorAll(".tab")[0].classList.remove("active");
}

/* ======================
   USER
====================== */

function createJob() {
  fetch(`${API}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + getToken()
    },
    body: JSON.stringify({
      command: document.getElementById("command").value
    })
  })
    .then(r => r.json())
    .then(() => loadUserJobs());
}

function loadUserJobs() {
  fetch(`${API}/jobs`, {
    headers: {
      "Authorization": "Bearer " + getToken()
    }
  })
    .then(r => r.json())
    .then(data => {
      const div = document.getElementById("jobs");
      div.innerHTML = "";

      data.forEach(j => {
        div.innerHTML += `
          <div class="job">
            <b>#${j.id}</b> | ${j.command}<br>
            Status: <b>${j.status}</b>
          </div>
        `;
      });
    });
}

/* ======================
   ADMIN
====================== */
async function loadAllJobs() {
  try {
    const res = await fetch(`${API}/jobs`, {
      headers: { "Authorization": "Bearer " + getToken() }
    });

    const data = await safeJson(res);
    if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);

    const div = document.getElementById("jobs");
    div.innerHTML = "";

    data.forEach(j => {
      const canApprove = j.status === "PENDING";
      const canRun = j.status === "APPROVED";

      div.innerHTML += `
        <div class="job">
          <b>#${j.id}</b> | ${j.command}<br>
          Status: <b>${j.status}</b><br>

      ${canApprove ? `<button onclick="approveJob(${j.id})">Approve</button>` : ""}
      ${canRun ? `<button onclick="runJob(${j.id})">Run</button>` : ""}

        </div>
      `;
    });
  } catch (e) {
    showMsg(e.message);
  }
}

async function approveJob(id) {
  try {
    const res = await fetch(`${API}/admin/jobs/${id}/approve`, {
      method: "POST",
      headers: { "Authorization": "Bearer " + getToken() }
    });

    const data = await safeJson(res);
    if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);

    await loadAllJobs();
  } catch (e) {
    showMsg(e.message);
  }
}

async function runJob(id) {
  try {
    const res = await fetch(`${API}/admin/jobs/${id}/run`, {
      method: "POST",
      headers: { "Authorization": "Bearer " + getToken() }
    });

    const data = await safeJson(res);
    if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);

    await loadAllJobs();
  } catch (e) {
    showMsg(e.message);
  }
}


// Backward-compatible alias (older pages may call submitJob)
function submitJob(){
  return createJob();
}
function showMsg(text) {
  alert(text);
}

async function safeJson(res) {
  try { return await res.json(); } catch { return null; }
}
