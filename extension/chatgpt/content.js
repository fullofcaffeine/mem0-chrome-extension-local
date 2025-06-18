// Mem0 Chrome Extension - Content Script for ChatGPT (Local Version)
// Version: 2.0 - 1:1 copy of original mem0 extension for local server
// This script is responsible for interacting with the ChatGPT interface.

console.log("Mem0: Content script v2.0 loading - Local server version");

let isProcessingMem0 = false;

// Initialize the MutationObserver variable
let observer;

function createPopup(container) {
  const popup = document.createElement("div");
  popup.className = "mem0-popup";
  popup.style.cssText = `
        display: none;
        position: absolute;
        background-color: #171717;
        color: white;
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 10000;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        margin-bottom: 11px;
        white-space: nowrap;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    `;
  container.appendChild(popup);
  return popup;
}

function addMem0Button() {
  const sendButton = document.querySelector('button[aria-label="Send prompt"]') ||
                     document.querySelector('button[data-testid="send-button"]') ||
                     document.querySelector('button[aria-label*="Send"]');

  if (sendButton && !document.querySelector("#mem0-button")) {
    const sendButtonContainer = sendButton.parentElement.parentElement;

    const mem0ButtonContainer = document.createElement("div");
    mem0ButtonContainer.style.position = "relative";
    mem0ButtonContainer.style.display = "inline-block";

    const mem0Button = document.createElement("img");
    mem0Button.id = "mem0-button";
    mem0Button.src = chrome.runtime.getURL("icons/icon48.png");
    mem0Button.style.width = "20px";
    mem0Button.style.height = "20px";
    mem0Button.style.cursor = "pointer";
    mem0Button.style.padding = "8px";
    mem0Button.style.borderRadius = "5px";
    mem0Button.style.transition = "filter 0.3s ease, opacity 0.3s ease";
    mem0Button.style.boxSizing = "content-box";
    mem0Button.style.marginBottom = "1px";

    const popup = createPopup(mem0ButtonContainer);

    mem0Button.addEventListener("click", () => handleMem0Click(popup));

    mem0Button.addEventListener("mouseenter", () => {
      if (!mem0Button.disabled) {
        mem0Button.style.filter = "brightness(70%)";
        tooltip.style.visibility = "visible";
        tooltip.style.opacity = "1";
      }
    });
    mem0Button.addEventListener("mouseleave", () => {
      mem0Button.style.filter = "none";
      tooltip.style.visibility = "hidden";
      tooltip.style.opacity = "0";
    });

    const tooltip = document.createElement("div");
    tooltip.textContent = "Add related memories";
    tooltip.style.visibility = "hidden";
    tooltip.style.backgroundColor = "black";
    tooltip.style.color = "white";
    tooltip.style.textAlign = "center";
    tooltip.style.borderRadius = "4px";
    tooltip.style.padding = "3px 6px";
    tooltip.style.position = "absolute";
    tooltip.style.zIndex = "1";
    tooltip.style.top = "calc(100% + 5px)";
    tooltip.style.left = "50%";
    tooltip.style.transform = "translateX(-50%)";
    tooltip.style.whiteSpace = "nowrap";
    tooltip.style.opacity = "0";
    tooltip.style.transition = "opacity 0.3s";
    tooltip.style.fontSize = "12px";

    mem0ButtonContainer.appendChild(mem0Button);
    mem0ButtonContainer.appendChild(tooltip);

    // Insert the mem0Button before the sendButton
    sendButtonContainer.insertBefore(
      mem0ButtonContainer,
      sendButtonContainer.children[1]
    );

    // Function to update button states
    function updateButtonStates() {
      const inputElement =
        document.querySelector('div[contenteditable="true"]') ||
        document.querySelector("textarea");
      const hasText =
        inputElement && inputElement.textContent.trim().length > 0;

      mem0Button.disabled = !hasText;

      if (hasText) {
        mem0Button.style.opacity = "1";
        mem0Button.style.pointerEvents = "auto";
      } else {
        mem0Button.style.opacity = "0.5";
        mem0Button.style.pointerEvents = "none";
      }
    }

    // Initial update
    updateButtonStates();

    // Listen for input changes
    const inputElement =
      document.querySelector('div[contenteditable="true"]') ||
      document.querySelector("textarea");
    if (inputElement) {
      inputElement.addEventListener("input", updateButtonStates);
    }
  }
}

