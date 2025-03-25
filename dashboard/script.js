document.querySelector('.dropdown-arrow').addEventListener('click', function(event) {
    let dropdown = this.parentElement.querySelector('.dropdown-menu');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
});


// 🔹 Fetch API Logs (Initial Load)
async function fetchAPILogs() {
    let response = await fetch("http://127.0.0.1:8000/api-logs");
    let logs = await response.json();
    updateLogsUI(logs);
}

// 🔹 Fetch Projects
async function fetchProjects() {
    let response = await fetch("http://127.0.0.1:8000/projects");
    let projects = await response.json();
    updateProjectsUI(projects);
}

// 🔹 Fetch GitHub Activity
async function fetchGitHubActivity() {
    let response = await fetch("http://127.0.0.1:8000/github-activity");
    let activity = await response.json();
    console.log("GitHub Activity:", activity);
}

// 🔹 Update UI for Logs
function updateLogsUI(logs) {
    let logList = document.getElementById("api-logs-list");
    logList.innerHTML = "";
    logs.forEach(log => {
        let li = document.createElement("li");
        li.textContent = `${log.timestamp}: ${log.endpoint} - ${log.status}`;
        logList.appendChild(li);
    });
}

// 🔹 Update UI for Projects
function updateProjectsUI(projects) {
    let projectList = document.getElementById("projects-list");
    projectList.innerHTML = "";
    projects.forEach(project => {
        let li = document.createElement("li");
        li.textContent = `${project.name} - ${project.description}`;
        projectList.appendChild(li);
    });
}

// 🔹 WebSocket Connection for Real-Time API Logs
let socket = new WebSocket("ws://127.0.0.1:8000/ws/logs");

socket.onmessage = function(event) {
    let logs = JSON.parse(event.data);
    updateLogsUI(logs);
};

// Call functions
fetchAPILogs();
fetchProjects();
fetchGitHubActivity();