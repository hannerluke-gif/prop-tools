/**
 * Footer Reveal Component
 * 
 * Creates a "theater curtain" effect where the page content lifts up
 * as the user scrolls down, revealing the footer underneath.
 * 
 * The effect activates when approaching the bottom of the page:
 * - Footer is fixed at bottom, behind content (z-index: 1)
 * - Page wrapper is above footer (z-index: 10)
 * - As user scrolls near bottom, page wrapper translates upward
 * - Creates illusion of curtain lifting to reveal footer
 */

export function initFooterReveal() {
  const footer = document.querySelector('.site-footer');
  const pageWrapper = document.querySelector('.page-content-wrapper');
  
  if (!footer || !pageWrapper) {
    console.warn('FooterReveal: Required elements not found');
    return;
  }

  // Get footer height for calculations
  const getFooterHeight = () => footer.offsetHeight;
  
  // Trigger distance: start revealing when this many pixels from bottom
  // Increased from 200 to 800 for slower, more gradual reveal
  const TRIGGER_OFFSET = 800;
  
  let footerHeight = getFooterHeight();
  let isRevealing = false;
  let rafId = null;

  /**
   * Calculate and apply the reveal transform
   */
  function updateReveal() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    // Distance from bottom of page
    const distanceFromBottom = documentHeight - (scrollTop + windowHeight);
    
    // Start revealing when within trigger distance
    if (distanceFromBottom <= TRIGGER_OFFSET) {
      // Calculate reveal progress (0 = start, 1 = fully revealed)
      const revealProgress = 1 - (distanceFromBottom / TRIGGER_OFFSET);
      const clampedProgress = Math.max(0, Math.min(1, revealProgress));
      
      // Translate page up by footer height * progress
      const translateY = -footerHeight * clampedProgress;
      pageWrapper.style.transform = `translateY(${translateY}px)`;
      
      if (!isRevealing) {
        pageWrapper.classList.add('footer-revealing');
        isRevealing = true;
      }
    } else {
      // Reset when scrolled away
      if (isRevealing) {
        pageWrapper.style.transform = '';
        pageWrapper.classList.remove('footer-revealing');
        isRevealing = false;
      }
    }
    
    rafId = null;
  }

  /**
   * Throttled scroll handler using requestAnimationFrame
   */
  function handleScroll() {
    if (rafId === null) {
      rafId = requestAnimationFrame(updateReveal);
    }
  }

  /**
   * Handle resize - recalculate footer height
   */
  function handleResize() {
    footerHeight = getFooterHeight();
    // Recalculate reveal on next frame
    if (rafId === null) {
      rafId = requestAnimationFrame(updateReveal);
    }
  }

  // Attach event listeners
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('resize', handleResize, { passive: true });

  // Initial check in case page loads near bottom
  updateReveal();

  console.log('FooterReveal: Initialized with footer height:', footerHeight);

  // Cleanup function (if needed for SPA scenarios)
  return () => {
    window.removeEventListener('scroll', handleScroll);
    window.removeEventListener('resize', handleResize);
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
    }
  };
}
