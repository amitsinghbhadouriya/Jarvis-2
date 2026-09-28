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
    }, 1000);
    setTimeout(function () {
      $("#Oval").attr("hidden", false);
    }, 1000);
  }
});