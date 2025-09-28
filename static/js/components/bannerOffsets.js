/**
 * Compute and apply dynamic top offset for the mobile hamburger slide-out menu.
 *
 * Behavior:
 * - On all pages, position the menu immediately below the site banner.
 * - On the dashboard page, a promo banner exists above the site banner; however,
 *   the site banner itself is already offset by the promo in normal flow.
 *   We therefore measure the bottom of the site banner relative to the viewport
 *   and use that as the menu's top offset.
 * - On other pages (no promo), the site banner is at the top; we still measure
 *   and set the offset in case its height changes due to responsive breakpoints.
 *
 * Implementation details:
 * - We set a CSS variable --mobile-menu-top on the root banner element so SCSS
 *   can use it for the fixed-position mobile menu container.
 * - Recomputes on load, resize, and scroll (throttled via rAF).
 */
export function initBannerOffsets(root = document.querySelector('.site-banner')) {
  const banner = root;
  if (!banner) return () => {};

  const MOBILE_BREAKPOINT = 768; // keep consistent with other components
  let ticking = false;

  function measureAndApply() {
    // Only relevant for mobile where the menu is fixed, but harmless on desktop
    const rect = banner.getBoundingClientRect();
    // bottom relative to viewport top -> number of pixels the banner occupies
    const offset = Math.max(0, Math.round(rect.bottom));
    banner.style.setProperty('--mobile-menu-top', `${offset}px`);
  }

  function onScrollOrResize() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      measureAndApply();
      ticking = false;
    });
  }

  // Initial apply
  measureAndApply();

  // Events
  window.addEventListener('resize', onScrollOrResize);
  window.addEventListener('scroll', onScrollOrResize, { passive: true });

  // Some pages may change banner layout dynamically (e.g., classes toggled)
  const mo = new MutationObserver(() => onScrollOrResize());
  mo.observe(banner, { attributes: true, childList: true, subtree: true });

  // Teardown
  return () => {
    window.removeEventListener('resize', onScrollOrResize);
    window.removeEventListener('scroll', onScrollOrResize);
    try { mo.disconnect(); } catch {}
  };
}
