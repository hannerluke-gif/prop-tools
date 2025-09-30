// analytics.js - Complete analytics system
// Includes Google Analytics 4, guide click tracking, and popularity features

// ============================================================
// GOOGLE ANALYTICS 4 SETUP
// ============================================================

// Initialize Google Analytics dataLayer
window.dataLayer = window.dataLayer || [];

function gtag() {
  dataLayer.push(arguments);
}

// Set up GA4
gtag('js', new Date());
gtag('config', 'G-ZEBP98J6ZQ', {
  'debug_mode': true
});

// Export gtag for use in other modules
window.gtag = gtag;

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

    // Rate limiting: max 3 clicks per guide per minute per session
    const rateLimitKey = 'analyticsRateLimit';
    const rateLimits = JSON.parse(localStorage.getItem(rateLimitKey) || '{}');
    const now = Date.now();
    const windowMs = 60 * 1000; // 1 minute
    const maxClicks = 3;

    // Clean up old entries
    Object.keys(rateLimits).forEach(key => {
      rateLimits[key] = rateLimits[key].filter(timestamp => now - timestamp < windowMs);
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
    // Target guide index links and back links
    const guideIndexEl = e.target.closest('.guide-index__link');
    const backLinkEl = e.target.closest('.guide-back__link');
    const el = guideIndexEl || backLinkEl;
    if (!el) return;

    // Different handling for guide links vs back links
    let id, title, href, eventType;
    
    if (guideIndexEl) {
      // Guide index link - existing logic
      id = el.dataset.guideId || (el.getAttribute('href') || '').split('/').pop();
      title = el.dataset.guideTitle || el.textContent.trim();
      href = el.getAttribute('href');
      eventType = 'guide_click';
    } else if (backLinkEl) {
      // Back link - track as navigation
      const backType = el.dataset.backType || 'unknown';
      id = `back_${backType}`;
      title = el.textContent.trim();
      href = el.getAttribute('href');
      eventType = 'guide_back_click';
    }

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
      const payload = JSON.stringify({ 
        guide_id: id, 
        guide_title: title, 
        href,
        event_type: eventType
      });

      // Use appropriate endpoint based on event type
      const endpoint = eventType === 'guide_back_click' ? '/analytics/guide-back-click' : '/analytics/guide-click';

      // Prefer sendBeacon so the request completes during navigation
      if (navigator.sendBeacon) {
        const blob = new Blob([payload], { type: 'application/json' });
        navigator.sendBeacon(endpoint, blob);
        console.log(`📊 Analytics beacon sent: ${id} (${eventType})`);
      } else {
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: payload,
          keepalive: true  // hint to allow during unload
        }).catch(() => {});
        console.log(`📊 Analytics fetch sent: ${id} (${eventType})`);
      }
    } else {
      console.log(`📊 Analytics rate limited for: ${id}`);
    }

    // Optional: also fire GA4
    if (window.gtag) {
      window.gtag('event', eventType, {
        event_category: eventType === 'guide_back_click' ? 'Navigation' : 'Guides',
        event_label: id,
        value: 1
      });
      console.log(`📈 GA4 event sent: ${eventType} for ${id}`);
    }

    // Don't prevent navigation - let the click go through
  });
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
          // Removed tooltip showing click count on hover
        }
      });
    });

    console.log('📈 Guide lists reordered by local popularity');
  } catch (error) {
    console.warn('Popularity reordering failed:', error);
  }
}

// ============================================================
// EXPORTS
// ============================================================

// Make functions available globally
window.Analytics = {
  initGuideTracking,
  initPopularityReordering,
  checkAnalyticsRateLimit
};