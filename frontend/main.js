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

  // Central Chat State Management
  const chatState = {
    messages: [],
    status: "IDLE", // IDLE | LISTENING | PROCESSING | RESPONDING | ERROR
    isLoading: false,
  };

  // Browser Web Speech API setup with graceful Python Eel fallback
  let recognition = null;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = function () {
      chatState.status = "LISTENING";
      if (typeof updateStatus === "function") {
        updateStatus("LISTENING...");
      }
      $("#hud-status-badge").removeClass("bg-primary bg-danger").addClass("bg-warning text-dark").text("LISTENING");
      if (window.eel && typeof eel.play_assistant_sound === "function") {
        eel.play_assistant_sound();
      }
    };

    recognition.onresult = function (event) {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (interimTranscript) {
        $("#chatbox").val(interimTranscript);
      }

      if (finalTranscript) {
        $("#chatbox").val(finalTranscript);
        PlayAssistant(finalTranscript);
      }
    };

    recognition.onerror = function (event) {
      console.warn("[SpeechRecognition Error]", event.error);
      if (typeof updateStatus === "function") {
        updateStatus("IDLE");
      }
      $("#hud-status-badge").removeClass("bg-warning text-dark").addClass("bg-primary text-white").text("IDLE");

      if (event.error === "not-allowed") {
        if (typeof showToast === "function") {
          showToast("Microphone permission denied in browser. Using system mic...", "warning");
        }
        triggerBackendVoiceInput();
      } else if (event.error === "no-speech") {
        if (typeof showToast === "function") {
          showToast("No speech detected. Please try again.", "info");
        }
      } else {
        triggerBackendVoiceInput();
      }
    };

    recognition.onend = function () {
      if (chatState.status === "LISTENING") {
        chatState.status = "IDLE";
        if (typeof updateStatus === "function") {
          updateStatus("IDLE");
        }
        $("#hud-status-badge").removeClass("bg-warning text-dark").addClass("bg-primary text-white").text("IDLE");
      }
    };
  }

  function triggerBackendVoiceInput() {
    if (window.eel && typeof eel.voice_input === "function") {
      chatState.status = "LISTENING";
      if (typeof updateStatus === "function") {
        updateStatus("LISTENING...");
      }
      $("#hud-status-badge").removeClass("bg-primary bg-danger").addClass("bg-warning text-dark").text("LISTENING");

      eel.voice_input()(function (res) {
        chatState.status = "IDLE";
        if (typeof updateStatus === "function") {
          updateStatus("IDLE");
        }
        $("#hud-status-badge").removeClass("bg-warning text-dark").addClass("bg-primary text-white").text("IDLE");
        if (res && res.success) {
          chatState.messages.push({ role: "user", content: res.user_message, timestamp: res.timestamp });
          chatState.messages.push({ role: "assistant", content: res.response, timestamp: res.timestamp });
        } else if (res && res.error) {
          console.warn("[Voice Input]", res.error);
        }
      });
    } else if (window.eel && typeof eel.takeAllCommands === "function") {
      $("#Oval").attr("hidden", true);
      $("#SiriWave").attr("hidden", false);
      eel.takeAllCommands();
    }
  }

  function startVoiceCapture() {
    if (recognition) {
      try {
        recognition.start();
      } catch (err) {
        console.warn("Speech recognition active or error, falling back to backend:", err);
        triggerBackendVoiceInput();
      }
    } else {
      triggerBackendVoiceInput();
    }
  }

  $("#MicBtn").click(function () {
    startVoiceCapture();
  });

  function doc_keyUp(e) {
    if ((e.key === "j" || e.key === "J") && (e.ctrlKey || e.metaKey)) {
      startVoiceCapture();
    }
  }

  document.addEventListener("keyup", doc_keyUp, false);

  function PlayAssistant(message) {
    const trimmed = (message || "").trim();
    if (!trimmed) {
      console.log("Empty message, nothing sent.");
      return;
    }

    // 1. Immediately render user message into DOM & chat state
    if (typeof senderText === "function") {
      senderText(trimmed);
    }
    chatState.messages.push({
      role: "user",
      content: trimmed,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    // 2. Clear input and restore mic button
    $("#chatbox").val("");
    ShowHideButton("");

    // 3. Set loading & typing indicators
    chatState.isLoading = true;
    chatState.status = "PROCESSING";
    if (typeof setAssistantTyping === "function") {
      setAssistantTyping(true);
    }
    if (typeof updateStatus === "function") {
      updateStatus("PROCESSING...");
    }
    $("#hud-status-badge").removeClass("bg-primary bg-warning bg-danger").addClass("bg-info text-dark").text("PROCESSING");

    // 4. Send request to backend
    if (window.eel && typeof eel.send_message === "function") {
      eel.send_message(trimmed, "text")(function (res) {
        chatState.isLoading = false;
        chatState.status = "IDLE";
        if (typeof setAssistantTyping === "function") {
          setAssistantTyping(false);
        }
        $("#hud-status-badge").removeClass("bg-info bg-warning bg-danger text-dark").addClass("bg-primary text-white").text("IDLE");

        if (res && res.success) {
          if (typeof receiverText === "function") {
            receiverText(res.response, res.timestamp);
          }
          chatState.messages.push({
            role: "assistant",
            content: res.response,
            timestamp: res.timestamp
          });
        } else {
          const errMsg = (res && res.response) || (res && res.error) || "Unable to process command. Please try again.";
          if (typeof receiverText === "function") {
            receiverText(errMsg);
          }
          if (typeof showToast === "function") {
            showToast(errMsg, "danger");
          }
        }
      });
    } else if (window.eel && typeof eel.takeAllCommands === "function") {
      eel.takeAllCommands(trimmed)(function (res) {
        chatState.isLoading = false;
        chatState.status = "IDLE";
        if (typeof setAssistantTyping === "function") {
          setAssistantTyping(false);
        }
        $("#hud-status-badge").removeClass("bg-info bg-warning bg-danger text-dark").addClass("bg-primary text-white").text("IDLE");

        if (res && res.response && typeof receiverText === "function") {
          receiverText(res.response, res.timestamp);
        }
      });
    } else {
      chatState.isLoading = false;
      chatState.status = "ERROR";
      if (typeof setAssistantTyping === "function") {
        setAssistantTyping(false);
      }
      $("#hud-status-badge").removeClass("bg-info bg-primary bg-warning").addClass("bg-danger text-white").text("ERROR");
      if (typeof receiverText === "function") {
        receiverText("Error: Jarvis backend is not connected. Please verify Python is running.");
      }
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
    if (key === 13 && !e.shiftKey) {
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

  // Clear live chat stream in main HUD
  $(document).on("click", "#clearMainChatBtn", function () {
    if (typeof clearChat === "function") {
      clearChat();
    }
    if (window.eel && typeof eel.clearChatHistory === "function") {
      eel.clearChatHistory()();
    }
    if (typeof showToast === "function") {
      showToast("Live conversation cleared", "info");
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
