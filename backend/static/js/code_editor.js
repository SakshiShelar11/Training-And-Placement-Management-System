// Initialize CodeMirror
const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: "python",  // Default mode
    theme: "dracula", // Improved theme
    lineNumbers: true
});

// Language mode mapping for CodeMirror
const modeMap = {
    "python": "python",
    "javascript": "javascript",
    "c": "text/x-csrc",
    "cpp": "text/x-c++src",
    "java": "text/x-java",
    "php": "application/x-httpd-php" // Added PHP support
};

// Change CodeMirror mode based on language selection
document.getElementById("language").addEventListener("change", function() {
    const mode = modeMap[this.value] || "plaintext";
    editor.setOption("mode", mode);
});

function runCode() {
    const code = editor.getValue().trim();
    const language = document.getElementById("language").value;
    const outputElement = document.getElementById("output");

    if (!code) {
        outputElement.innerText = "⚠️ Error: Code cannot be empty!";
        return;
    }

    outputElement.innerText = "⏳ Running..."; // Show loading state

    fetch("http://127.0.0.1:5000/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Response from server:", data); // Debugging
        outputElement.innerText = data.output || `⚠️ Error: ${data.error}`;
    })
    .catch(error => {
        console.error("Error:", error);
        outputElement.innerText = "⚠️ Error: Failed to connect to the server.";
    });
}
