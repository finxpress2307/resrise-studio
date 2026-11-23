/**
 * Resrise Studio - Main Application JavaScript
 * Clean vanilla modern JavaScript (ES6+) for browser & Node syntax check.
 * Manages Lucide icons, multi-creator roster, Telegram funnel routing,
 * shoppable affiliate lookbooks (EarnKaro & Amazon), lightboxes, and inquiry dispatcher.
 */

// ============================================================================
// 1. DATA ACCESS & GLOBAL DEFINITIONS
// ============================================================================
const data = (typeof window !== "undefined" && window.RESRISE_DATA) || {};

// ============================================================================
// 2. LUCIDE ICONS INITIALIZATION
// ============================================================================
function initLucideIcons() {
  if (typeof window !== "undefined" && window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
}

// ============================================================================
// 3. WHATSAPP BUTTON SYNC
// ============================================================================
function syncWhatsAppButton() {
  const whatsappBtn = document.getElementById("whatsappBtn");
  if (whatsappBtn && data.agency && data.agency.whatsappNumber) {
    const cleanNumber = data.agency.whatsappNumber.replace(/[^0-9]/g, "");
    const message = encodeURIComponent(
      "Hi Resrise Studio, I would like to inquire about initiating a virtual editorial campaign with the Resrise Creator Swarm."
    );
    whatsappBtn.href = `https://wa.me/${cleanNumber}?text=${message}`;
  }
}

// ============================================================================
// 4. CREATOR ROSTER SHOWCASE (Multi-Creator Hub & Telegram Routing)
// ============================================================================
function populateCreatorRoster() {
  const rosterGrid = document.getElementById("creatorRosterGrid");
  if (!rosterGrid || !data.creators) return;

  rosterGrid.innerHTML = data.creators
    .map(
      (creator) => `
      <div class="glass-panel rounded-3xl p-6 sm:p-8 border border-brand-border flex flex-col justify-between hover:border-brand-acid/40 transition-all group">
        <div>
          <!-- Creator Avatar & Header -->
          <div class="flex items-center gap-4 mb-5">
            <div class="relative w-16 h-16 sm:w-20 sm:h-20 rounded-2xl overflow-hidden shrink-0 border border-brand-border group-hover:border-brand-acid transition-colors">
              <img src="${creator.image}" alt="${creator.name}" class="w-full h-full object-cover">
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="font-display font-bold text-lg sm:text-xl text-white">${creator.name}</h3>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-acid/10 text-brand-acid border border-brand-acid/20">Verified</span>
              </div>
              <p class="font-mono text-xs text-brand-acid mt-0.5">${creator.handle}</p>
              <p class="text-[11px] font-mono text-zinc-400 mt-1">${creator.cities}</p>
            </div>
          </div>

          <!-- Creator Persona & Bio -->
          <p class="text-xs text-zinc-300 leading-relaxed mb-4">${creator.bio}</p>

          <!-- Niche Badge -->
          <div class="mb-6">
            <span class="inline-block text-[10px] font-mono uppercase tracking-wider px-3 py-1 rounded-full bg-zinc-900 text-zinc-300 border border-zinc-800">
              ${creator.niche}
            </span>
          </div>

          <!-- Shoppable Looks Previews -->
          <div class="mb-6 space-y-2.5">
            <p class="font-mono text-[11px] uppercase tracking-wider text-zinc-400 flex items-center justify-between">
              <span>Curated Drops & Looks</span>
              <span class="text-[9px] text-brand-acid">#affiliate</span>
            </p>
            <div class="space-y-2">
              ${(creator.shoppableLooks || [])
                .map(
                  (look) => `
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-zinc-950/70 border border-zinc-900 text-xs hover:border-zinc-800 transition-colors">
                  <div class="truncate pr-2">
                    <p class="font-medium text-white truncate text-[11px]">${look.title}</p>
                    <p class="text-[10px] text-zinc-400 font-mono">${look.store} • <span class="text-brand-acid">${look.price}</span></p>
                  </div>
                  <div class="flex items-center gap-1.5 shrink-0">
                    <a href="${look.earnkaroUrl}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 rounded bg-zinc-900 hover:bg-brand-acid hover:text-black text-[10px] font-mono text-zinc-300 border border-zinc-800 transition-colors" title="EarnKaro Tracked Deal">
                      Shop
                    </a>
                    <a href="${look.amazonUrl}" target="_blank" rel="noopener noreferrer" class="px-2 py-1 rounded bg-zinc-900 hover:bg-amber-400 hover:text-black text-[10px] font-mono text-zinc-300 border border-zinc-800 transition-colors" title="Amazon Associates Link">
                      Amazon
                    </a>
                  </div>
                </div>
              `
                )
                .join("")}
            </div>
          </div>
        </div>

        <!-- Direct Telegram VIP Join Button -->
        <div class="pt-4 border-t border-zinc-900">
          <a
            href="${creator.telegram.url}"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-acid text-xs uppercase tracking-wider py-3 px-5 rounded-xl font-bold flex items-center justify-center gap-2 w-full transition-all"
          >
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>${creator.telegram.ctaText}</span>
          </a>
          <p class="text-[9px] font-mono text-center text-zinc-400 mt-2">
            Canonical Handle: ${creator.telegram.handle}
          </p>
        </div>
      </div>
    `
    )
    .join("");
}

// ============================================================================
// 5. MUSE SHOWCASE GALLERY
// ============================================================================
function populateMuseShowcase() {
  const museGrid = document.getElementById("museShowcaseGrid");
  if (!museGrid || !data.muse || !data.muse.showcaseImages) return;

  museGrid.innerHTML = data.muse.showcaseImages
    .map(
      (item, index) => `
      <div class="lookbook-card group cursor-pointer relative aspect-[3/4] rounded-xl overflow-hidden" onclick="openMuseLightbox(${index})">
        <img src="${item.url}" alt="${item.caption}" class="w-full h-full object-cover">
        <div class="absolute inset-0 lookbook-overlay opacity-80 group-hover:opacity-95 flex flex-col justify-end p-5">
          <span class="text-[10px] font-mono text-brand-acid uppercase tracking-wider">${item.tag}</span>
          <p class="font-display font-bold text-sm text-white mt-1 leading-snug">${item.caption}</p>
        </div>
      </div>
    `
    )
    .join("");
}

// ============================================================================
// 6. PORTFOLIO CATEGORY FILTER & GRID
// ============================================================================
let activeCategory = "All";

function initPortfolioFilter() {
  const categoryContainer = document.getElementById("categoryFilterContainer");
  if (!categoryContainer || !data.portfolioCategories) return;

  categoryContainer.innerHTML = data.portfolioCategories
    .map(
      (cat) => `
      <button class="category-filter-btn px-4 py-2 rounded-full text-xs font-mono tracking-wider transition-all border ${
        cat === "All"
          ? "bg-brand-acid text-black border-brand-acid font-bold"
          : "bg-zinc-950/60 text-zinc-400 border-zinc-800 hover:text-white hover:border-zinc-700"
      }" data-category="${cat}">
        ${cat}
      </button>
    `
    )
    .join("");

  document.querySelectorAll(".category-filter-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const target = e.currentTarget;
      document.querySelectorAll(".category-filter-btn").forEach((b) => {
        b.className =
          "category-filter-btn px-4 py-2 rounded-full text-xs font-mono tracking-wider transition-all border bg-zinc-950/60 text-zinc-400 border-zinc-800 hover:text-white hover:border-zinc-700";
      });
      target.className =
        "category-filter-btn px-4 py-2 rounded-full text-xs font-mono tracking-wider transition-all border bg-brand-acid text-black border-brand-acid font-bold";
      activeCategory = target.getAttribute("data-category") || "All";
      renderPortfolio();
    });
  });
}

