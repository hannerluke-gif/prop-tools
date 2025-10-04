// analytics.js - Complete analytics system
// Includes Google Analytics 4, guide click tracking, and popularity features

// ============================================================
// ANALYTICS CONFIGURATION
// ============================================================

const ANALYTICS_CONFIG = {
  GA_ID: 'G-ZEBP98J6ZQ',
  RATE_LIMIT: {
    WINDOW_MS: 60 * 1000, // 1 minute
    MAX_CLICKS: 3,
    CLEANUP_INTERVAL_MS: 5 * 60 * 1000 // 5 minutes
  },
  ENDPOINTS: {
    GUIDE_CLICK: '/analytics/guide-click',
    GUIDE_BACK_CLICK: '/analytics/guide-back-click'
  },
  SESSION_ID_PREFIX: 'sess_',
  STORAGE_KEYS: {
    SESSION_ID: 'analyticsSessionId',
    RATE_LIMIT: 'analyticsRateLimit',
    GUIDE_CLICKS: 'guideClicks',
    ANALYTICS_CONSENT: 'analytics_consent'
  }
};

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
gtag('config', ANALYTICS_CONFIG.GA_ID);

// Export gtag for use in other modules
window.gtag = gtag;

// ============================================================
// PRIVACY AND ERROR HANDLING UTILITIES
// ============================================================

/**
 * Check if user has given consent for analytics tracking
 * @returns {boolean} True if consent given or not required
 */
function hasAnalyticsConsent() {
  try {
    // Check for explicit consent
    const consent = localStorage.getItem(ANALYTICS_CONFIG.STORAGE_KEYS.ANALYTICS_CONSENT);
    // Default to true if no consent system is implemented yet
    // In production, you might want to default to false and require explicit consent
    return consent !== 'false';
  } catch (error) {
    // If localStorage is unavailable, default to no tracking
    reportAnalyticsError(error, 'consent_check');
    return false;
  }
}

/**
 * Report analytics errors to monitoring service
 * @param {Error} error - The error that occurred
 * @param {string} context - Context where the error occurred
 */
function reportAnalyticsError(error, context) {
  try {
    // Log to console for debugging
    console.warn(`Analytics Error [${context}]:`, error);
    
    // Send to GA4 as exception event if available
    if (window.gtag && hasAnalyticsConsent()) {
      gtag('event', 'exception', {
        description: `Analytics Error: ${context} - ${error.message}`,
        fatal: false
      });
    }
    
    // TODO: Add integration with error monitoring service (e.g., Sentry, LogRocket)
    // Example: Sentry.captureException(error, { tags: { context: 'analytics_' + context } });
  } catch (reportingError) {
    // Silently fail if error reporting itself fails
    console.warn('Failed to report analytics error:', reportingError);
  }
}

// ============================================================
// GUIDE ANALYTICS - Client-side popularity tracking
// ============================================================

/**
 * Clean up old rate limit entries
 */
function cleanupRateLimits() {
  try {
    const rateLimits = JSON.parse(localStorage.getItem(ANALYTICS_CONFIG.STORAGE_KEYS.RATE_LIMIT) || '{}');
    const now = Date.now();
    let hasChanges = false;

    Object.keys(rateLimits).forEach(key => {
      const originalLength = rateLimits[key].length;
      rateLimits[key] = rateLimits[key].filter(timestamp => now - timestamp < ANALYTICS_CONFIG.RATE_LIMIT.WINDOW_MS);
      
      if (rateLimits[key].length === 0) {
        delete rateLimits[key];
        hasChanges = true;
      } else if (rateLimits[key].length !== originalLength) {
        hasChanges = true;
      }
    });

    if (hasChanges) {
      localStorage.setItem(ANALYTICS_CONFIG.STORAGE_KEYS.RATE_LIMIT, JSON.stringify(rateLimits));
    }
  } catch (error) {
    reportAnalyticsError(error, 'rate_limit_cleanup');
  }
}

/**
 * Session-based rate limiting for analytics
 * Prevents rapid-fire clicking abuse using configured limits
 */
