const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const log = document.getElementById("chat-log");
const customerRole = document.body.dataset.customerRole;

function appendMessage(role, content) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const label = document.createElement("span");
  label.className = "role-label";
  label.textContent = role === "assistant" ? customerRole : "あなた";

  const text = document.createElement("p");
  text.textContent = content;

  wrapper.appendChild(label);
  wrapper.appendChild(text);
  log.appendChild(wrapper);
  log.scrollTop = log.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  appendMessage("user", message);
  input.value = "";
  input.disabled = true;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      const err = await res.json();
      appendMessage("assistant", `エラー: ${err.detail}`);
      return;
    }

    const data = await res.json();
    appendMessage("assistant", data.reply);
  } catch (err) {
    appendMessage("assistant", "通信エラーが発生しました。時間をおいて再度お試しください。");
  } finally {
    input.disabled = false;
    input.focus();
  }
});
