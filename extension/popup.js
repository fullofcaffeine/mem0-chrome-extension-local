document.addEventListener("DOMContentLoaded", function () {
  const googleSignInButton = document.getElementById("googleSignInButton");

  function checkAuth() {
    chrome.storage.sync.get(["apiKey", "access_token"], function (data) {
      if (data.apiKey || data.access_token) {
        // User is logged in, close the popup and open the sidebar
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          chrome.tabs.sendMessage(tabs[0].id, {action: "toggleSidebar"});
          window.close();
        });
      }
    });
  }

  if (googleSignInButton) {
    googleSignInButton.addEventListener("click", function () {
      chrome.storage.sync.set({ userId: "chrome-extension-user" });
      chrome.storage.sync.get(["userLoggedIn"], function (data) {
        if (data.userLoggedIn) {
          chrome.tabs.create(
            { url: "http://localhost:8000/extension" },
            function (tab) {
              window.close();
            }
          );
        } else {
          chrome.tabs.create(
            { url: "http://localhost:8000/login?source=chrome-extension" },
            function (tab) {
              window.close();
          }
          );
        }
      });
    });
  }

  // Check auth status when popup opens
  checkAuth();
});