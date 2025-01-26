(() => {
  // ---------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------
  const configUrl = "http://localhost:8000/"; 
  // ^ Use localhost, or your machine's IP if 0.0.0.0 doesn't work in the browser

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
      // Check for HTTP errors
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      console.log("API response:", result, domain);
      return result;
    } catch (error) {
      console.error("Failed to check warning:", error);
    }
  }

  function getRootDomain(url) {
    try {
      const urlObj = new URL(url);
      const parts = urlObj.hostname.split(".").filter((p) => p !== "");
      return parts.slice(-2).join("."); // Get last two parts
    } catch {
      return null;
    }
  }

  function getMainDomain(url) {
    try {
      const urlObj = new URL(url); 
      const parts = urlObj.hostname.split(".").filter((p) => p !== "");
      const mainDomain = parts.length > 1 ? parts[parts.length - 2] : parts[0]; 
      return mainDomain.charAt(0).toUpperCase() + mainDomain.slice(1); 
    } catch {
      return null;
    }
  }

  // ---------------------------------------------------------
  // Wait for specific button press
  // ---------------------------------------------------------
  function waitForSpecificButtonPress() {
    return new Promise((resolve) => {
      const buttons = document.querySelectorAll(
        "button, input[type='button'], input[type='submit'], a"
      );
      buttons.forEach((button) => {
        const text = (button.innerText || button.value || "").toLowerCase();
        const matchesKeyword = keywords.some((keyword) =>
          text.includes(keyword.toLowerCase())
        );
        if (matchesKeyword) {
          button.addEventListener("click", (event) => {
            event.preventDefault();
            console.log(`Button clicked: "${text.trim()}"`);
            resolve(button);
          });
        }
      });
    });
  }

  // ---------------------------------------------------------
  // Create modal elements and behavior
  // ---------------------------------------------------------
  async function createModal(originalButton) {
    // Load CSS
    const cssLink = document.createElement("link");
    cssLink.rel = "stylesheet";
    cssLink.type = "text/css";
    cssLink.href = chrome.runtime.getURL("content.css");
    document.head.appendChild(cssLink);

    // Name
    const currentUrl = window.location.href;
    console.log("Current URL:", currentUrl);
    const nameUrl = getMainDomain(currentUrl);

    // Get Root Domain, then fetch warnings
    const rootDomain = getRootDomain(currentUrl);
    console.log("Root Domain:", rootDomain);

    let data;
    try {
      data = await checkWarning(rootDomain);
      console.log("Fetched data:", data);
    } catch (err) {
      console.error("Error retrieving data:", err);
    }

    // You can now safely access data, if it exists
    const message = data?.message || "No warning message available.";
    const extendedMessage = data?.extended_message || "";

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
      <h2 class="popup-title">TRUST ISSUES: ${nameUrl} Analysis</h2>
      <div class="popup-content">
        <p><strong>Message:</strong> ${message}</p>
        <p><strong>Extended Info:</strong> ${extendedMessage}</p>
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

    if (!document.getElementById("extension-popup-modal")) {
      console.log("Creating modal...");
      await createModal(originalButton); // await here as well
    }
  }

  // Start
  init();
})();