function renderPortfolio() {
  const portfolioGrid = document.getElementById("portfolioGrid");
  if (!portfolioGrid || !data.portfolio) return;

  const filtered =
    activeCategory === "All"
      ? data.portfolio
      : data.portfolio.filter((item) => item.category === activeCategory);

  portfolioGrid.innerHTML = filtered
    .map(
      (item) => `
      <div class="lookbook-card group cursor-pointer" onclick="openLightbox('${item.id}')">
        <div class="relative overflow-hidden aspect-[4/5] bg-zinc-950">
          <img src="${item.image}" alt="${item.title}" class="w-full h-full object-cover">

          <!-- Category Badge Top -->
          <div class="absolute top-4 left-4 z-10">
            <span class="text-[10px] font-mono uppercase tracking-widest px-2.5 py-1 rounded bg-black/60 backdrop-blur-md text-zinc-200 border border-white/10">
              ${item.category}
            </span>
          </div>

          <!-- Overlay Details Bottom -->
          <div class="absolute inset-0 lookbook-overlay opacity-90 group-hover:opacity-100 flex flex-col justify-end p-6">
            <div class="flex items-center justify-between text-xs font-mono text-zinc-400 mb-1">
              <span>${item.client}</span>
              <span class="text-zinc-500">${item.year}</span>
            </div>
            <h4 class="font-display font-bold text-lg text-white group-hover:text-brand-acid transition-colors">
              ${item.title}
            </h4>
            <div class="flex flex-wrap gap-1.5 mt-3">
              ${item.tags
                .map(
                  (tag) => `
                  <span class="text-[9px] font-mono text-zinc-400 bg-zinc-900/80 px-2 py-0.5 rounded border border-zinc-800">
                    ${tag}
                  </span>
                `
                )
                .join("")}
            </div>
          </div>
        </div>
      </div>
    `
    )
    .join("");

  initLucideIcons();
}

