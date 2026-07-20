const form = document.getElementById("review-form");
const input = document.getElementById("review-input");
const log = document.getElementById("review-log");
const submitButton = form.querySelector("button");
const customerRole = document.body.dataset.customerRole;

function appendReview(proposal, result) {
  const entry = document.createElement("div");
  entry.className = "review-entry";

  const proposalBlock = document.createElement("div");
  proposalBlock.className = "proposal";
  const proposalLabel = document.createElement("span");
  proposalLabel.className = "role-label";
  proposalLabel.textContent = "提案";
  const proposalText = document.createElement("p");
  proposalText.textContent = proposal;
  proposalBlock.appendChild(proposalLabel);
  proposalBlock.appendChild(proposalText);

  const resultBlock = document.createElement("div");
  resultBlock.className = "result";
  const resultLabel = document.createElement("span");
  resultLabel.className = "role-label";
  resultLabel.textContent = `${customerRole}からのレビュー`;
  const resultText = document.createElement("p");
  resultText.textContent = result;
  resultBlock.appendChild(resultLabel);
  resultBlock.appendChild(resultText);

  entry.appendChild(proposalBlock);
  entry.appendChild(resultBlock);
  log.appendChild(entry);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const proposal = input.value.trim();
  if (!proposal) return;

  input.disabled = true;
  submitButton.disabled = true;

  try {
    const res = await fetch("/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ proposal }),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`エラー: ${err.detail}`);
      return;
    }

    const data = await res.json();
    appendReview(proposal, data.result);
    input.value = "";
  } catch (err) {
    alert("通信エラーが発生しました。時間をおいて再度お試しください。");
  } finally {
    input.disabled = false;
    submitButton.disabled = false;
    input.focus();
  }
});
