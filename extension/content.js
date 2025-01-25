if (!document.getElementById("extension-popup-modal")) {
  // Add the CSS file to the document
  const cssLink = document.createElement("link");
  cssLink.rel = "stylesheet";
  cssLink.type = "text/css";
  cssLink.href = chrome.runtime.getURL("content.css");
  document.head.appendChild(cssLink);

  // Create the blurred overlay
  const overlay = document.createElement("div");
  overlay.id = "background-overlay";
  overlay.className = "background-overlay";
  document.body.appendChild(overlay);

  // Create the modal
  const modal = document.createElement("div");
  modal.id = "extension-popup-modal";
  modal.className = "popup-modal";

  // Add content to the modal
  modal.innerHTML = `
    <h2 class="popup-title">TRUST ISSUES</h2>
    <div class="popup-content">
      <strong>Spotify Privacy Policy and Terms of Service:</strong><br><br>
      <strong>Possible flags:</strong> collects and uses extensive personal data, 
      including your listening habits, device information, and location, which 
      may not be immediately clear to users. This data is used for personalized 
      advertising and other purposes, potentially beyond what users expect.
    </div>
    <div class="popup-buttons">
      <button class="popup-button leave"><strong>Leave</strong></button>
      <button class="popup-button continue"><strong>Continue with Sign Up</strong></button>
    </div>
  `;

  // Append the modal to the body
  document.body.appendChild(modal);

  // Function to remove the modal and overlay
  const closePopup = () => {
    modal.remove();
    overlay.remove();
  };

  // Add event listeners to the buttons
  document.querySelector(".popup-button.leave").addEventListener("click", closePopup);
  document.querySelector(".popup-button.continue").addEventListener("click", closePopup);
}
