document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("nav-toggle");
  const links = document.getElementById("nav-links");
  const navbar = document.querySelector(".navbar");

  // The mobile menu's top offset must match the navbar's *real* rendered
  // height, not a guessed constant — a stale hardcoded value is exactly
  // what caused the menu to render clipped/misaligned on real devices
  // after the navbar's own height changed (touch-target sizing fix).
  function syncNavbarHeight() {
    if (!navbar) return;
    const height = navbar.getBoundingClientRect().height;
    if (height > 0) {
      document.documentElement.style.setProperty("--navbar-height", height + "px");
    }
  }
  syncNavbarHeight();
  window.addEventListener("resize", syncNavbarHeight);
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(syncNavbarHeight);
  }

  if (!toggle || !links) return;

  function closeMenu() {
    links.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
  }

  toggle.addEventListener("click", function () {
    const isOpen = links.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) syncNavbarHeight();
  });

  links.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && links.classList.contains("is-open")) {
      closeMenu();
      toggle.focus();
    }
  });
});
