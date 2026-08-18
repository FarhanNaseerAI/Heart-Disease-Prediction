/* Shared UI: nav, back-to-top, header shadow */
document.addEventListener("DOMContentLoaded", () => {
  const nav = document.getElementById("primary-nav");
  const toggle = document.getElementById("nav-toggle");
  const header = document.getElementById("site-header");
  const backToTop = document.getElementById("back-to-top");

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  const onScroll = () => {
    const y = window.scrollY || 0;
    if (header) {
      header.style.boxShadow = y > 8 ? "0 8px 24px rgba(15,28,36,0.08)" : "none";
    }
    if (backToTop) {
      backToTop.classList.toggle("visible", y > 420);
    }
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (backToTop) {
    backToTop.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});
