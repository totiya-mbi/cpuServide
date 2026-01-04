const API = "http://127.0.0.1:8000";

// ---------- LOGIN ----------
function login() {
  fetch(`${API}/login?username=${username.value}&password=${password.value}`, {
    method: "POST"
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) {
      alert("Login failed");
      return;
    }

    localStorage.setItem("user_id", d.user_id);
    localStorage.setItem("role", d.role);

    if (d.role === "admin") {
      location = "admin.html";
    } else {
      location = "dashboard.html";
    }
  });
}

// ---------- USER ----------
function submitJob() {
  const uid = localStorage.getItem("user_id");

  fetch(`${API}/jobs?user_id=${uid}&command=${command.value}`, {
    method: "POST"
  })
  .then(r => r.json())
  .then(d => {
    output.innerText = JSON.stringify(d, null, 2);
  });
}

// ---------- ADMIN ----------
function loadJobs() {
  fetch(`${API}/jobs`)
    .then(r => r.json())
    .then(data => {
      jobs.innerHTML = "";
      data.forEach(j => {
        jobs.innerHTML += `
          <div>
            Job ${j.id} - ${j.status}
            <button onclick="approve(${j.id})">Approve</button>
            <button onclick="runJob(${j.id})">Run</button>
          </div>
        `;
      });
    });
}

function approve(id) {
  fetch(`${API}/admin/approve?job_id=${id}`, { method: "POST" })
    .then(loadJobs);
}

function runJob(id) {
  fetch(`${API}/admin/run?job_id=${id}`, { method: "POST" })
    .then(loadJobs);
}
