let currentTabId = null;
let currentRootDomain = null;

function getRootDomain(urlStr) {
  try {
    const { hostname } = new URL(urlStr);
    const parts = hostname.split('.').filter(Boolean);

    // remove domain + TLD
    if (parts.length > 2) {
      return parts.slice(parts.length - 2).join('.');
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
  // Step 1: Update our currentTabId to the newly active tab
  currentTabId = activeInfo.tabId;

  // Step 2: Get that tab's URL
  chrome.tabs.get(activeInfo.tabId, (tab) => {
    if (tab?.url) {
      const newRootDomain = getRootDomain(tab.url);
      // Step 3: Compare with currentRootDomain
      if (newRootDomain && newRootDomain !== currentRootDomain) {
        console.log(
          `Active tab changed: root domain from '${currentRootDomain}' to '${newRootDomain}'.`
        );
        currentRootDomain = newRootDomain;
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
    }
  }
});
