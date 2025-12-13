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
     RUN / SUBMIT (DEMO)
  ====================== */
  document.querySelector(".btn:not(.primary)")?.addEventListener("click", () =>
    alert("Run clicked (demo)")
  );

  document.querySelector(".btn.primary")?.addEventListener("click", () =>
    alert("Submit clicked (demo)")
  );

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
