(() => {
  const configUrl = "http://0.0.0.0:8000/";
  const keywords = [
    "sign up",
    "continue",
    "register",
    "get started",
    "join now",
    "join",
  ];

  const script = document.createElement("script");
  script.src = chrome.runtime.getURL("marked.min.js");

  script.onload = async () => {
    // Remove sanitize: true because Marked v2+ does not support it directly
    marked.use({
      breaks: true,
      silent: true,
    });

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
      const cssLink = document.createElement("link");
      cssLink.rel = "stylesheet";
      cssLink.type = "text/css";
      cssLink.href = chrome.runtime.getURL("content.css");
      document.head.appendChild(cssLink);

      const currentUrl = window.location.href;
      const nameUrl = getMainDomain(currentUrl);
      const rootDomain = getRootDomain(currentUrl);

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

      try {
        const [warningData, reviewData] = await Promise.all([
          checkWarning(rootDomain),
          new Promise((resolve) => {
            chrome.runtime.sendMessage(
              {
                action: "analyzeReviews",
                domain: rootDomain,
              },
              (response) => {
                if (response.error) {
                  console.error("Review API Error:", response.error);
                  resolve(null);
                } else {
                  resolve(response.data);
                }
              },
            );
          }),
        ]);

        const contentDiv = modal.querySelector(".popup-content");
        contentDiv.classList.remove("loading");

        const contentWrapper = document.createElement("div");
        contentWrapper.className = "content-wrapper";

        // Warnings Section
        if (warningData) {
          const warningSection = document.createElement("div");
          warningSection.className = "warning-section";

          const warningMarkdown = `
**Message:** ${warningData.message || "No warnings found"}

<details>
<summary><strong>Extended Info:</strong></summary>
\n${warningData.extended_message || "Additional information not available"}
</details>
          `;
          warningSection.innerHTML = marked.parse(warningMarkdown);
          contentWrapper.appendChild(warningSection);
        }

        // Reviews Section
        if (reviewData && reviewData.length > 0) {
          const reviewSection = document.createElement("div");
          reviewSection.className = "review-section";
          reviewSection.innerHTML = `<h3>User Reviews Analysis</h3>`;

          reviewData.forEach((review, index) => {
            const reviewElement = document.createElement("div");
            reviewElement.className = "review-item";

            const reviewMarkdown = `
**Summary:** ${review.reviews_message || "No summary available"}

<details>
<summary><strong>Full Review Analysis:</strong></summary>
\n${review.reviews_extended_message || "Detailed analysis not available"}
</details>
            `;
            reviewElement.innerHTML = marked.parse(reviewMarkdown);
            reviewSection.appendChild(reviewElement);
          });

          contentWrapper.appendChild(reviewSection);
        } else if (reviewData !== null) {
          const noReviews = document.createElement("p");
          noReviews.textContent = "No review analysis available";
          contentWrapper.appendChild(noReviews);
        }

        if (!warningData) {
          contentWrapper.innerHTML = `<p class="error">⚠️ Failed to load security information</p>`;
        }

        contentDiv.innerHTML = "";
        contentDiv.appendChild(contentWrapper);

        modal.querySelector(".popup-button.continue").disabled = false;
      } catch (err) {
        console.error("Modal data error:", err);
        modal.querySelector(".popup-content").innerHTML = `
          <p class="error">⚠️ Error loading security data. Proceed with caution.</p>
        `;
      }

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
          if (originalButton.tagName === "A" && originalButton.href) {
            window.open(originalButton.href, originalButton.target || "_self");
          } else {
            originalButton.click();
          }
        });
    }

    async function init() {
      console.log("Waiting for button press...");
      const originalButton = await waitForSpecificButtonPress();
      if (!document.getElementById("extension-popup-modal")) {
        console.log("Creating modal...");
        await createModal(originalButton);
      }
    }

    // Start
    init();
  };

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
