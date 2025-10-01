import { initPromoBanner } from './components/promoBanner.js';
import { initSiteBannerSearch } from './components/siteBannerSearch.js';
import { initHamburgerMenu } from './components/hamburgerMenu.js';
import { initHero } from './components/hero.js';
import { initBannerOffsets } from './components/bannerOffsets.js';
import { initGuideAnimations } from './components/guideAnimations.js';

document.addEventListener('DOMContentLoaded', () => {
  // Component initialization with error handling
  const components = [
    { name: 'PromoBanner', init: initPromoBanner },
    { name: 'SiteBannerSearch', init: initSiteBannerSearch },
    { name: 'HamburgerMenu', init: initHamburgerMenu },
    { name: 'BannerOffsets', init: initBannerOffsets },
    { name: 'Hero', init: initHero },
    { name: 'GuideAnimations', init: initGuideAnimations }
  ];

  const failedComponents = [];
  
  components.forEach(({ name, init }) => {
    try {
      init();
      console.log(`✅ ${name} initialized successfully`);
    } catch (error) {
      console.error(`❌ Failed to initialize ${name}:`, error);
      failedComponents.push(name);
      
      // Report to analytics if available
      if (window.Analytics && window.Analytics.reportAnalyticsError) {
        window.Analytics.reportAnalyticsError(error, `component_init_${name.toLowerCase()}`);
      }
    }
  });

  // Log initialization summary
  if (failedComponents.length === 0) {
    console.log('🚀 All components initialized successfully');
  } else {
    console.warn(`⚠️ ${failedComponents.length} component(s) failed to initialize: ${failedComponents.join(', ')}`);
  }
  
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