// ============================================================================
// 7. SERVICES & PRICING CARDS
// ============================================================================
function populatePricingCards() {
  const pricingContainer = document.getElementById("pricingCardsGrid");
  if (!pricingContainer || !data.services) return;

  pricingContainer.innerHTML = data.services
    .map(
      (pkg) => `
      <div class="glass-panel rounded-3xl p-8 border flex flex-col justify-between relative ${
        pkg.popular
          ? "border-brand-acid/50 shadow-[0_0_40px_rgba(212,255,0,0.08)] bg-zinc-900/90"
          : "border-brand-border"
      }">
        ${
          pkg.popular
            ? `
          <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 font-mono text-[10px] uppercase font-bold tracking-widest bg-brand-acid text-black px-4 py-1 rounded-full shadow-lg">
            ${pkg.badge}
          </div>
        `
            : ""
        }

        <div>
          <div class="font-mono text-xs text-brand-acid uppercase tracking-wider mb-2">
            ${pkg.tier}
          </div>
          <h3 class="font-display font-bold text-2xl text-white mb-2">${pkg.name}</h3>
          <p class="text-xs text-zinc-400 min-h-[36px] leading-relaxed mb-6">${pkg.subtitle}</p>

          <div class="flex items-baseline gap-2 mb-6 pb-6 border-b border-zinc-800">
            <span class="font-display font-extrabold text-3xl sm:text-4xl text-white">${pkg.price}</span>
            <span class="text-xs font-mono text-zinc-400">/ ${pkg.period}</span>
          </div>

          <div class="space-y-3 mb-8">
            <p class="font-mono text-[11px] uppercase tracking-wider text-zinc-400">Deliverables Included:</p>
            <ul class="space-y-2.5 text-xs text-zinc-300">
              ${pkg.features
                .map(
                  (feat) => `
                  <li class="flex items-start gap-2.5">
                    <i data-lucide="check" class="w-4 h-4 text-brand-acid shrink-0 mt-0.5"></i>
                    <span>${feat}</span>
                  </li>
                `
                )
                .join("")}
            </ul>
          </div>
        </div>

        <button
          onclick="selectPackage('${pkg.name.replace(/'/g, "\\'")}')"
          class="${
            pkg.popular ? "btn-acid" : "btn-outline-luxury"
          } text-xs uppercase tracking-wider py-3.5 px-6 rounded-xl font-bold flex items-center justify-center gap-2 w-full transition-all"
        >
          <span>${pkg.ctaText}</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </div>
    `
    )
    .join("");

  initLucideIcons();
}