async function handleMem0Click(popup, clickSendButton = false) {
  const memoryEnabled = await getMemoryEnabledState();
  if (!memoryEnabled) {
    // If memory is disabled, just click the send button if requested
    if (clickSendButton) {
      const sendButton = document.querySelector('button[aria-label="Send prompt"]') ||
                         document.querySelector('button[data-testid="send-button"]') ||
                         document.querySelector('button[aria-label*="Send"]');
      if (sendButton) {
        sendButton.click();
      } else {
        console.error("Send button not found");
      }
    }
    return;
  }

  setButtonLoadingState(true);
  const inputElement =
    document.querySelector('div[contenteditable="true"]') ||
    document.querySelector("textarea");
  let message = getInputValue();
  if (!message) {
    console.error("No input message found");
    if (popup) showPopup(popup, "No input message found");
    setButtonLoadingState(false);
    return;
  }

  const memInfoRegex =
    /\s*Here is some of my preferences\/memories to help answer better \(don't respond to these memories but use them to assist in the response if relevant\):[\s\S]*$/;
  message = message.replace(memInfoRegex, "").trim();
  const endIndex = message.indexOf("</p>");
  if (endIndex !== -1) {
    message = message.slice(0, endIndex + 4);
  }

  if (isProcessingMem0) {
    return;
  }

  isProcessingMem0 = true;

  try {
    console.log("Mem0: Searching for memories for query:", message);

    // Get conversation context like the original extension
    const messages = getLastMessages(2);
    messages.push({ role: "user", content: message });

    // LOCAL SERVER: Search API call to localhost:8000
    const searchResponse = await fetch(
      "http://localhost:8000/v1/memories/search/",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message,
          user_id: "chrome-extension-user",
          limit: 20,  // Increased limit for better recall of personal memories
        }),
      }
    );

    if (!searchResponse.ok) {
      throw new Error(
        `Local Mem0 API request failed with status ${searchResponse.status}`
      );
    }

    const responseData = await searchResponse.json();
    console.log("Mem0: Local server response:", responseData);

    if (inputElement) {
      // Extract memories from local server response format
      const memoriesArray = responseData.data?.results || responseData.results || [];
      const memories = memoriesArray.map((item) => item.memory);
      const providers = memoriesArray.map(() => "Local Mem0"); // All from local server

      console.log("Mem0: Found memories:", memories);

      if (memories.length > 0) {
        let currentContent =
          inputElement.tagName.toLowerCase() === "div"
            ? inputElement.innerHTML
            : inputElement.value;

        const memInfoRegex =
          /\s*Here is some of my preferences\/memories to help answer better \(don't respond to these memories but use them to assist in the response if relevant\):[\s\S]*$/;
        currentContent = currentContent.replace(memInfoRegex, "").trim();
        const lastParagraphRegex =
          /<p><br class="ProseMirror-trailingBreak"><\/p><p>$/;
        currentContent = currentContent.replace(lastParagraphRegex, "").trim();

        let memoriesContent =
          '<div id="mem0-wrapper" style="background-color: rgb(220, 252, 231); padding: 8px; border-radius: 4px; margin-top: 8px; margin-bottom: 8px;">';
        memoriesContent +=
          "<strong>Here is some of my preferences/memories to help answer better (don't respond to these memories but use them to assist in the response if relevant):</strong>";
        memories.forEach((mem) => {
          memoriesContent += `<div>- ${mem}</div>`;
        });
        memoriesContent += "</div>";

        if (inputElement.tagName.toLowerCase() === "div") {
          inputElement.innerHTML = `${currentContent}<div><br></div>${memoriesContent}`;
        } else {
          inputElement.value = `${currentContent}\n${memoriesContent}`;
        }
        inputElement.dispatchEvent(new Event("input", { bubbles: true }));
        
        console.log("Mem0: Memories injected successfully");
      } else {
        if (inputElement.tagName.toLowerCase() === "div") {
          inputElement.innerHTML = message;
        } else {
          inputElement.value = message;
        }
        inputElement.dispatchEvent(new Event("input", { bubbles: true }));
        if (popup) showPopup(popup, "No memories found");
      }
    } else {
      if (popup) showPopup(popup, "No input field found to update");
    }

    setButtonLoadingState(false);

    if (clickSendButton) {
      const sendButton = document.querySelector('button[aria-label="Send prompt"]') ||
                         document.querySelector('button[data-testid="send-button"]') ||
                         document.querySelector('button[aria-label*="Send"]');
      if (sendButton) {
        setTimeout(() => {
          sendButton.click();
        }, 100);
      } else {
        console.error("Send button not found");
      }
    }

    // LOCAL SERVER: Add memory asynchronously to localhost:8000 with existing memory context
    addMemoryWithContext(messages).catch((error) => {
      console.error("Error adding memory to local server:", error);
    });
  } catch (error) {
    console.error("Mem0 Local Error:", error);
    if (popup) showPopup(popup, "Error connecting to local Mem0 server");
    setButtonLoadingState(false);
    throw error;
  } finally {
    isProcessingMem0 = false;
  }
}

