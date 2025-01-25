const config_url = "http://0.0.0.0:8000/";
let checkedDomains = new Set(); // Stores domains we've already checked

console.log("Background script loaded");

// Get simple website address (like "google.com" from "https://mail.google.com")
function getRootDomain(url) {
  try {
    const urlObj = new URL(url);
    const parts = urlObj.hostname.split(".").filter((p) => p !== "");
    return parts.slice(-2).join("."); // Get last two parts
  } catch {
    return null;
  }
}

async function addURL(domain) {
  try {
    // Basic validation
    if (!domain || !domain.includes(".")) {
      console.error("Invalid domain:", domain);
      return { error: "Invalid domain format" };
    }

    const response = await fetch(`${config_url}add_website`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ website: domain }),
      // Important for long requests
      signal: AbortSignal.timeout(45000), // 45 second timeout
    });

    if (!response.ok) {
      const error = await response.json();
      console.error("Server error:", error);
      return { error: error.detail || "Request failed" };
    }

    return await response.json();
  } catch (err) {
    if (err.name === "AbortError") {
      console.error("Request timed out");
      return { error: "Request took too long - try again later" };
    }
    console.error("Network error:", err);
    return { error: "Network connection failed" };
  }
}
// Check if domain is new with our API
async function checkURL(domain) {
  try {
    if (!domain.includes(".")) {
      return;
    }
    const response = await fetch(`${config_url}check_root_url/${domain}`);
    const result = await response.json();
    console.log("API response:", result, domain);
    return result.exists;
  } catch (error) {
    console.error("Failed to check domain:", error);
  }
}

// Handle tab changes
async function handleTabUpdate(tabId) {
  try {
    // Get current tab info
    const tab = await chrome.tabs.get(tabId);
    if (!tab.url) return;

    // Get simple domain format
    const domain = getRootDomain(tab.url);
    if (!domain) return;

    if (checkedDomains.has(domain)) {
      return true;
    }
    // Only check new domains
    checkedDomains.add(domain);
    const exists = await checkURL(domain);
    if (!exists) {
      const res = await addURL(domain);
      console.log(res);
    }
  } catch (error) {
    console.error("Tab error:", error);
  }
}

// Listen for these two events:
// 1. When user switches tabs
chrome.tabs.onActivated.addListener((info) => handleTabUpdate(info.tabId));

// 2. When website URL changes in current tab
chrome.tabs.onUpdated.addListener((tabId, change) => {
  if (change.url) handleTabUpdate(tabId);
});