// ============================================================================
// 8. LIGHTBOX MODAL MANAGEMENT
// ============================================================================
const lightboxModal = typeof document !== "undefined" ? document.getElementById("lightboxModal") : null;
const closeLightboxBtn = typeof document !== "undefined" ? document.getElementById("closeLightboxBtn") : null;

function openLightbox(id) {
  const item = data.portfolio && data.portfolio.find((p) => p.id === id);
  if (!item) return;

  setLightboxContent({
    image: item.image,
    title: item.title,
    client: `Client: ${item.client} • ${item.year}`,
    category: item.category,
    year: item.year,
    description: item.description,
    tags: item.tags
      .map(
        (t) =>
          `<span class="text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">${t}</span>`
      )
      .join(""),
    inquireAction: () => {
      closeLightbox();
      selectPackage(`Campaign Style: ${item.title}`);
    },
  });
}

function openMuseLightbox(index) {
  const item = data.muse && data.muse.showcaseImages && data.muse.showcaseImages[index];
  if (!item) return;

  setLightboxContent({
    image: item.url,
    title: item.caption,
    client: "Avanya Mehra • Editorial Drop",
    category: item.tag || "Editorial",
    year: "2026",
    description:
      "Official editorial archive frame captured using Resrise photorealistic neural pipeline. Featuring 100% facial geometry coherence across complex dynamic angles.",
    tags: `
      <span class="text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">Avanya Mehra</span>
      <span class="text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">8K Photorealism</span>
      <span class="text-[10px] font-mono text-zinc-400 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">Milan • Paris</span>
    `,
    inquireAction: () => {
      closeLightbox();
      selectPackage(`Feature Avanya: ${item.caption}`);
    },
  });
}

function setLightboxContent(content) {
  const lightboxImg = document.getElementById("lightboxImg");
  const lightboxTitle = document.getElementById("lightboxTitle");
  const lightboxClient = document.getElementById("lightboxClient");
  const lightboxCategory = document.getElementById("lightboxCategory");
  const lightboxYear = document.getElementById("lightboxYear");
  const lightboxDesc = document.getElementById("lightboxDesc");
  const lightboxTags = document.getElementById("lightboxTags");
  const lightboxInquireBtn = document.getElementById("lightboxInquireBtn");

  if (lightboxImg) lightboxImg.src = content.image;
  if (lightboxTitle) lightboxTitle.textContent = content.title;
  if (lightboxClient) lightboxClient.textContent = content.client;
  if (lightboxCategory) lightboxCategory.textContent = content.category;
  if (lightboxYear) lightboxYear.textContent = content.year;
  if (lightboxDesc) lightboxDesc.textContent = content.description;
  if (lightboxTags) lightboxTags.innerHTML = content.tags;

  if (lightboxInquireBtn) {
    lightboxInquireBtn.onclick = content.inquireAction;
  }

  const modal = document.getElementById("lightboxModal");
  if (modal) modal.classList.add("active");
  initLucideIcons();
}

function closeLightbox() {
  const modal = document.getElementById("lightboxModal");
  if (modal) modal.classList.remove("active");
}

// Bind modal listeners
if (typeof window !== "undefined") {
  const modal = document.getElementById("lightboxModal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) closeLightbox();
    });
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const activeModal = document.getElementById("lightboxModal");
      if (activeModal && activeModal.classList.contains("active")) {
        closeLightbox();
      }
    }
  });

  const closeBtn = document.getElementById("closeLightboxBtn");
  if (closeBtn) {
    closeBtn.addEventListener("click", closeLightbox);
  }
}

