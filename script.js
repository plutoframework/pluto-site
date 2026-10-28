const menuToggle = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#site-nav");

function closeMenu() {
  menuToggle.setAttribute("aria-expanded", "false");
  navigation.classList.remove("is-open");
}

menuToggle.addEventListener("click", () => {
  const open = menuToggle.getAttribute("aria-expanded") !== "true";
  menuToggle.setAttribute("aria-expanded", String(open));
  navigation.classList.toggle("is-open", open);
});

navigation.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && navigation.classList.contains("is-open")) {
    closeMenu();
    menuToggle.focus();
  }
});

document.addEventListener("click", (event) => {
  if (!event.target.closest(".nav-shell")) closeMenu();
});

const desktopQuery = window.matchMedia("(min-width: 851px)");
desktopQuery.addEventListener("change", closeMenu);

const tabs = [...document.querySelectorAll('[role="tab"]')];

function selectTab(tab, moveFocus = false) {
  for (const candidate of tabs) {
    const selected = candidate === tab;
    candidate.setAttribute("aria-selected", String(selected));
    candidate.tabIndex = selected ? 0 : -1;
    document.getElementById(candidate.getAttribute("aria-controls")).hidden =
      !selected;
  }
  if (moveFocus) tab.focus();
}

for (const tab of tabs) {
  tab.addEventListener("click", () => selectTab(tab));
  tab.addEventListener("keydown", (event) => {
    const index = tabs.indexOf(tab);
    let next;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    if (event.key === "ArrowLeft")
      next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    selectTab(tabs[next], true);
  });
}

const status = document.querySelector(".copy-status");
let statusTimer;

function showStatus(message) {
  clearTimeout(statusTimer);
  status.textContent = message;
  status.classList.add("visible");
  statusTimer = setTimeout(() => status.classList.remove("visible"), 5000);
}

for (const button of document.querySelectorAll("[data-copy]")) {
  button.addEventListener("click", async () => {
    const source = document.getElementById(button.dataset.copy);
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("Clipboard unavailable");
      }
      await navigator.clipboard.writeText(source.textContent.trim());
      button.innerHTML = '<span aria-hidden="true">✓</span> Copied';
      showStatus("Install command copied. Ready for your terminal.");
      setTimeout(() => {
        button.innerHTML = '<span aria-hidden="true">⧉</span> Copy';
      }, 3000);
    } catch {
      const range = document.createRange();
      range.selectNodeContents(source);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      showStatus("Copy was unavailable. Command selected; copy it manually.");
    }
  });
}
