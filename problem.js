const params = new URLSearchParams(window.location.search);
const tagFromUrl = params.get("tag");

if (tagFromUrl) {
  activeFilter = tagFromUrl;
}

const runBtn = document.querySelector(".btn:not(.primary)");
const submitBtn = document.querySelector(".btn.primary");

runBtn.addEventListener("click", () => {
  alert("Run clicked (demo)");
});

submitBtn.addEventListener("click", () => {
  alert("Submit clicked (demo)");
});
const templates = {
  java: `class Solution {
  public int[] twoSum(int[] nums, int target) {

  }
}`,

  cpp: `class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {

    }
};`,

  python: `class Solution:
    def twoSum(self, nums, target):
        pass`,

  go: `func twoSum(nums []int, target int) []int {

}`,

  js: `var twoSum = function(nums, target) {

};`
};

const languageSelect = document.querySelector(".lang-pill");

const editor = document.querySelector(".code-editor");

// set initial template
editor.value = templates[languageSelect.value];

languageSelect.addEventListener("change", () => {
  const lang = languageSelect.value;
  editor.value = templates[lang];
});

document.querySelectorAll(".tag.clickable").forEach(tag => {
  tag.addEventListener("click", () => {
    const value = tag.dataset.tag;
    window.location.href = `home.html?tag=${value}`;
  });
});

if (tagFromUrl) {
  document.querySelectorAll("#chips .chip").forEach(chip => {
    chip.classList.remove("active");
    if (chip.dataset.filter === tagFromUrl) {
      chip.classList.add("active");
    }
  });
}



document.querySelectorAll(".tc-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    if (tab.classList.contains("add")) return;

    document.querySelectorAll(".tc-tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
  });
});



const bookmarkBtn = document.querySelector('[title="Bookmark"]');
const formatBtn   = document.querySelector('[title="Format"]');
const resetBtn    = document.querySelector('[title="Reset"]');
const fullBtn     = document.querySelector('[title="Fullscreen"]');
const editorArea  = document.querySelector('.code-editor');

// Bookmark (demo)
bookmarkBtn.onclick = () => {
  alert("Bookmarked (demo)");
};

// Format (demo)
formatBtn.onclick = () => {
  editorArea.value = editorArea.value.trim();
};

// Reset editor
resetBtn.onclick = () => {
  editorArea.value = templates[languageSelect.value];
};

// Fullscreen editor
const codeCard = document.querySelector(".code-card");

fullBtn.onclick = () => {
  const isFull = codeCard.classList.toggle("fullscreen");
  document.body.style.overflow = isFull ? "hidden" : "";
};

document.addEventListener("keydown", e => {
  if (e.key === "Escape" && editorArea.classList.contains("fullscreen")) {
    editorArea.classList.remove("fullscreen");
    document.body.style.overflow = "";
  }
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && codeCard.classList.contains("fullscreen")) {
    codeCard.classList.remove("fullscreen");
    document.body.style.overflow = "";
  }
});
