const outputElement = document.getElementById("output");

// Utility function to send requests
async function sendRequest(url, method = "GET", body = null) {
    try {
        const options = { method, headers: { "Content-Type": "application/json" } };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(url, options);
        if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const result = await response.json();
            outputElement.textContent = JSON.stringify(result, null, 2);
        } else if (contentType && contentType.includes("text/html")) {
            const result = await response.text();
            outputElement.innerHTML = result; // HTML을 직접 삽입
        } else {
            throw new Error("Unsupported response type");
        }
    } catch (error) {
        outputElement.textContent = `Error: ${error.message}`;
    }
}

// Event handlers for each section
document.body.addEventListener("click", (event) => {
    const action = event.target.dataset.action;
    console.log("Action:", action); // Add this line to debug
    if (!action) return;

    let url = "";
    let body = null;
    
    switch (action) {     
        ////////////////////////////  home.html  ////////////////////////////
        case "log-trace":
        case "log-debug":
        case "log-info":
        case "log-success":
        case "log-warning":
        case "log-error":
        case "log-critical":
            body = { log_level: action.replace("log-", "").toUpperCase() };
            url = "/log_level";
            break;
        case "apply-betting-params":
            const slave1Multiple = parseInt(document.getElementById("betting-slave1-multiple").value);
            const slave2Multiple = parseInt(document.getElementById("betting-slave2-multiple").value);
            body = {
                betting_params: {
                    slave1_multiple: slave1Multiple,
                    slave2_multiple: slave2Multiple
                }
            };
            url = "/set_betting_params";
            break;
        case "view-params":
            body = { password: document.getElementById("password").value.trim() };
            url = "/view_params";
            break;
        case "view-status":
            body = { password: document.getElementById("password").value.trim() };
            url = "/view_status";
            break;

        ////////////////////////////  admin.html  ////////////////////////////
        case "on-whitelist":
            url = "/use_whitelist/1";
            break;
        case "off-whitelist":
            url = "/use_whitelist/0";
            break;
        case "pause-operation":
            body = { password: document.getElementById("password").value.trim() };
            url = "/pause"
            break;
        case "resume-operation":
            body = { password: document.getElementById("password").value.trim() };
            url = "/resume"
            break;

        ////////////////////////////  default  ////////////////////////////
        default:
            alert("Unknown action!");
            return;
    }

    // Add password to the body
    if (body) {
        const password = document.getElementById("password").value.trim();
        body.password = password;
    } 

    sendRequest(url, body ? "POST" : "GET", body);
});