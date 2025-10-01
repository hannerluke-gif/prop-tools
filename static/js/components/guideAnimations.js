// static/js/components/guideAnimations.js
/**
 * Light-touch scroll animations for guide pages
 * Uses IntersectionObserver to trigger fade/slide animations
 * when elements enter the viewport.
 * 
 * Respects prefers-reduced-motion for accessibility.
 * Safely no-ops if no animation-ready elements exist.
 */

export function initGuideAnimations() {
  // Check if user prefers reduced motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  if (prefersReducedMotion) {
    // Make all animation-ready elements visible immediately
    const elements = document.querySelectorAll('.animation-ready');
    elements.forEach(el => {
      el.classList.remove('animation-ready');
      el.style.opacity = '1';
    });
    return;
  }

  // Find all elements marked for animation
  const animationElements = document.querySelectorAll('.animation-ready');
  
  if (animationElements.length === 0) {
    return; // No elements to animate, exit early
  }

  // Intersection Observer options
  const observerOptions = {
    root: null, // Use viewport as root
    rootMargin: '0px 0px -100px 0px', // Trigger slightly before element fully enters viewport
    threshold: 0.1 // Trigger when 10% of element is visible
  };

  // Callback when elements intersect
  const observerCallback = (entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const element = entry.target;
        
        // Add animation-active class to trigger animation
        element.classList.add('animation-active');
        
        // Unobserve after animation to prevent re-triggering
        observer.unobserve(element);
      }
    });
  };

  // Create the observer
  const observer = new IntersectionObserver(observerCallback, observerOptions);

  // Observe all animation-ready elements
  animationElements.forEach(element => {
    observer.observe(element);
  });

  // Cleanup function (useful for SPA navigation, though not needed for current setup)
  return () => {
    observer.disconnect();
  };
}
