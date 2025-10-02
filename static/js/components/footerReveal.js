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

  // Force scroll to top on page load to prevent browser scroll restoration issues
  // This prevents mobile browsers from jumping to previous scroll position
  window.scrollTo(0, 0);

  // Get footer height for calculations
  const getFooterHeight = () => footer.offsetHeight;
  
  // Trigger distance: start revealing when this many pixels from bottom
  // Responsive: smaller offset on mobile to avoid premature triggering
  const isMobile = window.innerWidth < 768;
  const TRIGGER_OFFSET = isMobile ? 400 : 800;
  
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
    
    // Only activate reveal if page is actually scrollable beyond one viewport
    // This prevents footer from showing on pages with minimal content
    const hasScrollableContent = documentHeight > windowHeight + footerHeight;
    
    if (!hasScrollableContent) {
      // Page too short - keep footer hidden, no reveal effect
      if (isRevealing) {
        pageWrapper.classList.remove('footer-reveal-active');
        pageWrapper.style.removeProperty('--footer-reveal-offset');
        pageWrapper.classList.remove('footer-revealing');
        isRevealing = false;
      }
      rafId = null;
      return;
    }
    
    // Distance from bottom of page
    const distanceFromBottom = documentHeight - (scrollTop + windowHeight);
    
    // Start revealing when within trigger distance
    if (distanceFromBottom <= triggerOffset) {
      // Calculate reveal progress (0 = start, 1 = fully revealed)
      const revealProgress = 1 - (distanceFromBottom / triggerOffset);
      const clampedProgress = Math.max(0, Math.min(1, revealProgress));
      
      // Translate page up by footer height * progress
      const translateY = -footerHeight * clampedProgress;
      
      // CSP-compliant: Use CSS custom property instead of inline style
      pageWrapper.style.setProperty('--footer-reveal-offset', `translateY(${translateY}px)`);
      pageWrapper.classList.add('footer-reveal-active');
      
      if (!isRevealing) {
        pageWrapper.classList.add('footer-revealing');
        isRevealing = true;
      }
    } else {
      // Reset when scrolled away
      if (isRevealing) {
        pageWrapper.classList.remove('footer-reveal-active');
        pageWrapper.style.removeProperty('--footer-reveal-offset');
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
   * Handle resize - recalculate footer height and trigger offset
   */
  let triggerOffset = isMobile ? 400 : 800;
  
  function handleResize() {
    footerHeight = getFooterHeight();
    // Update trigger offset based on new viewport width
    const nowMobile = window.innerWidth < 768;
    triggerOffset = nowMobile ? 400 : 800;
    // Recalculate reveal on next frame
    if (rafId === null) {
      rafId = requestAnimationFrame(updateReveal);
    }
  }

  // Attach event listeners
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('resize', handleResize, { passive: true });

  // Initial check after a brief delay to ensure DOM is fully rendered
  // This prevents premature reveal on page load
  setTimeout(() => {
    updateReveal();
  }, 100);

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
