import { initPromoBanner } from './components/promoBanner.js';
import { initSiteBannerSearch } from './components/siteBannerSearch.js';
import { initHero } from './components/hero.js';

document.addEventListener('DOMContentLoaded', () => {
  initPromoBanner();        // looks for #promoBanner by default
  initSiteBannerSearch();   // looks for .site-banner by default
  initHero();               // populate hero slide 1 content
});

