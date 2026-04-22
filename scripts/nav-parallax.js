(function () {
  "use strict";

  const header = document.querySelector(".topbar");
  const dropdownItems = Array.from(document.querySelectorAll(".has-dropdown"));

  if (!header) {
    return;
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let ticking = false;
  let isScrolled = false;
  let closeTimer = null;

  function setOpenDropdown(nextItem) {
    dropdownItems.forEach((item) => {
      item.classList.toggle("is-open", item === nextItem);
    });
  }

  dropdownItems.forEach((item) => {
    item.addEventListener("pointerenter", () => {
      if (closeTimer) {
        window.clearTimeout(closeTimer);
        closeTimer = null;
      }
      setOpenDropdown(item);
    });

    item.addEventListener("pointerleave", () => {
      closeTimer = window.setTimeout(() => {
        setOpenDropdown(null);
      }, 220);
    });

    item.addEventListener("focusin", () => {
      if (closeTimer) {
        window.clearTimeout(closeTimer);
        closeTimer = null;
      }
      setOpenDropdown(item);
    });

    item.addEventListener("focusout", () => {
      window.requestAnimationFrame(() => {
        if (!item.contains(document.activeElement)) {
          setOpenDropdown(null);
        }
      });
    });
  });

  function updateParallax() {
    const scrollY = window.scrollY || 0;

    if (!isScrolled && scrollY > 48) {
      isScrolled = true;
      header.classList.add("is-scrolled");
    } else if (isScrolled && scrollY < 18) {
      isScrolled = false;
      header.classList.remove("is-scrolled");
    }

    ticking = false;
  }

  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  updateParallax();
})();
