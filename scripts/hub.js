(function () {
  "use strict";

  const PLACEHOLDER_IMAGE = "assets/report-covers/Image - no preview - square (1).jpg";

  const cards = Array.from(document.querySelectorAll("#report-cards .card"));
  const topicPills = Array.from(document.querySelectorAll(".topic-pill[data-topic-filter]"));
  const searchInput = document.getElementById("report-search");
  const clearSearch = document.getElementById("clear-search");
  const featuredBrief = document.getElementById("featured-brief");
  const featuredHiddenNote = document.getElementById("featured-hidden-note");
  const resultsCount = document.getElementById("results-count");
  const noResults = document.getElementById("no-results");

  if (!cards.length || !topicPills.length || !searchInput || !clearSearch || !featuredBrief || !featuredHiddenNote || !resultsCount || !noResults) {
    return;
  }

  let activeTopic = "all";

  function normalize(value) {
    return (value || "").toLowerCase().trim();
  }

  function parseCsv(value) {
    return normalize(value)
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function matchesCriteria(item) {
    const query = normalize(searchInput.value);
    const topics = parseCsv(item.dataset.topic);
    const title = normalize(item.dataset.title);
    const summary = normalize(item.dataset.summary);

    const matchesTopic = activeTopic === "all" || topics.includes(normalize(activeTopic));
    const matchesQuery = !query || title.includes(query) || summary.includes(query);

    return matchesTopic && matchesQuery;
  }

  function updateResults() {
    let visibleCount = 0;

    cards.forEach((card) => {
      const isVisible = matchesCriteria(card);

      card.classList.toggle("hidden", !isVisible);

      if (isVisible) {
        visibleCount += 1;
      }
    });

    const featuredVisible = matchesCriteria(featuredBrief);
    featuredBrief.classList.toggle("hidden", !featuredVisible);
    featuredHiddenNote.classList.toggle("hidden", featuredVisible);

    resultsCount.textContent = "Showing " + visibleCount + " of " + cards.length + " briefs";
    noResults.classList.toggle("hidden", visibleCount !== 0);
  }

  function applyImageFallbacks() {
    const reportImages = Array.from(document.querySelectorAll(".card-media img, .featured-media img"));

    reportImages.forEach((img) => {
      const src = (img.getAttribute("src") || "").trim();

      if (!src || src.includes("report-placeholder-thumb.svg")) {
        img.dataset.fallbackApplied = "true";
        img.src = PLACEHOLDER_IMAGE;
        img.classList.add("is-placeholder");
      }

      img.addEventListener("error", () => {
        if (img.dataset.fallbackApplied === "true") {
          return;
        }

        img.dataset.fallbackApplied = "true";
        img.src = PLACEHOLDER_IMAGE;
        img.classList.add("is-placeholder");
      });
    });
  }

  topicPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      topicPills.forEach((item) => {
        item.classList.remove("active");
        item.setAttribute("aria-pressed", "false");
      });

      pill.classList.add("active");
      pill.setAttribute("aria-pressed", "true");
      activeTopic = pill.dataset.topicFilter || "all";
      updateResults();
    });
  });

  searchInput.addEventListener("input", updateResults);

  clearSearch.addEventListener("click", () => {
    searchInput.value = "";
    updateResults();
  });

  applyImageFallbacks();
  updateResults();
})();
