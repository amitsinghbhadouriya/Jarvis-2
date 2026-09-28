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
});