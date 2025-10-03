import { initPromoBanner } from './components/promoBanner.js';
import { initSiteBannerSearch } from './components/siteBannerSearch.js';
import { initHamburgerMenu } from './components/hamburgerMenu.js';
import { initHero } from './components/hero.js';
import { initBannerOffsets } from './components/bannerOffsets.js';
import { initGuideAnimations } from './components/guideAnimations.js';
import { initFooter } from './components/footer.js';

document.addEventListener('DOMContentLoaded', () => {
  // Component initialization with error handling
  const components = [
    { name: 'PromoBanner', init: initPromoBanner },
    { name: 'SiteBannerSearch', init: initSiteBannerSearch },
    { name: 'HamburgerMenu', init: initHamburgerMenu },
    { name: 'BannerOffsets', init: initBannerOffsets },
    { name: 'Hero', init: initHero },
    { name: 'GuideAnimations', init: initGuideAnimations },
    { name: 'Footer', init: initFooter }
  ];

  const failedComponents = [];
  
  components.forEach(({ name, init }) => {
    try {
      init();
    } catch (error) {
      failedComponents.push(name);
      
      // Report to analytics if available
      if (window.Analytics && window.Analytics.reportAnalyticsError) {
        window.Analytics.reportAnalyticsError(error, `component_init_${name.toLowerCase()}`);
      }
    }
  });
  
  // Analytics is now auto-initialized in analytics.js
  // No manual initialization needed here
});

// ============================================================
// ANALYTICS INTEGRATION
// Analytics system is auto-initialized in analytics.js and loaded via script tag.
// No manual initialization required here.
// 
// Available via window.Analytics:
// - Guide click tracking (auto-enabled)
// - Popularity reordering (auto-enabled) 
// - Rate limiting (built-in)
// - Error reporting (used above for component failures)
// - Privacy consent checking (built-in)
// ============================================================