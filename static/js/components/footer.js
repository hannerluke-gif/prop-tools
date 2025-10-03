/**
 * Footer component - Dynamic reveal on scroll
 * Calculates footer height and reveals footer when scrolling near bottom
 */
export function initFooter() {
  const footer = document.querySelector('.site-footer');
  const main = document.querySelector('main');

  if (!footer || !main) {
    console.warn('Footer or main element not found');
    return;
  }

  let footerHeight = 0;
  let isScrolling = false;

  /**
   * Calculate footer height and set initial positioning
   */
  function updateFooterSpacing() {
    // Force a reflow to get accurate height measurement
    footer.style.bottom = '0';
    const newHeight = footer.offsetHeight;
    
    if (newHeight !== footerHeight) {
      footerHeight = newHeight;
      main.style.marginBottom = `${footerHeight}px`;
      console.log(`Footer height updated: ${footerHeight}px`);
    }
    
    // Initially hide the footer
    footer.style.bottom = `-${footerHeight}px`;
  }

  /**
   * Handle scroll-based footer reveal with better performance
   */
  function handleScroll() {
    if (isScrolling) return;
    
    isScrolling = true;
    requestAnimationFrame(() => {
      const scrollY = window.scrollY || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // Calculate distance from bottom
      const distanceFromBottom = documentHeight - (scrollY + windowHeight);
      
      // Reveal footer when within footer height of bottom, or if scrolled past threshold
      const shouldReveal = distanceFromBottom <= footerHeight || scrollY > 100;
      
      footer.style.bottom = shouldReveal ? '0' : `-${footerHeight}px`;
      isScrolling = false;
    });
  }

  // Initial setup
  updateFooterSpacing();

  // Optimized event listeners
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(updateFooterSpacing, 150);
  }, { passive: true });

  window.addEventListener('scroll', handleScroll, { passive: true });
  
  // Handle late-loading content that might affect footer height
  window.addEventListener('load', updateFooterSpacing);
  
  // Handle font loading which can affect height
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(updateFooterSpacing);
  }
}
