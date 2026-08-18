/* Theme engine — light / dark with localStorage persistence */
(function () {
  const ROOT = document.documentElement;
  const KEY = "hv_theme";

  function syncIcon(theme) {
    const icon = document.getElementById("theme-icon");
    if (!icon) return;
    icon.className = theme === "light" ? "fa-solid fa-moon" : "fa-solid fa-sun";
  }

  function applyTheme(theme) {
    ROOT.setAttribute("data-theme", theme);
    try { localStorage.setItem(KEY, theme); } catch (e) {}
    syncIcon(theme);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const saved = (() => {
      try { return localStorage.getItem(KEY) || "light"; } catch (e) { return "light"; }
    })();
    applyTheme(saved);

    const btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", () => {
        const next = ROOT.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyTheme(next);
      });
    }
  });
})();
