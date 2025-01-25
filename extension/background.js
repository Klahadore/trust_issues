// Helper function to extract the "root domain" from a full URL
function getRootDomain(urlStr) {
    try {
      const { hostname } = new URL(urlStr);
      // Split on '.' to see how many parts there are.
      const parts = hostname.split('.').filter(Boolean);
  
      // If there are more than 2 parts, assume the last two are the TLD+domain
      // e.g. www.example.com => parts = ['www', 'example', 'com']
      // We want 'example.com' as the root domain
      if (parts.length > 2) {
        return parts.slice(parts.length - 2).join('.');
      }
  
      // If it’s already just something like 'example.com' or 'localhost',
      // return it directly.
      return hostname;
    } catch (err) {
      console.error('Invalid URL encountered:', urlStr, err);
      return null;
    }
  }
  
  // Listen for tab updates (such as when a URL changes or a tab is reloaded).
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
      const rootDomain = getRootDomain(changeInfo.url);
      if (rootDomain) {
        console.log("Tab updated, root domain:", rootDomain);
      }
    }
  });
  
  // Listen when the active tab changes (e.g., user switches tabs).
  chrome.tabs.onActivated.addListener((activeInfo) => {
    chrome.tabs.get(activeInfo.tabId, (tab) => {
      if (tab.url) {
        const rootDomain = getRootDomain(tab.url);
        if (rootDomain) {
          console.log("Tab activated, root domain:", rootDomain);
        }
      }
    });
  });
  