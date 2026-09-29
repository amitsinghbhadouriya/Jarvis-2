/**
 * Jarvis 2 - Frontend Controller & Eel Bridge
 * Manages UI state transitions, live message streaming, and Python RPC endpoints.
 */

// Utility function to escape HTML and prevent XSS
function escapeHTML(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Utility to get current formatted time
function getCurrentTime() {
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12;
  return `${hours}:${minutes} ${ampm}`;
}

// Display Speak Message on Siri screen
function DisplayMessage(message) {
  const cleanMsg = (message || "").trim();
  $(".siri-message li:first").text(cleanMsg);
  $(".siri-message").textillate("start");

  // Also update live HUD status if element exists
  const statusEl = document.getElementById("hud-status-text");
  if (statusEl) {
    statusEl.textContent = cleanMsg;
  }
}

// Switch view to central HUD
function ShowHood() {
  $("#Oval").attr("hidden", false);
  $("#SiriWave").attr("hidden", true);
}

// Render user message into both the on-screen live feed and offcanvas drawer
function senderText(message, timestamp) {
  const cleanMsg = (message || "").trim();
  if (!cleanMsg) return;

  const escaped = escapeHTML(cleanMsg);
  const timeStr = timestamp || getCurrentTime();

  const msgHTML = `
    <div class="row justify-content-end mb-3 message-row user-message-row animate__animated animate__fadeInUp animate__faster">
      <div class="width-size">
        <div class="sender_message">
          <div class="message-content">${escaped}</div>
          <div class="message-meta text-end"><small class="message-time">${timeStr}</small></div>
        </div>
      </div>
    </div>`;

  // 1. Offcanvas drawer
  const offcanvasBox = document.getElementById("chat-canvas-body");
  if (offcanvasBox) {
    offcanvasBox.innerHTML += msgHTML;
    offcanvasBox.scrollTop = offcanvasBox.scrollHeight;
  }

  // 2. On-screen live chat feed
  const liveBox = document.getElementById("live-chat-messages");
  if (liveBox) {
    liveBox.innerHTML += msgHTML;
    liveBox.scrollTop = liveBox.scrollHeight;
  }
}

// Render assistant response into both on-screen live feed and offcanvas drawer
function receiverText(message, timestamp) {
  const cleanMsg = (message || "").trim();
  if (!cleanMsg) return;

  // Remove typing indicator if present
  setAssistantTyping(false);

  const escaped = escapeHTML(cleanMsg);
  const timeStr = timestamp || getCurrentTime();

  const msgHTML = `
    <div class="row justify-content-start mb-3 message-row assistant-message-row animate__animated animate__fadeInUp animate__faster">
      <div class="width-size">
        <div class="receiver_message">
          <div class="d-flex align-items-center mb-1">
            <i class="bi bi-robot text-info me-1"></i>
            <strong class="text-info small">JARVIS</strong>
          </div>
          <div class="message-content">${escaped}</div>
          <div class="message-meta text-end"><small class="message-time">${timeStr}</small></div>
        </div>
      </div>
    </div>`;

  // 1. Offcanvas drawer
  const offcanvasBox = document.getElementById("chat-canvas-body");
  if (offcanvasBox) {
    offcanvasBox.innerHTML += msgHTML;
    offcanvasBox.scrollTop = offcanvasBox.scrollHeight;
  }

  // 2. On-screen live chat feed
  const liveBox = document.getElementById("live-chat-messages");
  if (liveBox) {
    liveBox.innerHTML += msgHTML;
    liveBox.scrollTop = liveBox.scrollHeight;
  }

  // Also update live HUD banner
  const banner = document.getElementById("assistant-response-banner");
  if (banner) {
    banner.textContent = cleanMsg;
    banner.removeAttribute("hidden");
  }
}

// Toggle animated typing / processing indicator
function setAssistantTyping(isTyping) {
  const liveBox = document.getElementById("live-chat-messages");
  const offcanvasBox = document.getElementById("chat-canvas-body");

  // Remove existing indicators
  $(".typing-indicator-container").remove();

  if (!isTyping) return;

  const typingHTML = `
    <div class="row justify-content-start mb-3 typing-indicator-container animate__animated animate__fadeIn">
      <div class="width-size">
        <div class="receiver_message py-2 px-3">
          <div class="d-flex align-items-center">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="ms-2 text-info small">Jarvis is processing...</span>
          </div>
        </div>
      </div>
    </div>`;

  if (liveBox) {
    liveBox.innerHTML += typingHTML;
    liveBox.scrollTop = liveBox.scrollHeight;
  }
  if (offcanvasBox) {
    offcanvasBox.innerHTML += typingHTML;
    offcanvasBox.scrollTop = offcanvasBox.scrollHeight;
  }
}

// Hide Loader and show Face Auth
function hideLoader() {
  $("#Loader").attr("hidden", true);
  $("#FaceAuth").attr("hidden", false);
}

// Hide Face auth and display Face Auth success animation
function hideFaceAuth() {
  $("#FaceAuth").attr("hidden", true);
  $("#FaceAuthSuccess").attr("hidden", false);
}

// Hide success and display greeting
function hideFaceAuthSuccess() {
  $("#FaceAuthSuccess").attr("hidden", true);
  $("#HelloGreet").attr("hidden", false);
}

// Hide Start Page and display central HUD
function hideStart() {
  $("#Start").attr("hidden", true);
  setTimeout(function () {
    $("#Oval").addClass("animate__animated animate__zoomIn");
    $("#Oval").attr("hidden", false);
  }, 1000);
}

// Clear chat history in DOM
function clearChat() {
  const offcanvasBox = document.getElementById("chat-canvas-body");
  if (offcanvasBox) {
    offcanvasBox.innerHTML = "";
  }
  const liveBox = document.getElementById("live-chat-messages");
  if (liveBox) {
    liveBox.innerHTML = "";
  }
  const banner = document.getElementById("assistant-response-banner");
  if (banner) {
    banner.setAttribute("hidden", "true");
    banner.textContent = "";
  }
}

// Display a brief toast / alert notification
function showToast(message, type) {
  const toastContainer = document.getElementById("toast-container");
  if (!toastContainer) {
    console.log("[Toast]", type || "info", message);
    return;
  }
  const toast = document.createElement("div");
  toast.className = `alert alert-${type || "info"} alert-dismissible fade show cyber-toast`;
  toast.setAttribute("role", "alert");
  toast.innerHTML = `${escapeHTML(message)}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
  toastContainer.appendChild(toast);
  setTimeout(function () {
    $(toast).alert("close");
  }, 4000);
}

// Update status text
function updateStatus(statusText) {
  const statusEl = document.getElementById("assistant-status");
  if (statusEl) {
    statusEl.textContent = statusText;
  }
  const hudBadge = document.getElementById("hud-status-badge");
  if (hudBadge) {
    hudBadge.textContent = statusText;
  }
}

// Register all functions immediately on window and expose to Eel
window.DisplayMessage = DisplayMessage;
window.ShowHood = ShowHood;
window.senderText = senderText;
window.receiverText = receiverText;
window.setAssistantTyping = setAssistantTyping;
window.hideLoader = hideLoader;
window.hideFaceAuth = hideFaceAuth;
window.hideFaceAuthSuccess = hideFaceAuthSuccess;
window.hideStart = hideStart;
window.clearChat = clearChat;
window.showToast = showToast;
window.updateStatus = updateStatus;

if (typeof eel !== "undefined") {
  eel.expose(DisplayMessage);
  eel.expose(ShowHood);
  eel.expose(senderText);
  eel.expose(receiverText);
  eel.expose(setAssistantTyping);
  eel.expose(hideLoader);
  eel.expose(hideFaceAuth);
  eel.expose(hideFaceAuthSuccess);
  eel.expose(hideStart);
  eel.expose(clearChat);
  eel.expose(showToast);
  eel.expose(updateStatus);
}