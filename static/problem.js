document.addEventListener("DOMContentLoaded", async () => {
  const API_BASE = "http://127.0.0.1:8000";

  const params = new URLSearchParams(window.location.search);
  const currentId = Number(params.get("id"));

  if (!currentId) {
    alert("Invalid problem ID");
    return;
  }

  /* ======================
     NAVIGATION BUTTONS
  ====================== */
  const prevBtn = document.getElementById("prevProblem");
  const nextBtn = document.getElementById("nextProblem");

  if (prevBtn) {
    prevBtn.disabled = currentId <= 1;
    prevBtn.addEventListener("click", () => {
      window.location.href = `/problem?id=${currentId - 1}`;
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      window.location.href = `/problem?id=${currentId + 1}`;
    });
  }

  /* ======================
     FETCH PROBLEM
  ====================== */
  try {
    const res = await fetch(`${API_BASE}/api/problems/${currentId}`);
    if (!res.ok) throw new Error("Problem not found");

    const p = await res.json();

    document.getElementById("problemTitle").textContent =
      `${p.id}. ${p.title}`;

    const meta = document.getElementById("problemMeta");
    meta.innerHTML = `
      <span class="diff ${p.difficulty}">${p.difficulty}</span>
      ${p.tags.split(",").map(
        t => `<span class="tag clickable" data-tag="${t.trim()}">${t.trim()}</span>`
      ).join("")}
    `;

    document.getElementById("problemDescription").textContent =
      p.description || "No description yet.";

    document.getElementById("problemExample").textContent =
      p.tests.map(t =>
        `Input: ${t.input}\nOutput: ${t.expected_output}`
      ).join("\n\n");

    meta.addEventListener("click", e => {
      if (e.target.classList.contains("tag")) {
        window.location.href = `/?tag=${e.target.dataset.tag}`;
      }
    });

  } catch (err) {
    console.error(err);
    alert("Failed to load problem");
    return;
  }

  /* ======================
     VERDICT MODAL
  ====================== */
  function showVerdict(result) {
    const modal = document.createElement("div");
    modal.className = "verdict-modal";

    const isAccepted = result.status === "accepted";
    const statusColor = isAccepted ? "#22c55e" : "#ef4444";
    const statusText = isAccepted ? "✓ ACCEPTED" : "✗ " + result.status.toUpperCase();

    // Format pass probability as percentage
    const passPercentage = Math.round(result.pass_probability_on_this * 100);
    const probabilityHTML = `<div class="verdict-probability">Success Rate: <strong>${passPercentage}%</strong></div>`;

    let hintHTML = "";
    if (result.hint && result.hint.trim()) {
      hintHTML = `<div class="verdict-hint"><strong>Hint:</strong> ${result.hint}</div>`;
    }

    let recsHTML = "";
    if (result.recommendations && result.recommendations.length > 0) {
      recsHTML = `
        <div class="verdict-recommendations">
          <strong>Next Problems:</strong>
          <ul>
            ${result.recommendations.map(r => `<li>${r.title} (${r.difficulty})</li>`).join("")}
          </ul>
        </div>
      `;
    }

    let explanationHTML = "";
    if (result.explanation && result.explanation.trim()) {
      explanationHTML = `<div class="verdict-explanation"><em>${result.explanation}</em></div>`;
    }

    modal.innerHTML = `
      <div class="verdict-content">
        <div class="verdict-header" style="color: ${statusColor}">
          ${statusText}
        </div>
        
        ${probabilityHTML}
        
        <div class="verdict-body">
          ${hintHTML}
          ${recsHTML}
          ${explanationHTML}
        </div>
        
        <div class="verdict-actions">
          <button class="verdict-btn" onclick="location.reload()">Close</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // If there's a hint, also show notification
    if (result.hint && result.hint.trim()) {
      showHintNotification(result.hint);
    }
  }

  function showHintNotification(hint) {
    const notification = document.createElement("div");
    notification.className = "hint-notification";

    notification.innerHTML = `
      <div class="hint-notification-header">Hint Available</div>
      <div class="hint-notification-text">${hint}</div>
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      notification.classList.add("fade-out");
      setTimeout(() => notification.remove(), 300);
    }, 5000);
  }

  /* ======================
     RUN / SUBMIT
  ====================== */
  document.querySelector(".btn:not(.primary)")?.addEventListener("click", () =>
    alert("Run clicked (demo)")
  );

  document.querySelector(".btn.primary")?.addEventListener("click", async () => {
    const code = document.querySelector(".code-editor").value;
    const language = document.querySelector(".lang-pill").value;

    try {
      const res = await fetch(`${API_BASE}/api/mentor/submit/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 1,
          problem_id: currentId,
          code: code,
          time_spent_seconds: 0,
        }),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      const result = await res.json();
      console.log("Full response:", result);
      showVerdict(result);
    } catch (err) {
      console.error(err);
      alert("Submission failed: " + err.message);
    }
  });

  /* ======================
     EDITOR
  ====================== */
  const templates = {
    java: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // write your code here

    }
}`,

    cpp: `
#include <bits/stdc++.h>
using namespace std;

int main() {

    // write your code here

    return 0;
}`,

    python: `# write your code here

def main():
    pass


if __name__ == "__main__":
    main()
`,

    go: `package main

import "fmt"

func main() {

    // write your code here

    fmt.Println()
}
`,

    js: `// write your code here

function main() {

}

main();
`
  };

  const lang = document.querySelector(".lang-pill");
  const editor = document.querySelector(".code-editor");

  if (lang && editor) {
    editor.value = templates[lang.value];
    lang.addEventListener("change", () => {
      editor.value = templates[lang.value];
    });
  }
});