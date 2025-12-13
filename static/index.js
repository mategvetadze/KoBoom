/* =====================
   STATE
===================== */
document.addEventListener("DOMContentLoaded", () => {


const API_BASE = "http://127.0.0.1:8000";

let items = [];
let activeFilter = "all";
let activeDifficulty = "all";
let query = "";

/* =====================
   DOM ELEMENTS
===================== */

const problemBody = document.getElementById("problemBody");
const searchInput = document.getElementById("searchInput");
const chips = document.getElementById("chips");
const diffChips = document.getElementById("difficultyChips");
const filterLabel = document.getElementById("filterLabel");
const solvedEl = document.getElementById("statsSolved");
const totalEl = document.getElementById("statsTotal");
const toggleThemeBtn = document.getElementById("toggleTheme");
const shuffleBtn = document.getElementById("shuffleBtn");
const resetBtn = document.getElementById("resetBtn");

/* =====================
   HELPERS
===================== */

function titleCase(s) {
  return s.split("-").map(x => x[0].toUpperCase() + x.slice(1)).join(" ");
}

function matchesFilter(p) {
  if (activeFilter === "all") return true;
  return p.tags.includes(activeFilter);
}

function matchesDifficulty(p) {
  if (activeDifficulty === "all") return true;
  return p.diff === activeDifficulty;
}

function matchesQuery(p) {
  if (!query.trim()) return true;
  const q = query.toLowerCase();
  return (
    p.title.toLowerCase().includes(q) ||
    p.tags.some(t => t.includes(q)) ||
    String(p.id) === q
  );
}

/* =====================
   RENDER
===================== */

function render() {
  const filtered = items.filter(
    p => matchesFilter(p) && matchesDifficulty(p) && matchesQuery(p)
  );

  problemBody.innerHTML = filtered.map(p => {
    const tagHtml = p.tags
      .map(t => `<span class="tag">${titleCase(t)}</span>`)
      .join("");

    return `
    <tr onclick="location.href='/problem?id=${p.id}'">


        <td>
          <span class="status ${p.status}">
            ${p.status === "solved" ? "Solved" : "To Do"}
          </span>
        </td>
        <td>
          <div class="row-title">
            <span class="dot"></span>
            <span>${p.id}. ${p.title}</span>
          </div>
        </td>
        <td>
          <span class="diff ${p.diff}">
            ${p.diff[0].toUpperCase() + p.diff.slice(1)}
          </span>
        </td>
        <td>${tagHtml}</td>
        <td class="muted">${p.acc}</td>
      </tr>
    `;
  }).join("");

  filterLabel.textContent =
    `Showing: ${activeFilter === "all" ? "All" : titleCase(activeFilter)}`;
}

/* =====================
   FETCH DATA
===================== */

fetch(`${API_BASE}/api/problems`)
  .then(res => res.json())
  .then(data => {
    items = data.map(p => ({
      id: p.id,
      title: p.title,
      diff: p.difficulty,
      tags: p.tags.split(",").map(t => t.trim()),

      acc: Math.floor(Math.random() * 30 + 40) + "%",
      status: "todo"
    }));

    totalEl.textContent = `${items.length} total problems`;
    solvedEl.textContent = `0 solved`;
    render();
  })
  .catch(err => console.error(err));

/* =====================
   EVENTS
===================== */

searchInput.addEventListener("input", e => {
  query = e.target.value;
  render();
});

chips.addEventListener("click", e => {
  const btn = e.target.closest(".chip");
  if (!btn) return;

  chips.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  btn.classList.add("active");

  activeFilter = btn.dataset.filter;
  render();
});

diffChips.addEventListener("click", e => {
  const btn = e.target.closest(".chip");
  if (!btn) return;

  diffChips.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  btn.classList.add("active");

  activeDifficulty = btn.dataset.diff;
  render();
});

shuffleBtn.addEventListener("click", () => {
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  render();
});

resetBtn.addEventListener("click", () => {
  query = "";
  activeFilter = "all";
  activeDifficulty = "all";
  searchInput.value = "";

  document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  document.querySelector('.chip[data-filter="all"]').classList.add("active");
  document.querySelector('#difficultyChips .chip[data-diff="all"]').classList.add("active");

  render();
});

toggleThemeBtn.addEventListener("click", () => {
  document.body.classList.toggle("light");
  toggleThemeBtn.textContent =
    document.body.classList.contains("light") ? "🌞" : "🌙";
  localStorage.setItem(
    "demoTheme",
    document.body.classList.contains("light") ? "light" : "dark"
  );
});

/* =====================
   THEME INIT
===================== */

const savedTheme = localStorage.getItem("demoTheme");
if (savedTheme === "light") {
  document.body.classList.add("light");
  toggleThemeBtn.textContent = "🌞";
}


/* =====================
   SIMPLE AUTH (HOME PAGE)
===================== */

const openAuthBtn = document.getElementById("openAuth");
const authOverlay = document.getElementById("authOverlay");
const closeAuthBtn = document.getElementById("closeAuth");

const authTabs = document.querySelectorAll(".auth-tabs .tab");
const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");
const authTitle = document.getElementById("authTitle");

/* OPEN / CLOSE MODAL */
if (openAuthBtn && authOverlay) {
  openAuthBtn.onclick = () => authOverlay.classList.add("active");
}

if (closeAuthBtn && authOverlay) {
  closeAuthBtn.onclick = () => authOverlay.classList.remove("active");
}

/* TAB SWITCH */
if (authTabs.length) {
  authTabs.forEach(tab => {
    tab.onclick = () => {
      authTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      if (tab.dataset.tab === "login") {
        loginForm.classList.add("active");
        signupForm.classList.remove("active");
        authTitle.textContent = "Log In";
      } else {
        signupForm.classList.add("active");
        loginForm.classList.remove("active");
        authTitle.textContent = "Sign Up";
      }
    };
  });
}

/* LOGIN */
if (loginForm) {
  loginForm.onsubmit = e => {
    e.preventDefault();

    const email = loginForm.querySelector("input[type='email']").value;
    const username = email.split("@")[0];

    localStorage.setItem("user", JSON.stringify({ username, email }));

    openAuthBtn.textContent = username;
    authOverlay.classList.remove("active");
  };
}

/* SIGN UP */
if (signupForm) {
  signupForm.onsubmit = e => {
    e.preventDefault();

    const username = signupForm.querySelector("input[type='text']").value;
    const email = signupForm.querySelector("input[type='email']").value;

    localStorage.setItem("user", JSON.stringify({ username, email }));

    openAuthBtn.textContent = username;
    authOverlay.classList.remove("active");
  };
}

/* LOAD USER ON PAGE LOAD */
const savedUser = JSON.parse(localStorage.getItem("user"));
if (savedUser && openAuthBtn) {
  openAuthBtn.textContent = savedUser.username;
}

});
