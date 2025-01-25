let currentTabId = null;
let currentRootDomain = null;
let config = "http://0.0.0.0:8000";
let myData = null;

function getRootDomain(urlStr) {
  try {
    const { hostname } = new URL(urlStr);
    const parts = hostname.split(".").filter(Boolean);

    // remove domain + TLD
    if (parts.length > 2) {
      return parts.slice(parts.length - 2).join(".");
    }
    return hostname;
  } catch (error) {
    return null;
  }
}

/**
 * Handle activation of a new tab.
 * 1. We get the newly activated tab's URL.
 * 2. Extract its root domain.
 * 3. If it's different from our global currentRootDomain, we update and log it.
 */
chrome.tabs.onActivated.addListener((activeInfo) => {
    currentTabId = activeInfo.tabId;
  
    chrome.tabs.get(activeInfo.tabId, (tab) => {
      if (tab?.url) {
        const newRootDomain = getRootDomain(tab.url);
  
        if (newRootDomain && newRootDomain !== currentRootDomain) {
          console.log(
            `Active tab changed: root domain from '${currentRootDomain}' to '${newRootDomain}'.`
          );
          currentRootDomain = newRootDomain;
  
          // Check if the domain exists in the database
          fetch(config + "/check_root_url/" + currentRootDomain)
            .then((res) => res.json())
            .then((data) => {
              console.log(data.exists);
              if (data.exists) {
                // Update myData if the domain exists
                myData = true;
              } else {
                // If it doesn't exist, call POST
                myData = false;
                return fetch(`${config}/websites`, {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({
                    website: currentRootDomain,
                  }),
                });
              }
            })
            .then((res) => {
              if (res) {
                if (!res.ok) {
                  return res.json().then((errData) => {
                    throw new Error(
                      `Server error ${res.status}: ${
                        errData.detail || JSON.stringify(errData)
                      }`
                    );
                  });
                }
                return res.json();
              }
            })
            .then((postResponse) => {
              if (postResponse) {
                console.log("POST /websites success:", postResponse);
              }
            })
            .catch((error) => {
              console.error("Error posting website:", error);
            });
        }
      }
    });
  });
  

/**
 * Handle updates in the currently active tab (e.g., user navigates to a new site).
 * Only respond if:
 *   1. The updated tab is the *active* tab, AND
 *   2. The root domain actually changed.
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // We only care if the updated tab is the current active tab
    if (tabId === currentTabId && changeInfo.url) {
      const newRootDomain = getRootDomain(changeInfo.url);
  
      if (newRootDomain && newRootDomain !== currentRootDomain) {
        console.log(
          `Active tab domain changed: '${currentRootDomain}' → '${newRootDomain}'.`
        );
        currentRootDomain = newRootDomain;
  
        // Check if the domain exists in the database
        fetch(config + "/check_root_url/" + currentRootDomain)
          .then((res) => res.json())
          .then((data) => {
            console.log(data.exists);
  
            if (data.exists) {
              // If the domain exists, update myData
              myData = true;
            } else {
              // If the domain doesn't exist, call POST
              myData = false;
              return fetch(`${config}/websites`, {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  website: currentRootDomain,
                }),
              });
            }
          })
          .then((res) => {
            if (res) {
              if (!res.ok) {
                return res.json().then((errData) => {
                  throw new Error(
                    `Server error ${res.status}: ${
                      errData.detail || JSON.stringify(errData)
                    }`
                  );
                });
              }
              return res.json();
            }
          })
          .then((postResponse) => {
            if (postResponse) {
              console.log("POST /websites success:", postResponse);
            }
          })
          .catch((error) => {
            console.error("Error in onUpdated logic:", error);
          });
      }
    }
  });
  
