(function () {
  "use strict";

  const header = document.querySelector(".topbar");
  const dropdownItems = Array.from(document.querySelectorAll(".has-dropdown"));
  const mobileToggle = document.querySelector(".mobile-nav-toggle");
  const mobileToggleLabel = document.querySelector(".mobile-nav-toggle-label");
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
      const isOpen = item === nextItem;
      item.classList.toggle("is-open", isOpen);

      const itemToggle = item.querySelector(":scope > .dropdown-toggle");
      if (itemToggle) {
        itemToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      }
    });
  }

  function toggleDropdown(item) {
    const isOpen = item.classList.contains("is-open");
    setOpenDropdown(isOpen ? null : item);
  }

  function setMobileMenuState(isOpen) {
    if (!header || !mobileToggle) {
      return;
    }

    header.classList.toggle("is-mobile-open", isOpen);
    mobileToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");

    if (mobileToggleLabel) {
      mobileToggleLabel.textContent = isOpen ? "Close" : "Menu";
    }
  }

  function closeMobileMenu() {
    setMobileMenuState(false);
    setOpenDropdown(null);
  }

  function isSmallViewport() {
    return mobileBreakpoint.matches;
  }

  function addMobileDropdownToggles() {
    dropdownItems.forEach((item, index) => {
      const itemLink = item.querySelector(":scope > a");
      const itemDropdown = item.querySelector(":scope > .nav-dropdown");

      if (!itemLink || !itemDropdown) {
        return;
      }

      if (!itemDropdown.id) {
        itemDropdown.id = "mobile-submenu-" + (index + 1);
      }

      let itemToggle = item.querySelector(":scope > .dropdown-toggle");

      if (!itemToggle) {
        itemToggle = document.createElement("button");
        itemToggle.type = "button";
        itemToggle.className = "dropdown-toggle";
        itemToggle.setAttribute("aria-expanded", "false");
        itemToggle.setAttribute("aria-controls", itemDropdown.id);
        itemToggle.setAttribute("aria-label", "Toggle submenu");
        itemToggle.textContent = "▾";
        item.insertBefore(itemToggle, itemDropdown);
      }

      itemToggle.addEventListener("click", (event) => {
        if (!isSmallViewport()) {
          return;
        }

        event.preventDefault();
        event.stopPropagation();
        toggleDropdown(item);
      });

      itemLink.addEventListener("click", (event) => {
        if (!isSmallViewport()) {
          return;
        }

        if (item.classList.contains("is-open")) {
          return;
        }

        event.preventDefault();
        toggleDropdown(item);
      });
    });
  }

  addMobileDropdownToggles();

  dropdownItems.forEach((item) => {
    item.addEventListener("pointerenter", () => {
      if (isSmallViewport()) {
        return;
      }

      if (closeTimer) {
        window.clearTimeout(closeTimer);
        closeTimer = null;
      }
      setOpenDropdown(item);
    });

    item.addEventListener("pointerleave", () => {
      if (isSmallViewport()) {
        return;
      }

      closeTimer = window.setTimeout(() => {
        setOpenDropdown(null);
      }, 220);
    });

    item.addEventListener("focusin", () => {
      if (isSmallViewport()) {
        return;
      }

      if (closeTimer) {
        window.clearTimeout(closeTimer);
        closeTimer = null;
      }
      setOpenDropdown(item);
    });

    item.addEventListener("focusout", () => {
      if (isSmallViewport()) {
        return;
      }

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
