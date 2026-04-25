(function () {
  "use strict";

  const header = document.querySelector(".topbar");
  const dropdownItems = Array.from(document.querySelectorAll(".has-dropdown"));
  const mobileToggle = document.querySelector(".mobile-nav-toggle");
  const mobileBreakpoint = window.matchMedia("(max-width: 768px)");

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

  function setMobileMenuState(isOpen) {
    if (!header || !mobileToggle) {
      return;
    }

    header.classList.toggle("is-mobile-open", isOpen);
    mobileToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }

  function closeMobileMenu() {
    setMobileMenuState(false);
    setOpenDropdown(null);
  }

  function isSmallViewport() {
    return mobileBreakpoint.matches;
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

  if (mobileToggle) {
    mobileToggle.addEventListener("click", () => {
      const isOpen = header.classList.contains("is-mobile-open");
      setMobileMenuState(!isOpen);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMobileMenu();
      }
    });

    document.addEventListener("click", (event) => {
      if (!isSmallViewport() || !header.classList.contains("is-mobile-open")) {
        return;
      }

      if (!header.contains(event.target)) {
        closeMobileMenu();
      }
    });

    mobileBreakpoint.addEventListener("change", () => {
      if (!isSmallViewport()) {
        closeMobileMenu();
      }
    });
  }

  updateParallax();
})();
