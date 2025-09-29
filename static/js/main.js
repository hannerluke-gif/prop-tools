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
 * Session-based rate limiting for analytics
 * Prevents rapid-fire clicking abuse (max 3 clicks per guide per minute per session)
 */
function checkAnalyticsRateLimit(guideId) {
  try {
    // Generate or retrieve session UUID
    let sessionId = localStorage.getItem('analyticsSessionId');
    if (!sessionId) {
      sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('analyticsSessionId', sessionId);
    }

    // Get rate limit data
    const rateLimitKey = 'analyticsRateLimit';
    const rateLimits = JSON.parse(localStorage.getItem(rateLimitKey) || '{}');
    const now = Date.now();
    const windowMs = 60 * 1000; // 1 minute window
    const maxClicks = 3; // max clicks per guide per minute
    
    // Clean old entries (older than window)
    const cutoff = now - windowMs;
    Object.keys(rateLimits).forEach(key => {
      rateLimits[key] = rateLimits[key].filter(timestamp => timestamp > cutoff);
      if (rateLimits[key].length === 0) {
        delete rateLimits[key];
      }
    });
    
    // Check current guide rate limit
    const limitKey = `${sessionId}:${guideId}`;
    const clicks = rateLimits[limitKey] || [];
    
    if (clicks.length >= maxClicks) {
      return false; // Rate limited
    }
    
    // Record this click
    clicks.push(now);
    rateLimits[limitKey] = clicks;
    localStorage.setItem(rateLimitKey, JSON.stringify(rateLimits));
    
    return true; // Allow analytics
  } catch (error) {
    console.warn('Rate limit check failed:', error);
    return true; // Default to allowing on error
  }
}

/**
 * Track guide link clicks in localStorage for personalized UX
 */
function initGuideTracking() {
  document.addEventListener('click', (e) => {
    // Target guide index links specifically
    const el = e.target.closest('.guide-index__link');
    if (!el) return;

    // Extract guide data with fallbacks
    const id = el.dataset.guideId || (el.getAttribute('href') || '').split('/').pop();
    const title = el.dataset.guideTitle || el.textContent.trim();
    const href = el.getAttribute('href');

    // Session-based deduplication to prevent abuse
    const shouldSendAnalytics = checkAnalyticsRateLimit(id);
    
    // Log to localStorage for client-side popularity tracking
    try {
      const key = 'guideClicks';
      const clicks = JSON.parse(localStorage.getItem(key) || '{}');
      clicks[id] = (clicks[id] || 0) + 1;
      localStorage.setItem(key, JSON.stringify(clicks));
      
      // Optional: Log for debugging
      console.log(`📊 Guide click: ${id} (${clicks[id]} total)`);
    } catch (error) {
      // Silently handle localStorage errors (private browsing, etc.)
      console.warn('Guide tracking failed:', error);
    }

    // Send event to our analytics endpoint (with rate limiting)
    if (shouldSendAnalytics) {
      const payload = JSON.stringify({ guide_id: id, guide_title: title, href });

    // Prefer sendBeacon so the request completes during navigation
    if (navigator.sendBeacon) {
      const blob = new Blob([payload], { type: 'application/json' });
      navigator.sendBeacon('/analytics/guide-click', blob);
      console.log(`📊 Analytics beacon sent: ${id}`);
    } else {
      fetch('/analytics/guide-click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true  // hint to allow during unload
      }).catch(() => {});
      console.log(`📊 Analytics fetch sent: ${id}`);
    }
    } else {
      console.log(`📊 Analytics rate limited for: ${id}`);
    }

    // Optional: also fire GA4
    if (window.gtag) {
      window.gtag('event', 'guide_click', {
        event_category: 'Guides',
        event_label: id,
        value: 1
      });
      console.log(`📈 GA4 event sent: guide_click for ${id}`);
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

