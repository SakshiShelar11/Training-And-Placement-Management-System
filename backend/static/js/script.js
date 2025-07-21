// function fetchJobs() {
//     fetch("/jobs")
//     .then(response => response.json())
//     .then(data => {
//         let jobList = document.getElementById("job-list");
//         jobList.innerHTML = "";
//         data.forEach(job => {
//             let li = document.createElement("li");
//             li.textContent = `${job.title} at ${job.company}`;
//             jobList.appendChild(li);
//         });
//     });
// }

function fetchJobs() {
    fetch("/jobs", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("token") // Ensure token is included
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data); // Debugging
        let jobList = document.getElementById("job-list");
        jobList.innerHTML = "";
        data.forEach(job => {
            let li = document.createElement("li");
            li.textContent = `${job.title} at ${job.company}`;
            jobList.appendChild(li);
        });
    })
    .catch(error => console.error("Error fetching jobs:", error));
}


function applyForJob(jobId) {
    const token = localStorage.getItem("token");
    if (!token) {
        console.error("No token found. User must be logged in.");
        return;
    }

    const data = { job_id: jobId };

    fetch("/apply", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}` // Include the token in the header
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        alert(data.message);
    })
    .catch(error => {
        console.error("Error applying for job:", error);
    });
}


