const API_URL = "http://127.0.0.1:5000/api/merged_data";

async function loadData() {
    document.getElementById("data-table").innerHTML = `<tr><td colspan="8" class="loading">Loading data...</td></tr>`;

    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        if (data.length === 0) {
            document.getElementById("data-table").innerHTML = `<tr><td colspan="8">No data available</td></tr>`;
            return;
        }

        const tableContent = data.map(entry => `
            <tr>
                <td>${entry.sno}</td>
                <td>${entry.id}</td>
                <td>${entry.url}</td>
                <td>${entry.access}</td>
                <td>${entry.safe_or_not}</td>
                <td>${entry.malicious_activity}</td>
                <td>${entry.content}</td>
                <td>${entry.mitigation_solution}</td>
            </tr>
        `).join("");

        document.getElementById("data-table").innerHTML = tableContent;
    } catch (error) {
        document.getElementById("data-table").innerHTML = `<tr><td colspan="8">Error loading data</td></tr>`;
        console.error("Error fetching data:", error);
    }
}

function downloadCSV() {
    let table = document.querySelector("table");
    let rows = Array.from(table.querySelectorAll("tr"));
    let csv = rows.map(row => {
        return Array.from(row.querySelectorAll("td, th")).map(cell => `"${cell.innerText}"`).join(",");
    }).join("\n");

    let blob = new Blob([csv], { type: "text/csv" });
    let a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "dark_web_data.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function navigate(page) {
    let title = document.getElementById("page-title");
    switch (page) {
        case "home":
            title.innerText = "Dark Web Monitoring";
            break;
        case "scraped_data":
            title.innerText = "search url";
            break;
        case "dash":
            title.innerText = "Dark Web Monitoring Dashboard";
            break;
        case "vault":
            title.innerText = "Dark Web Monitoring Data";
            break;
    }
}