function checkAnalyticsRateLimit(guideId) {
  try {
    // Generate or retrieve session UUID
    let sessionId = localStorage.getItem(ANALYTICS_CONFIG.STORAGE_KEYS.SESSION_ID);
    if (!sessionId) {
      sessionId = ANALYTICS_CONFIG.SESSION_ID_PREFIX + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem(ANALYTICS_CONFIG.STORAGE_KEYS.SESSION_ID, sessionId);
    }

    // Get current rate limits
    const rateLimits = JSON.parse(localStorage.getItem(ANALYTICS_CONFIG.STORAGE_KEYS.RATE_LIMIT) || '{}');
    const now = Date.now();

    // Check current guide rate limit
    const limitKey = `${sessionId}:${guideId}`;
    const clicks = rateLimits[limitKey] || [];
    
    // Filter out old clicks (no need to clean all on every check now)
    const recentClicks = clicks.filter(timestamp => now - timestamp < ANALYTICS_CONFIG.RATE_LIMIT.WINDOW_MS);
    
    if (recentClicks.length >= ANALYTICS_CONFIG.RATE_LIMIT.MAX_CLICKS) {
      return false; // Rate limited
    }
    
    // Record this click
    recentClicks.push(now);
    rateLimits[limitKey] = recentClicks;
    localStorage.setItem(ANALYTICS_CONFIG.STORAGE_KEYS.RATE_LIMIT, JSON.stringify(rateLimits));
    
    return true; // Allow analytics
  } catch (error) {
    reportAnalyticsError(error, 'rate_limit_check');
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

    // Check for analytics consent first
    if (!hasAnalyticsConsent()) {
      return; // Don't track if no consent
    }

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
      const clicks = JSON.parse(localStorage.getItem(ANALYTICS_CONFIG.STORAGE_KEYS.GUIDE_CLICKS) || '{}');
      clicks[id] = (clicks[id] || 0) + 1;
      localStorage.setItem(ANALYTICS_CONFIG.STORAGE_KEYS.GUIDE_CLICKS, JSON.stringify(clicks));
    } catch (error) {
      // Handle localStorage errors (private browsing, etc.)
      reportAnalyticsError(error, 'guide_tracking_localStorage');
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
      const endpoint = eventType === 'guide_back_click' 
        ? ANALYTICS_CONFIG.ENDPOINTS.GUIDE_BACK_CLICK 
        : ANALYTICS_CONFIG.ENDPOINTS.GUIDE_CLICK;

      // Prefer sendBeacon so the request completes during navigation
      if (navigator.sendBeacon) {
        const blob = new Blob([payload], { type: 'application/json' });
        navigator.sendBeacon(endpoint, blob);
      } else {
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: payload,
          keepalive: true  // hint to allow during unload
        }).catch((error) => {
          reportAnalyticsError(error, 'analytics_fetch');
        });
      }
    }

    // Optional: also fire GA4
    if (window.gtag) {
      window.gtag('event', eventType, {
        event_category: eventType === 'guide_back_click' ? 'Navigation' : 'Guides',
        event_label: id,
        value: 1
      });
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
  
  // Only reorder if user has consented to analytics
  if (!hasAnalyticsConsent()) return;

  try {
    const clicks = JSON.parse(localStorage.getItem(ANALYTICS_CONFIG.STORAGE_KEYS.GUIDE_CLICKS) || '{}');
    
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
  } catch (error) {
    reportAnalyticsError(error, 'popularity_reordering');
  }
}

// ============================================================
// INITIALIZATION AND EXPORTS
// ============================================================

// Set up periodic cleanup for rate limits
let cleanupInterval;

/**
 * Initialize the analytics system
 */
function initAnalytics() {
  // Set up periodic cleanup (only if not already running)
  if (!cleanupInterval) {
    cleanupInterval = setInterval(cleanupRateLimits, ANALYTICS_CONFIG.RATE_LIMIT.CLEANUP_INTERVAL_MS);
    
    // Clean up interval on page unload
    window.addEventListener('beforeunload', () => {
      if (cleanupInterval) {
        clearInterval(cleanupInterval);
        cleanupInterval = null;
      }
    });
  }
  
  // Initialize tracking and popularity features
  initGuideTracking();
  initPopularityReordering();
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAnalytics);
} else {
  initAnalytics();
}

// Make functions available globally
window.Analytics = {
  initGuideTracking,
  initPopularityReordering,
  checkAnalyticsRateLimit,
  hasAnalyticsConsent,
  reportAnalyticsError,
  cleanupRateLimits,
  initAnalytics,
  config: ANALYTICS_CONFIG
};