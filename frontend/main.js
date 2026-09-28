$(document).ready(function () {

  if (window.eel) {
    eel.init();
  }
  $(".text").textillate({
    loop: true,
    speed: 1500,
    sync: true,
    in: {
      effect: "bounceIn",
    },
    out: {
      effect: "bounceOut",
    },
  });

  $(".siri-message").textillate({
    loop: true,
    sync: true,
    in: {
      effect: "fadeInUp",
      sync: true,
    },
    out: {
      effect: "fadeOutUp",
      sync: true,
    },
  });

  var siriWave = new SiriWave({
    container: document.getElementById("siri-container"),
    width: 940,
    style: "ios9",
    amplitude: "1",
    speed: "0.30",
    height: 200,
    autostart: true,
    waveColor: "#ff0000",
    waveOffset: 0,
    rippleEffect: true,
    rippleColor: "#ffffff",
  });

  $("#MicBtn").click(function () {
    if (window.eel) {
      eel.play_assistant_sound();
    }
    $("#Oval").attr("hidden", true);
    $("#SiriWave").attr("hidden", false);

    if (window.eel) {
      eel.takeAllCommands();
    }
  });

  function doc_keyUp(e) {
    if ((e.key === "j" || e.key === "J") && (e.ctrlKey || e.metaKey)) {
      if (window.eel) {
        eel.play_assistant_sound();
      }
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      if (window.eel) {
        eel.takeAllCommands();
      }
    }
  }

  document.addEventListener("keyup", doc_keyUp, false);

  function PlayAssistant(message) {
    const trimmed = (message || "").trim();
    if (trimmed !== "") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      if (window.eel) {
        eel.takeAllCommands(trimmed);
      }
      $("#chatbox").val("");
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      console.log("Empty message, nothing sent.");
    }
  }

  function ShowHideButton(message) {
    const trimmed = (message || "").trim();
    if (trimmed.length === 0) {
      $("#MicBtn").attr("hidden", false);
      $("#SendBtn").attr("hidden", true);
    } else {
      $("#MicBtn").attr("hidden", true);
      $("#SendBtn").attr("hidden", false);
    }
  }

  $("#chatbox").keyup(function () {
    const message = $("#chatbox").val();
    ShowHideButton(message);
  });

  $(document).on("click", "#SendBtn", function () {
    const message = $("#chatbox").val();
    PlayAssistant(message);
  });

  $("#chatbox").keypress(function (e) {
    const key = e.which || e.keyCode;
    if (key === 13) {
      e.preventDefault();
      const message = $("#chatbox").val();
      PlayAssistant(message);
    }
  });

  // Quick command chips interaction
  $(document).on("click", ".quick-cmd-chip", function () {
    const cmd = $(this).attr("data-cmd") || $(this).text().trim();
    if (cmd) {
      PlayAssistant(cmd);
      // Close offcanvas if opened on mobile
      if (window.innerWidth < 768) {
        var offcanvasEl = document.getElementById("offcanvasChat");
        if (offcanvasEl) {
          var bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
          if (bsOffcanvas) bsOffcanvas.hide();
        }
      }
    }
  });

  // Clear chat history
  $("#clearChatBtn").click(function () {
    if (window.eel && typeof eel.clearChatHistory === "function") {
      eel.clearChatHistory()(function (success) {
        if (success) {
          var chatBox = document.getElementById("chat-canvas-body");
          if (chatBox) {
            chatBox.innerHTML = '<div class="row justify-content-start mb-4"><div class="width-size"><div class="receiver_message">Conversation history cleared.</div></div></div>';
          }
          if (typeof eel.showToast === "function") {
            eel.showToast("Chat history cleared", "info");
          }
        }
      });
    } else {
      var chatBox = document.getElementById("chat-canvas-body");
      if (chatBox) {
        chatBox.innerHTML = "";
      }
    }
  });

  // Settings range inputs live display
  $("#settingSpeechRate").on("input", function () {
    $("#rateValue").text($(this).val());
  });

  $("#settingSpeechVol").on("input", function () {
    $("#volValue").text($(this).val() + "%");
  });

  // Save settings handler
  $("#saveSettingsBtn").click(function () {
    const rate = $("#settingSpeechRate").val();
    const vol = $("#settingSpeechVol").val();
    const sfx = $("#settingSoundEffects").is(":checked");
    const faceAuth = $("#settingFaceAuth").is(":checked");

    localStorage.setItem("jarvis_speech_rate", rate);
    localStorage.setItem("jarvis_speech_vol", vol);
    localStorage.setItem("jarvis_sfx", sfx);
    localStorage.setItem("jarvis_face_auth", faceAuth);

    var modalEl = document.getElementById("settingsModal");
    if (modalEl) {
      var bsModal = bootstrap.Modal.getInstance(modalEl);
      if (bsModal) bsModal.hide();
    }

    if (window.eel && typeof eel.showToast === "function") {
      eel.showToast("Preferences saved successfully", "success");
    }
  });

  // Load chat history when offcanvas opens
  var offcanvasEl = document.getElementById("offcanvasChat");
  if (offcanvasEl) {
    offcanvasEl.addEventListener("show.bs.offcanvas", function () {
      if (window.eel && typeof eel.getChatHistory === "function") {
        eel.getChatHistory(20)(function (history) {
          if (history && history.length > 0) {
            var chatBox = document.getElementById("chat-canvas-body");
            if (chatBox) {
              chatBox.innerHTML = "";
              history.forEach(function (item) {
                if (item.user_input && typeof eel.senderText === "function") {
                  eel.senderText(item.user_input);
                }
                if (item.response && typeof eel.receiverText === "function") {
                  eel.receiverText(item.response);
                }
              });
            }
          }
        });
      }
    });
  }
});
