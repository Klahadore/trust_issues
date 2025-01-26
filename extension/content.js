const config_url = "http://0.0.0.0:8000/";
const keywords = ["sign up", "continue", "register", "get started", "join now", "join"];

// Function to check for warnings from the API
async function checkWarning(domain) {
  try {
    if (!domain.includes(".")) {
      return;
    }
    const response = await fetch(`${config_url}get_warning/${domain}`);
    const result = await response.json();
    console.log("API response:", result, domain);
    return result.message;
  } catch (error) {
    console.error("Failed to check warning:", error);
  }
}

// Function to wait for a specific button press
function waitForSpecificButtonPress() {
  return new Promise((resolve) => {
    const buttons = document.querySelectorAll("button, input[type='button'], input[type='submit'], a");

    buttons.forEach((button) => {
      const text = (button.innerText || button.value || "").toLowerCase();

      // Check if the button matches the keywords
      const matchesKeyword = keywords.some((keyword) =>
        text.includes(keyword.toLowerCase())
      );

      if (matchesKeyword) {
        button.addEventListener("click", (event) => {
          event.preventDefault(); // Stop the original button behavior
          console.log(`Button clicked: "${text.trim()}"`);
          resolve(button); // Resolve the Promise with the clicked button
        });
      }
    });
  });
}

// Main function
(async function () {
  console.log("Waiting for button press...");
  const originalButton = await waitForSpecificButtonPress();

  // Check if the modal already exists
  if (!document.getElementById("extension-popup-modal")) {
    console.log("Creating modal...");

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
      console.log("Modal closed.");
    };

    // Add event listeners to the buttons
    document.querySelector(".popup-button.leave").addEventListener("click", closePopup);
    const continueButton = document.querySelector(".popup-button.continue");
    continueButton.addEventListener("click", () => {
      modal.remove();
      overlay.remove();
      console.log("Executing original button's behavior...");

      // Simulate the original button's behavior
      if (originalButton.tagName === "A" && originalButton.href) {
        window.open(originalButton.href, originalButton.target || "_self");
      } else {
        originalButton.click();
      }
    });

    console.log("Modal displayed, behavior reassigned to 'Continue with Sign Up'.");
  }
})();
