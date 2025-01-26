(() => {
  // ---------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------
  const configUrl = "http://0.0.0.0:8000/";
  // ^ Use localhost, or your machine's IP if 0.0.0.0 doesn't work in the browser

  const keywords = [
    "sign up",
    "continue",
    "register",
    "get started",
    "join now",
    "join",
  ];

  // ---------------------------------------------------------
  // Fetching warning from API
  // ---------------------------------------------------------
  async function checkWarning(domain) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage(
        {
          action: "fetchWarning",
          domain: domain,
        },
        (response) => {
          if (response.error) {
            console.error("API ERROR:", response.error);
            resolve(null);
          } else {
            resolve(response.data);
          }
        },
      );
    });
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
        "button, input[type='button'], input[type='submit'], a",
      );
      buttons.forEach((button) => {
        const text = (button.innerText || button.value || "").toLowerCase();
        const matchesKeyword = keywords.some((keyword) =>
          text.includes(keyword.toLowerCase()),
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

    const currentUrl = window.location.href;
    const nameUrl = getMainDomain(currentUrl);
    const rootDomain = getRootDomain(currentUrl);

    // Create initial modal structure with loading state
    const overlay = document.createElement("div");
    overlay.id = "background-overlay";
    overlay.className = "background-overlay";
    document.body.appendChild(overlay);

    const modal = document.createElement("div");
    modal.id = "extension-popup-modal";
    modal.className = "popup-modal";
    modal.innerHTML = `
      <h2 class="popup-title">TRUST ISSUES: ${nameUrl} Analysis</h2>
      <div class="popup-content loading">
        <div class="spinner"></div>
        <p>Checking for security warnings...</p>
      </div>
      <div class="popup-buttons">
        <button class="popup-button leave"><strong>Leave</strong></button>
        <button class="popup-button continue" disabled>
          <strong>Continue with Sign Up</strong>
        </button>
      </div>
    `;
    document.body.appendChild(modal);

    // Fetch data after modal is rendered
    try {
      const data = await checkWarning(rootDomain);
      const contentDiv = modal.querySelector(".popup-content");

      if (data) {
        contentDiv.classList.remove("loading");
        contentDiv.innerHTML = `
          <p><strong>Message:</strong> ${data.message || "No warnings found"}</p>
          <p><strong>Extended Info:</strong> ${data.extended_message || "Additional information not available"}</p>
        `;
      } else {
        contentDiv.innerHTML = `<p class="error">⚠️ Failed to load security information</p>`;
      }

      // Enable continue button after load
      modal.querySelector(".popup-button.continue").disabled = false;
    } catch (err) {
      console.error("Modal data error:", err);
      modal.querySelector(".popup-content").innerHTML = `
        <p class="error">⚠️ Error loading security data. Proceed with caution.</p>
      `;
    }

    // Event listeners for buttons
    const closePopup = () => {
      modal.remove();
      overlay.remove();
    };

    modal
      .querySelector(".popup-button.leave")
      .addEventListener("click", closePopup);
    modal
      .querySelector(".popup-button.continue")
      .addEventListener("click", () => {
        closePopup();
        originalButton.click();
      });
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
