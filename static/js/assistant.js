document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");
  const log = document.getElementById("chat-log");
  const empty = document.getElementById("chat-empty");
  const suggestions = document.getElementById("chat-suggestions");
  const modeBadge = document.getElementById("chat-mode");
  if (!form || !input || !log) return;

  function scrollToBottom() {
    log.scrollTop = log.scrollHeight;
  }

  function hideEmptyState() {
    if (empty) empty.remove();
  }

  function appendMessage(text, role) {
    hideEmptyState();
    const bubble = document.createElement("div");
    bubble.className = "msg " + (role === "user" ? "msg-user" : role === "error" ? "msg-error" : "msg-assistant");
    bubble.textContent = text;
    log.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function appendTyping() {
    hideEmptyState();
    const bubble = document.createElement("div");
    bubble.className = "msg msg-assistant";
    bubble.id = "typing-indicator";
    bubble.innerHTML = '<span class="typing-dots"><span></span><span></span><span></span></span>';
    bubble.setAttribute("aria-label", "T2C Assistant is typing");
    log.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function setMode(mode) {
    if (!modeBadge) return;
    if (!mode) {
      modeBadge.hidden = true;
      return;
    }
    modeBadge.hidden = false;
    modeBadge.dataset.mode = mode;
    modeBadge.textContent = mode === "openai" ? "OpenAI" : "Local fallback";
  }

  function autoResize() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 120) + "px";
  }
  input.addEventListener("input", autoResize);

  function sendMessage(text) {
    const trimmed = text.trim();
    if (!trimmed) return;

    appendMessage(trimmed, "user");
    input.value = "";
    autoResize();

    sendBtn.disabled = true;
    input.disabled = true;
    if (suggestions) suggestions.hidden = true;
    const typing = appendTyping();

    fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: trimmed }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Request failed");
        return res.json();
      })
      .then(function (data) {
        typing.remove();
        appendMessage(data.response, "assistant");
        setMode(data.mode);
      })
      .catch(function () {
        typing.remove();
        appendMessage("Something went wrong reaching the assistant. Please try again in a moment.", "error");
      })
      .finally(function () {
        sendBtn.disabled = false;
        input.disabled = false;
        input.focus();
      });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    sendMessage(input.value);
  });

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(input.value);
    }
    // Shift+Enter falls through to the default behavior (newline).
  });

  if (suggestions) {
    suggestions.addEventListener("click", function (event) {
      const chip = event.target.closest(".suggestion-chip");
      if (!chip) return;
      sendMessage(chip.textContent);
    });
  }
});
