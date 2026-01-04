const API = "http://127.0.0.1:8000";

function saveToken(token) {
  localStorage.setItem("token", token);
}

function getToken() {
  return localStorage.getItem("token");
}

// ---------- AUTH ----------
function register() {
  fetch(`${API}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username.value,
      password: password.value
    })
  })
  .then(r => r.json())
  .then(d => alert("Registered successfully"));
}

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
    location = "dashboard.html";
  });
}

// ---------- USER ----------
function submitJob() {
  fetch(`${API}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + getToken()
    },
    body: JSON.stringify({
      gpu_type: "A100",
      gpu_count: 1,
      estimated_hours: 2,
      command: command.value,
      is_sensitive: false
    })
  })
  .then(r => r.json())
  .then(d => alert("Job submitted"));
}

// ---------- ADMIN ----------
function loadJobs() {
  fetch(`${API}/jobs`, {
    headers: {
      "Authorization": "Bearer " + getToken()
    }
  })
  .then(r => r.json())
  .then(jobs => {
    jobsDiv.innerHTML = "";
    jobs.forEach(j => {
      jobsDiv.innerHTML += `
        <div class="job">
          <b>Job ${j.id}</b> - ${j.status}
        </div>
      `;
    });
  });
}
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
    alert("Account created, please login");
    showLogin();
  });
}