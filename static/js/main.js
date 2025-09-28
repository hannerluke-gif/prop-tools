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
});

