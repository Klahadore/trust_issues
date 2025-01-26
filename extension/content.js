(() => {
  // ---------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------
  const configUrl = "http://0.0.0.0:8000/";
  const keywords = ["sign up", "continue", "register", "get started", "join now", "join"];

  // ---------------------------------------------------------
  // Fetching warning from API
  // ---------------------------------------------------------
  async function checkWarning(domain) {
    try {
      if (!domain.includes(".")) {
        return;
      }
      const response = await fetch(`${configUrl}get_warning/${domain}`);
      const result = await response.json();
      console.log("API response:", result, domain);
      return result.message;
    } catch (error) {
      console.error("Failed to check warning:", error);
    }
  }

  // ---------------------------------------------------------
  // Wait for specific button press
  // ---------------------------------------------------------
  function waitForSpecificButtonPress() {
    return new Promise((resolve) => {
      // Select all relevant clickable elements
      const buttons = document.querySelectorAll(
        "button, input[type='button'], input[type='submit'], a"
      );

      // Attach click handlers to any button matching our keywords
      buttons.forEach((button) => {
        const text = (button.innerText || button.value || "").toLowerCase();
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

  // ---------------------------------------------------------
  // Create modal elements and behavior
  // ---------------------------------------------------------
  function createModal(originalButton) {
    // Load CSS
    const cssLink = document.createElement("link");
    cssLink.rel = "stylesheet";
    cssLink.type = "text/css";
    cssLink.href = chrome.runtime.getURL("content.css");
    document.head.appendChild(cssLink);

    // Create overlay
    const overlay = document.createElement("div");
    overlay.id = "background-overlay";
    overlay.className = "background-overlay";
    document.body.appendChild(overlay);

    // Create modal container
    const modal = document.createElement("div");
    modal.id = "extension-popup-modal";
    modal.className = "popup-modal";

    // Populate modal HTML
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

    // Append modal to the document
    document.body.appendChild(modal);

    // Cleanup function to remove modal & overlay
    const closePopup = () => {
      modal.remove();
      overlay.remove();
      console.log("Modal closed.");
    };

    // "Leave" button closes the popup
    document.querySelector(".popup-button.leave").addEventListener("click", closePopup);

    // "Continue" button closes popup and simulates original behavior
    const continueButton = document.querySelector(".popup-button.continue");
    continueButton.addEventListener("click", () => {
      closePopup();
      console.log("Executing original button's behavior...");

      if (originalButton.tagName === "A" && originalButton.href) {
        // Simulate clicking a link
        window.open(originalButton.href, originalButton.target || "_self");
      } else {
        // Simulate clicking a standard button or submit
        originalButton.click();
      }
    });

    console.log("Modal displayed. Behavior reassigned to 'Continue with Sign Up'.");
  }

  // ---------------------------------------------------------
  // Main logic
  // ---------------------------------------------------------
  async function init() {
    console.log("Waiting for button press...");
    const originalButton = await waitForSpecificButtonPress();

    // Only create the modal if it doesn't already exist
    if (!document.getElementById("extension-popup-modal")) {
      console.log("Creating modal...");
      createModal(originalButton);
    }
  }

  // Start
  init();
})();
