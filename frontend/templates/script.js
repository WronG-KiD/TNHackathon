const API_BASE_URL = "http://127.0.0.1:5000/api/";

async function loadData(type) {
    document.getElementById("data-table").innerHTML = `<tr><td colspan="4" class="loading">Loading ${type.replace('_', ' ')} data...</td></tr>`;

    const response = await fetch(API_BASE_URL + type);
    const data = await response.json();

    if (data.length === 0) {
        document.getElementById("data-table").innerHTML = `<tr><td colspan="4">No data available</td></tr>`;
        return;
    }

    const tableContent = data.map(entry => `
        <tr>
            
            <td>${entry.url || "N/A"}</td>
            <td>${entry.category || "N/A"}</td>
            <td>${entry.description || "N/A"}</td>
            <td>${entry.content ? entry.content.substring(0, 100) + "..." : "No content"}</td>
            <td>${entry.mitigation_steps || "N/A"}</td>
        </tr>
    `).join("");

    document.getElementById("data-table").innerHTML = tableContent;

    document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
    document.querySelector(`button[onclick="loadData('${type}')"]`).classList.add("active");
}