async function addMemoryWithContext(messages) {
  try {
    console.log("Mem0: Adding memory with conversation context:", messages);
    
    // Send messages with conversation context (like the original extension)
    const response = await fetch("http://localhost:8000/v1/memories/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages: messages,  // Already contains conversation context from getLastMessages()
        user_id: "chrome-extension-user",
        infer: true,  // Enable intelligent inference like the original
        metadata: {
          provider: "ChatGPT",
        },
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Memory addition failed with status ${response.status}`);
    }
    
    const result = await response.json();
    console.log("Mem0: Memory added with conversation context:", result);
    
    // Enhanced logging to show detailed memory operations
    if (result && result.results) {
      let operations;
      if (result.results.results) {
        operations = result.results.results;
      } else if (Array.isArray(result.results)) {
        operations = result.results;
      }
      
      if (operations && operations.length > 0) {
        console.log(`Mem0: Detailed memory operations (${operations.length} total):`);
        operations.forEach((op, index) => {
          if (typeof op === 'object' && op.event) {
            const event = op.event;
            const memory = op.memory || 'No memory text';
            const id = op.id || 'No ID';
            
            switch (event) {
              case 'ADD':
                console.log(`  ➕ ${index + 1}. ADDED: "${memory}" (ID: ${id})`);
                break;
              case 'UPDATE':
                console.log(`  🔄 ${index + 1}. UPDATED: "${memory}" (ID: ${id})`);
                break;
              case 'DELETE':
                console.log(`  🗑️ ${index + 1}. DELETED: "${memory}" (ID: ${id})`);
                break;
              case 'NONE':
                console.log(`  ⏸️ ${index + 1}. NO CHANGE: "${memory}" (ID: ${id})`);
                break;
              default:
                console.log(`  ❓ ${index + 1}. ${event}: "${memory}" (ID: ${id})`);
            }
          } else {
            console.log(`  📄 ${index + 1}. Raw operation:`, op);
          }
        });
        
        // Summary of operations
        const adds = operations.filter(op => op.event === 'ADD').length;
        const updates = operations.filter(op => op.event === 'UPDATE').length;
        const deletes = operations.filter(op => op.event === 'DELETE').length;
        const noChanges = operations.filter(op => op.event === 'NONE').length;
        
        console.log(`Mem0: Summary - Added: ${adds}, Updated: ${updates}, Deleted: ${deletes}, No Change: ${noChanges}`);
        
        // Alert if deletions occurred
        if (deletes > 0) {
          console.warn(`⚠️ Mem0: ${deletes} memories were deleted! Check server logs for details.`);
        }
      }
    }
    
  } catch (error) {
    console.error("Error in addMemoryWithContext:", error);
    // Fallback to simple memory addition without context
    fetch("http://localhost:8000/v1/memories/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages: messages,
        user_id: "chrome-extension-user",
        metadata: {
          provider: "ChatGPT",
        },
      }),
    });
  }
}

function getLastMessages(count) {
  const messageContainer = document.querySelector(
    ".flex.flex-col.text-sm.md\\:pb-9"
  );
  if (!messageContainer) return [];

  const messageElements = Array.from(messageContainer.children).reverse();
  const messages = [];

  for (const element of messageElements) {
    if (messages.length >= count) break;

    const userElement = element.querySelector(
      '[data-message-author-role="user"]'
    );
    const assistantElement = element.querySelector(
      '[data-message-author-role="assistant"]'
    );

    if (userElement) {
      const content = userElement
        .querySelector(".whitespace-pre-wrap")
        .textContent.trim();
      messages.unshift({ role: "user", content });
    } else if (assistantElement) {
      const content = assistantElement
        .querySelector(".markdown")
        .textContent.trim();
      messages.unshift({ role: "assistant", content });
    }
  }

  return messages;
}

function showPopup(popup, message) {
  // Create and add the (i) icon
  const infoIcon = document.createElement("span");
  infoIcon.textContent = "ⓘ ";
  infoIcon.style.marginRight = "3px";

  popup.innerHTML = "";
  popup.appendChild(infoIcon);
  popup.appendChild(document.createTextNode(message));

  popup.style.display = "block";
  setTimeout(() => {
    popup.style.display = "none";
  }, 2000);
}

function setButtonLoadingState(isLoading) {
  const mem0Button = document.querySelector("#mem0-button");
  if (mem0Button) {
    if (isLoading) {
      mem0Button.disabled = true;
      document.body.style.cursor = "wait";
      mem0Button.style.cursor = "wait";
      mem0Button.style.opacity = "0.7";
    } else {
      mem0Button.disabled = false;
      document.body.style.cursor = "default";
      mem0Button.style.cursor = "pointer";
      mem0Button.style.opacity = "1";
    }
  }
}

function getInputValue() {
  const inputElement =
    document.querySelector('div[contenteditable="true"]') ||
    document.querySelector("textarea");
  return inputElement ? inputElement.textContent || inputElement.value : null;
}

function addSyncButton() {
  const buttonContainer = document.querySelector("div.mt-5.flex.justify-end");
  if (buttonContainer) {
    let syncButton = document.querySelector("#sync-button");

    // If the syncButton does not exist, create it
    if (!syncButton) {
      syncButton = document.createElement("button");
      syncButton.id = "sync-button";
      syncButton.className = "btn relative btn-neutral mr-2";
      syncButton.style.color = "#b4844a";
      syncButton.style.backgroundColor = "transparent";
      syncButton.innerHTML =
        '<div id="sync-button-content" class="flex items-center justify-center font-normal">Sync</div>';
      syncButton.style.border = "1px solid #b4844a";

      const syncIcon = document.createElement("img");
      syncIcon.src = chrome.runtime.getURL("icons/icon48.png");
      syncIcon.style.width = "16px";
      syncIcon.style.height = "16px";
      syncIcon.style.marginRight = "8px";

      syncButton.prepend(syncIcon);

      syncButton.addEventListener("click", handleSyncClick);

      syncButton.addEventListener("mouseenter", () => {
        if (!syncButton.disabled) {
          syncButton.style.filter = "opacity(0.7)";
        }
      });
      syncButton.addEventListener("mouseleave", () => {
        if (!syncButton.disabled) {
          syncButton.style.filter = "opacity(1)";
        }
      });
    }

    if (!buttonContainer.contains(syncButton)) {
      buttonContainer.insertBefore(syncButton, buttonContainer.firstChild);
    }

    // Optionally, handle the disabled state
    function updateSyncButtonState() {
      // Define when the sync button should be enabled or disabled
      syncButton.disabled = false; // For example, always enabled
      // Update opacity or pointer events if needed
      if (syncButton.disabled) {
        syncButton.style.opacity = "0.5";
        syncButton.style.pointerEvents = "none";
      } else {
        syncButton.style.opacity = "1";
        syncButton.style.pointerEvents = "auto";
      }
    }

    updateSyncButtonState();
  } else {
    // If resetMemoriesButton or specificTable is not found, remove syncButton from DOM
    const existingSyncButton = document.querySelector("#sync-button");
    if (existingSyncButton && existingSyncButton.parentNode) {
      existingSyncButton.parentNode.removeChild(existingSyncButton);
    }
  }
}

function handleSyncClick() {
  getMemoryEnabledState().then((memoryEnabled) => {
    if (!memoryEnabled) {
      showSyncPopup(
        document.querySelector("#sync-button"),
        "Memory is disabled"
      );
      return;
    }

    const table = document.querySelector(
      "table.w-full.border-separate.border-spacing-0"
    );
    const syncButton = document.querySelector("#sync-button");

    if (table && syncButton) {
      const rows = table.querySelectorAll("tbody tr");
      let memories = [];

      // Change sync button state to loading
      setSyncButtonLoadingState(true);

      let syncedCount = 0;
      const totalCount = rows.length;

      rows.forEach((row) => {
        const cells = row.querySelectorAll("td");
        if (cells.length >= 1) {
          const content = cells[0]
            .querySelector("div.whitespace-pre-wrap")
            .textContent.trim();

          const memory = {
            role: "user",
            content: `Remember this about me: ${content}`,
          };

          memories.push(memory);

          sendMemoryToMem0(memory)
            .then(() => {
              syncedCount++;
              if (syncedCount === totalCount) {
                showSyncPopup(syncButton, `${syncedCount} memories synced`);
                setSyncButtonLoadingState(false);
              }
            })
            .catch((error) => {
              if (syncedCount === totalCount) {
                showSyncPopup(
                  syncButton,
                  `${syncedCount}/${totalCount} memories synced`
                );
                setSyncButtonLoadingState(false);
              }
            });
        }
      });

      sendMemoriesToMem0(memories)
        .then(() => {
          showSyncPopup(syncButton, `${memories.length} memories synced`);
          setSyncButtonLoadingState(false);
        })
        .catch((error) => {
          console.error("Error syncing memories:", error);
          showSyncPopup(syncButton, "Error syncing memories");
          setSyncButtonLoadingState(false);
        });
    } else {
      console.error("Table or Sync button not found");
    }
  });
}

// LOCAL SERVER: Modified to send memories to localhost:8000
function sendMemoriesToMem0(memories) {
  return new Promise((resolve, reject) => {
    fetch("http://localhost:8000/v1/memories/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages: memories,
        user_id: "chrome-extension-user",
        metadata: {
          provider: "ChatGPT",
        },
      }),
    })
      .then((response) => {
        if (!response.ok) {
          reject(`Failed to add memories: ${response.status}`);
        } else {
          resolve();
        }
      })
      .catch((error) =>
        reject(`Error sending memories to Local Mem0: ${error}`)
      );
  });
}

function setSyncButtonLoadingState(isLoading) {
  const syncButton = document.querySelector("#sync-button");
  const syncButtonContent = document.querySelector("#sync-button-content");
  if (syncButton) {
    if (isLoading) {
      syncButton.disabled = true;
      syncButton.style.cursor = "wait";
      document.body.style.cursor = "wait";
      syncButton.style.opacity = "0.7";
      syncButtonContent.textContent = "Syncing...";
    } else {
      syncButton.disabled = false;
      syncButton.style.cursor = "pointer";
      syncButton.style.opacity = "1";
      document.body.style.cursor = "default";
      syncButtonContent.textContent = "Sync";
    }
  }
}

function showSyncPopup(button, message) {
  const popup = document.createElement("div");

  // Create and add the (i) icon
  const infoIcon = document.createElement("span");
  infoIcon.textContent = "ⓘ ";
  infoIcon.style.marginRight = "3px";

  popup.appendChild(infoIcon);
  popup.appendChild(document.createTextNode(message));

  popup.style.cssText = `
        position: absolute;
        top: 50%;
        left: -160px;
        transform: translateY(-50%);
        background-color: #171717;
        color: white;
        padding: 6px 8px;
        border-radius: 6px;
        font-size: 12px;
        white-space: nowrap;
        z-index: 1000;
    `;

  button.style.position = "relative";
  button.appendChild(popup);

  setTimeout(() => {
    popup.remove();
  }, 3000);
}

// LOCAL SERVER: Modified to send memory to localhost:8000
function sendMemoryToMem0(memory) {
  return new Promise((resolve, reject) => {
    fetch("http://localhost:8000/v1/memories/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages: [{ content: memory.content, role: "user" }],
        user_id: "chrome-extension-user",
        metadata: {
          provider: "ChatGPT",
        },
      }),
    })
      .then((response) => {
        if (!response.ok) {
          reject(`Failed to add memory: ${response.status}`);
        } else {
          resolve();
        }
      })
      .catch((error) => reject(`Error sending memory to Local Mem0: ${error}`));
  });
}

function initializeMem0Integration() {
  document.addEventListener("DOMContentLoaded", () => {
    addMem0Button();
    addSyncButton();
    addEnterKeyInterception();
  });

  document.addEventListener("keydown", function (event) {
    if (event.ctrlKey && event.key === "m") {
      event.preventDefault();
      (async () => {
        await handleMem0Click(null, true);
      })();
    }
  });

  observer = new MutationObserver(() => {
    addMem0Button();
    addSyncButton();
  });

  observer.observe(document.body, { childList: true, subtree: true });

  // Add a MutationObserver to watch for changes in the DOM
  const observerForEnterKey = new MutationObserver(() => {
    addEnterKeyInterception();
  });

  observerForEnterKey.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

function addEnterKeyInterception() {
  const inputElement =
    document.querySelector('div[contenteditable="true"]') ||
    document.querySelector("textarea");

  if (inputElement && !inputElement.dataset.enterKeyIntercepted) {
    inputElement.dataset.enterKeyIntercepted = "true";

    inputElement.addEventListener(
      "keydown",
      async function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          event.stopPropagation();

          const memoryEnabled = await getMemoryEnabledState();
          if (memoryEnabled) {
            // Call handleMem0Click
            handleMem0Click(null, true)
              .then(() => {
                // Message sent automatically by handleMem0Click with clickSendButton=true
              })
              .catch((error) => {
                console.error("Error in Mem0 processing:", error);
              });
          } else {
            // If memory is disabled, just click the send button
            const sendButton = document.querySelector('button[aria-label="Send prompt"]') ||
                               document.querySelector('button[data-testid="send-button"]') ||
                               document.querySelector('button[aria-label*="Send"]');
            if (sendButton) {
              sendButton.click();
            } else {
              console.error("Send button not found");
            }
          }
        }
      },
      true
    );
  }
}

// Add this new function to get the memory_enabled state (default to enabled for local version)
function getMemoryEnabledState() {
  return new Promise((resolve) => {
    // For local version, we default to enabled since there's no cloud API dependency
    resolve(true);
  });
}

console.log("Mem0: Content script v2.0 observer started for local server");
initializeMem0Integration(); 