// ============================================================================
// 9. PACKAGE SELECTOR HELPER
// ============================================================================
function selectPackage(packageName) {
  const select = document.getElementById("servicePackage");
  if (select) {
    let found = false;
    for (let i = 0; i < select.options.length; i++) {
      if (select.options[i].text.toLowerCase().includes(packageName.toLowerCase())) {
        select.selectedIndex = i;
        found = true;
        break;
      }
    }
    if (!found && select.options.length > 0) {
      select.value = select.options[0].value;
    }
  }

  const inquireSection = document.getElementById("inquire");
  if (inquireSection) {
    inquireSection.scrollIntoView({ behavior: "smooth" });
  }
}

// ============================================================================
// 10. INQUIRY FORM DISPATCHER (mailto)
// ============================================================================
function initInquiryForm() {
  const form = document.getElementById("inquiryForm");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const nameInput = document.getElementById("clientName");
    const brandInput = document.getElementById("clientBrand");
    const serviceInput = document.getElementById("servicePackage");
    const budgetInput = document.getElementById("estimatedBudget");
    const messageInput = document.getElementById("clientMessage");

    const name = nameInput ? nameInput.value.trim() : "";
    const brand = brandInput ? brandInput.value.trim() : "";
    const service = serviceInput ? serviceInput.value : "";
    const budget = budgetInput ? budgetInput.value : "";
    const message = messageInput ? messageInput.value.trim() : "";

    const recipient = (data.agency && data.agency.contactEmail) || "contact.resrise@gmail.com";
    const subject = encodeURIComponent(`[Campaign Inquiry] ${brand} x Resrise Studio - ${name}`);

    const bodyContent = `Hello Resrise Studio Team,

I would like to inquire about initiating a virtual editorial campaign. Here are our campaign details:

---------------------------------------------------------
Client Name: ${name}
Brand / Agency: ${brand}
Selected Package: ${service}
Estimated Budget: ${budget}
---------------------------------------------------------

Project Brief & Requirements:
${message}

Looking forward to your review and next steps.

Best regards,
${name}
${brand}`;

    const mailtoUrl = `mailto:${recipient}?subject=${subject}&body=${encodeURIComponent(bodyContent)}`;
    window.location.href = mailtoUrl;

    alert(
      `Thank you, ${name}! Your email client is opening with a pre-filled campaign brief for ${recipient}. If your client did not launch automatically, feel free to contact us on WhatsApp or Telegram!`
    );
  });
}

// ============================================================================
// 11. MOBILE MENU TOGGLE
// ============================================================================
function initMobileMenu() {
  const mobileBtn = document.getElementById("mobileMenuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  if (!mobileBtn || !mobileMenu) return;

  mobileBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
    mobileMenu.classList.toggle("flex");
  });

  document.querySelectorAll(".mobile-link").forEach((link) => {
    link.addEventListener("click", () => {
      mobileMenu.classList.add("hidden");
      mobileMenu.classList.remove("flex");
    });
  });
}

// ============================================================================
// 12. EXPORTS & ATTACHMENTS
// ============================================================================
if (typeof window !== "undefined") {
  window.openLightbox = openLightbox;
  window.openMuseLightbox = openMuseLightbox;
  window.closeLightbox = closeLightbox;
  window.selectPackage = selectPackage;
  window.initLucideIcons = initLucideIcons;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    initLucideIcons,
    syncWhatsAppButton,
    populateCreatorRoster,
    populateMuseShowcase,
    initPortfolioFilter,
    renderPortfolio,
    populatePricingCards,
    openLightbox,
    openMuseLightbox,
    setLightboxContent,
    closeLightbox,
    selectPackage,
    initInquiryForm,
    initMobileMenu,
  };
}

// ============================================================================
// 13. MAIN INITIALIZATION
// ============================================================================
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    initLucideIcons();
    syncWhatsAppButton();
    populateCreatorRoster();
    populateMuseShowcase();
    initPortfolioFilter();
    renderPortfolio();
    populatePricingCards();
    initInquiryForm();
    initMobileMenu();
  });
}
