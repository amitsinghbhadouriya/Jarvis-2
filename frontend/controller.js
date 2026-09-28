$(document).ready(function () {
  // Display Speak Message
  eel.expose(DisplayMessage);
  function DisplayMessage(message) {
    $(".siri-message li:first").text(message);
    $(".siri-message").textillate("start");
  }

  eel.expose(ShowHood);
  function ShowHood() {
    $("#Oval").attr("hidden", false);
    $("#SiriWave").attr("hidden", true);
  }

  // Utility function to escape HTML and prevent XSS
  function escapeHTML(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  eel.expose(senderText);
  function senderText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (!chatBox) {
      console.warn("chat-canvas-body element not found in DOM");
      return;
    }
    var cleanMsg = (message || "").trim();
    if (cleanMsg !== "") {
      var escaped = escapeHTML(cleanMsg);
      chatBox.innerHTML += `<div class="row justify-content-end mb-4">
          <div class="width-size">
          <div class="sender_message">${escaped}</div>
      </div></div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(receiverText);
  function receiverText(message) {
    var chatBox = document.getElementById("chat-canvas-body");
    if (!chatBox) {
      console.warn("chat-canvas-body element not found in DOM");
      return;
    }
    var cleanMsg = (message || "").trim();
    if (cleanMsg !== "") {
      var escaped = escapeHTML(cleanMsg);
      chatBox.innerHTML += `<div class="row justify-content-start mb-4">
          <div class="width-size">
          <div class="receiver_message">${escaped}</div>
          </div>
      </div>`;

      chatBox.scrollTop = chatBox.scrollHeight;
    }
  }

  eel.expose(hideLoader);
  function hideLoader() {
    $("#Loader").attr("hidden", true);
    $("#FaceAuth").attr("hidden", false);
  }
  // Hide Face auth and display Face Auth success animation
  eel.expose(hideFaceAuth);
  function hideFaceAuth() {
    $("#FaceAuth").attr("hidden", true);
    $("#FaceAuthSuccess").attr("hidden", false);
  }
  // Hide success and display
  eel.expose(hideFaceAuthSuccess);
  function hideFaceAuthSuccess() {
    $("#FaceAuthSuccess").attr("hidden", true);
    $("#HelloGreet").attr("hidden", false);
  }

  // Hide Start Page and display blob
  eel.expose(hideStart);
  function hideStart() {
    $("#Start").attr("hidden", true);

    setTimeout(function () {
      $("#Oval").addClass("animate__animated animate__zoomIn");
      $("#Oval").attr("hidden", false);
    }, 1000);
  }

  // Clear chat window history in DOM
  eel.expose(clearChat);
  function clearChat() {
    var chatBox = document.getElementById("chat-canvas-body");
    if (chatBox) {
      chatBox.innerHTML = "";
    }
  }

  // Display a brief toast / status notification
  eel.expose(showToast);
  function showToast(message, type) {
    var toastContainer = document.getElementById("toast-container");
    if (!toastContainer) {
      console.log("[Toast]", type || "info", message);
      return;
    }
    var toast = document.createElement("div");
    toast.className = `alert alert-${type || "info"} alert-dismissible fade show cyber-toast`;
    toast.setAttribute("role", "alert");
    toast.innerHTML = `${escapeHTML(message)}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    toastContainer.appendChild(toast);
    setTimeout(function () {
      $(toast).alert("close");
    }, 4000);
  }

  // Update status message
  eel.expose(updateStatus);
  function updateStatus(statusText) {
    var statusEl = document.getElementById("assistant-status");
    if (statusEl) {
      statusEl.textContent = statusText;
    }
  }
});