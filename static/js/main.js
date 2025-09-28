import { initPromoBanner } from './components/promoBanner.js';
import { initSiteBannerSearch } from './components/siteBannerSearch.js';
import { initHamburgerMenu } from './components/hamburgerMenu.js';
import { initHero } from './components/hero.js';
import { initBannerOffsets } from './components/bannerOffsets.js';

document.addEventListener('DOMContentLoaded', () => {
  initPromoBanner();        // looks for #promoBanner by default
  initSiteBannerSearch();   // looks for .site-banner by default
  initHamburgerMenu();      // looks for .site-banner by default
  initBannerOffsets();      // measures banner(s) and sets menu top offset
  initHero();               // populate hero slide 1 content
  initGuideTracking();      // client-side popularity tracking
  initPopularityReordering(); // reorder guides by local click count
});

// ============================================================
// GUIDE ANALYTICS - Client-side popularity tracking
// ============================================================

/**
 * Track guide link clicks in localStorage for personalized UX
 */
function initGuideTracking() {
  document.addEventListener('click', (e) => {
    // Match any guide link with data-guide-id attribute
    const el = e.target.closest('a[data-guide-id]');
    if (!el) return;

    const id = el.dataset.guideId;
    const title = el.textContent.trim();
    const source = getClickSource(el);

    // Log to localStorage for client-side popularity tracking
    try {
      const key = 'guideClicks';
      const clicks = JSON.parse(localStorage.getItem(key) || '{}');
      clicks[id] = (clicks[id] || 0) + 1;
      localStorage.setItem(key, JSON.stringify(clicks));
      
      // Optional: Log for debugging
      console.log(`📊 Guide click: ${id} (${clicks[id]} total) from ${source}`);
    } catch (error) {
      // Silently handle localStorage errors (private browsing, etc.)
      console.warn('Guide tracking failed:', error);
    }

    // Send event to Google Analytics 4
    try {
      if (typeof gtag !== 'undefined') {
        gtag('event', 'guide_click', {
          guide_id: id,
          guide_title: title,
          click_source: source,
          event_category: 'engagement',
          event_label: `${source}:${id}`,
          debug_mode: true
        });
        console.log(`📈 GA4 event sent: guide_click for ${id}`);
      }
    } catch (error) {
      console.warn('GA4 tracking failed:', error);
    }

    // Don't prevent navigation - let the click go through
  });
}

/**
 * Determine click source from element classes
 */
function getClickSource(element) {
  if (element.classList.contains('footer-link')) return 'footer';
  if (element.classList.contains('guide-index__link')) return 'index';
  if (element.classList.contains('guide__next__link')) return 'navigation';
  if (element.classList.contains('text-link')) return 'content';
  return 'other';
}

/**
 * Reorder guide lists by local popularity on page load
 */
function initPopularityReordering() {
  // Only run on guides index page
  if (!document.querySelector('.guide-index')) return;

  try {
    const clicks = JSON.parse(localStorage.getItem('guideClicks') || '{}');
    
    // Get all guide groups
    document.querySelectorAll('.guide-index__group').forEach(group => {
      const list = group.querySelector('.guide-index__list');
      if (!list) return;

      // Get all items and their click counts
      const items = Array.from(list.querySelectorAll('.guide-index__item'));
      const itemsWithClicks = items.map(item => {
        const link = item.querySelector('a[data-guide-id]');
        const guideId = link?.dataset.guideId;
        const clickCount = clicks[guideId] || 0;
        return { item, clickCount, guideId };
      });

      // Sort by click count (descending), then by original order
      itemsWithClicks.sort((a, b) => {
        if (a.clickCount !== b.clickCount) {
          return b.clickCount - a.clickCount; // Higher clicks first
        }
        // Keep original order for ties
        return items.indexOf(a.item) - items.indexOf(b.item);
      });

      // Reorder DOM elements
      itemsWithClicks.forEach(({ item }) => {
        list.appendChild(item);
      });

      // Optional: Add visual indicators for popular items
      itemsWithClicks.forEach(({ item, clickCount }) => {
        if (clickCount > 0) {
          const link = item.querySelector('a');
          link.title = `${link.title || link.textContent} (clicked ${clickCount} times)`;
        }
      });
    });

    console.log('📈 Guide lists reordered by local popularity');
  } catch (error) {
    console.warn('Popularity reordering failed:', error);
  }
}

