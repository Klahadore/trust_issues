(() => {
  // ---------------------------------------------------------
  // Configuration
  // ---------------------------------------------------------
  const configUrl = "http://0.0.0.0:8000/";
  const keywords = [
    "sign up",
    "continue",
    "register",
    "get started",
    "join now",
    "join",
  ];

  // Load Marked.js first with proper error handling
  const script = document.createElement("script");
  script.src = chrome.runtime.getURL("marked.min.js");

  // Wrap all logic in script.onload
  script.onload = async () => {
    // Initialize marked with safe defaults
    marked.use({
      breaks: true,
      sanitize: true, // Critical for security
      silent: true,
    });

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
        return parts.slice(-2).join(".");
      } catch {
        return null;
      }
    }

    function getMainDomain(url) {
      try {
        const urlObj = new URL(url);
        const parts = urlObj.hostname.split(".").filter((p) => p !== "");
        const mainDomain =
          parts.length > 1 ? parts[parts.length - 2] : parts[0];
        return mainDomain.charAt(0).toUpperCase() + mainDomain.slice(1);
      } catch {
        return null;
      }
    }

    // ---------------------------------------------------------

    function waitForSpecificButtonPress() {
      return new Promise((resolve) => {
        const buttons = document.querySelectorAll(
          "button, input[type='button'], input[type='submit'], a",
        );
        buttons.forEach((button) => {
          const text = (button.innerText || button.value || "")
            .trim()
            .toLowerCase();
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
          const markdownContent = `
            **Message:** ${data.message || "No warnings found"}

            <details>
            <summary><strong>Extended Info:</strong></summary>
            ${data.extended_message || "Additional information not available"}
            </details>
          `;
          contentDiv.innerHTML = marked.parse(markdownContent);
        } else {
          contentDiv.innerHTML = marked.parse(
            `<p class="error">⚠️ Failed to load security information</p>`,
          );
        }

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
        await createModal(originalButton);
      }
    }

    // Start main logic after Marked.js is loaded
    init();
  };

  // Handle script loading errors
  script.onerror = () => {
    console.error("Failed to load Marked.js parser");
    document.body.innerHTML = `
      <div style="padding: 10px; color: red">
        ⚠️ Security extension failed to initialize - Please refresh the page
      </div>
    `;
  };

  document.head.appendChild(script);
})();
