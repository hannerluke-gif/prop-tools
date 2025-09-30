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
  
  // Analytics functions now in analytics.js (loaded via script tag)
  if (window.Analytics) {
    window.Analytics.initGuideTracking();      // client-side popularity tracking
    window.Analytics.initPopularityReordering(); // reorder guides by local click count
  }
});

// ============================================================
// ANALYTICS MOVED TO analytics.js
// All analytics functions have been consolidated in analytics.js
// This includes:
// - Google Analytics 4 setup
// - Guide click tracking
// - Rate limiting
// - Popularity reordering
// ============================================================