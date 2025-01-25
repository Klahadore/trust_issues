// Inject the CSS file into the page
const cssLink = document.createElement("link");
cssLink.rel = "stylesheet";
cssLink.type = "text/css";
cssLink.href = chrome.runtime.getURL("content.css"); // Adjust the path if necessary
document.head.appendChild(cssLink);

// Check if a popup already exists
if (!document.getElementById("extension-popup-modal")) {
  const modal = document.createElement("div");
  modal.id = "extension-popup-modal";
  modal.className = "popup-modal";

  modal.innerHTML = `
    <h2 class="popup-title">TRUST ISSUES</h2>
    <button id="close-modal" class="popup-button">Close</button>
  `;

  document.body.appendChild(modal);

  document.getElementById("close-modal").addEventListener("click", () => {
    modal.remove();
  });
}
