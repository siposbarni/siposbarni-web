(function () {
  const state = {
    lang: "hu",
    content: null,
    artworks: null,
    flatWorks: [],
    activeIndex: 0
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  function valueForLang(value) {
    if (!value || typeof value !== "object") return value || "";
    return value[state.lang] || value.hu || value.en || "";
  }

  function getPath(source, path) {
    return path.split(".").reduce((acc, key) => (acc ? acc[key] : undefined), source);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function applyText() {
    $$("[data-i18n]").forEach((node) => {
      const text = valueForLang(getPath(state.content, node.dataset.i18n));
      if (text) node.textContent = text;
    });

    $$("[data-i18n-aria]").forEach((node) => {
      const text = valueForLang(getPath(state.content, node.dataset.i18nAria));
      if (text) node.setAttribute("aria-label", text);
    });

    document.documentElement.lang = state.lang;
    $("#instagram-link").href = state.content.links.instagram;
    $("#tiktok-link").href = state.content.links.tiktok;

    renderAboutMedia();
  }

  function renderAboutMedia() {
    const box = $("#about-media");
    const videoUrl = state.content.links.video;
    const imageUrl = state.content.about.image;
    const imageAlt = valueForLang(state.content.about.imageAlt);
    if (imageUrl) {
      box.innerHTML = `<img src="${imageUrl}" alt="${escapeHtml(imageAlt)}" loading="lazy">`;
      return;
    }
    if (!videoUrl) {
      box.innerHTML = `<span>${valueForLang(state.content.about.videoPlaceholder)}</span>`;
      return;
    }
    box.innerHTML = `<iframe loading="lazy" src="${videoUrl}" title="${valueForLang(state.content.about.title)}" allowfullscreen></iframe>`;
  }

  function renderGallery() {
    const gallery = $("#gallery-list");
    gallery.innerHTML = "";
    state.flatWorks = [];

    state.artworks.categories.forEach((category) => {
      const section = document.createElement("article");
      section.className = "gallery-category";

      const grid = document.createElement("div");
      grid.className = "thumb-grid";

      category.works.forEach((work) => {
        const index = state.flatWorks.length;
        state.flatWorks.push(work);

        const button = document.createElement("button");
        button.type = "button";
        button.className = "thumb-button";
        button.dataset.index = String(index);
        button.setAttribute("aria-label", valueForLang(work.title));
        button.innerHTML = `<img src="${work.thumb}" alt="${valueForLang(work.title)}" loading="lazy">`;
        button.addEventListener("click", () => openLightbox(index));
        grid.appendChild(button);
      });

      const copy = document.createElement("aside");
      copy.className = "category-copy";
      copy.innerHTML = `
        <h3>${escapeHtml(valueForLang(category.title))}</h3>
        <p>${escapeHtml(valueForLang(category.description))}</p>
      `;

      section.append(grid, copy);
      gallery.appendChild(section);
    });
  }

  function openLightbox(index) {
    state.activeIndex = index;
    updateLightbox();
    $("#lightbox").setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    $("#lightbox-close").focus();
  }

  function closeLightbox() {
    $("#lightbox").setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function moveLightbox(direction) {
    const total = state.flatWorks.length;
    state.activeIndex = (state.activeIndex + direction + total) % total;
    updateLightbox();
  }

  function updateLightbox() {
    const work = state.flatWorks[state.activeIndex];
    if (!work) return;

    $("#lightbox-image").src = work.image;
    $("#lightbox-image").alt = valueForLang(work.title);
    $("#lightbox-title").textContent = valueForLang(work.title);
    $("#lightbox-count").textContent = `${state.activeIndex + 1} / ${state.flatWorks.length}`;
    $("#lightbox-description").textContent = valueForLang(work.description);
    $("#lightbox-meta").innerHTML = [
      ["year", work.year],
      ["medium", valueForLang(work.medium)],
      ["size", work.size]
    ]
      .filter(([, value]) => value)
      .map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`)
      .join("");
  }

  function handleInterest() {
    const work = state.flatWorks[state.activeIndex];
    if (!work) return;

    const title = valueForLang(work.title);
    const prefill = valueForLang(state.content.contact.prefill);
    $("#message-field").value = `${prefill} ${title}`;
    closeLightbox();
    $("#contact").scrollIntoView({ behavior: "smooth", block: "start" });
    setTimeout(() => $("#message-field").focus(), 400);
  }

  function bindEvents() {
    $("#lightbox-close").addEventListener("click", closeLightbox);
    $("#lightbox-prev").addEventListener("click", () => moveLightbox(-1));
    $("#lightbox-next").addEventListener("click", () => moveLightbox(1));
    $("#interest-button").addEventListener("click", handleInterest);

    document.addEventListener("keydown", (event) => {
      if ($("#lightbox").getAttribute("aria-hidden") === "true") return;
      if (event.key === "Escape") closeLightbox();
      if (event.key === "ArrowLeft") moveLightbox(-1);
      if (event.key === "ArrowRight") moveLightbox(1);
    });
  }

  async function init() {
    const cacheKey = "v=20260718-11";
    const [contentResponse, artworkResponse] = await Promise.all([
      fetch(`content.json?${cacheKey}`, { cache: "no-store" }),
      fetch(`artworks.json?${cacheKey}`, { cache: "no-store" })
    ]);
    state.content = await contentResponse.json();
    state.artworks = await artworkResponse.json();

    if (!state.content.languages.includes(state.lang)) {
      state.lang = state.content.defaultLanguage;
    }

    applyText();
    renderGallery();
    bindEvents();
  }

  init().catch((error) => {
    console.error("Site initialization failed", error);
  });
})();
