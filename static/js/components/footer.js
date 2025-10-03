/**
 * Footer component - Dynamic reveal on scroll
 * Calculates footer height and reveals footer when scrolling near bottom
 */
export function initFooter() {
  const footer = document.querySelector('.site-footer');
  const main = document.querySelector('main');

  if (!footer || !main) {
    return;
  }

  let footerHeight = 0;
  let isScrolling = false;
  let isRevealed = false; // Track current reveal state to prevent flicker on mobile

  /**
   * Calculate footer height and set initial positioning
   */
  function updateFooterSpacing() {
    // Measure height without forcing a visual jump
    const newHeight = footer.offsetHeight;
    
    if (newHeight !== footerHeight) {
      footerHeight = newHeight;
      main.style.marginBottom = `${footerHeight}px`;
    }
    
    // Respect current reveal state (critical on mobile where resize fires during scroll)
    footer.style.bottom = isRevealed ? '0' : `-${footerHeight}px`;
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

      if (shouldReveal !== isRevealed) {
        isRevealed = shouldReveal;
        footer.style.bottom = isRevealed ? '0' : `-${footerHeight}px`;
      }
      isScrolling = false;
    });
  }

  // Initial setup
  updateFooterSpacing();
  // Initialize reveal state based on initial scroll position
  handleScroll();

  // Optimized event listeners
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    // Debounced resize: recompute height and re-apply current reveal state
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
