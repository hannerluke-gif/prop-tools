// static/js/components/hero.js
/**
 * Initialize hero carousel with 3 slides: auto-rotation, keyboard nav, touch swipe,
 * and disabled CTAs until ctaHref is provided.
 * Safely no-ops if .hero is missing.
 */
export function initHero() {
  const hero = document.querySelector('.hero');
  if (!hero) return;

  // Prevent duplicate initialization
  if (hero.hasAttribute('data-hero-initialized')) return;
  hero.setAttribute('data-hero-initialized', 'true');

  const slides = hero.querySelectorAll('.hero-slide[data-slide-id]');
  const dotsContainer = hero.querySelector('.hero__dots');
  const prevArrow = hero.querySelector('.hero__arrow--prev');
  const nextArrow = hero.querySelector('.hero__arrow--next');

  // Dynamic (nonced) stylesheet for CSP-safe background-image injection
  const dynStyleEl = document.getElementById('dyn-styles');
  const dynSheet = dynStyleEl?.sheet;
  const insertedRules = new Set();

  function ensureRule(selector, declarations) {
    if (!dynSheet) return; // fail-soft if stylesheet missing
    const cleaned = declarations.trim().replace(/\s+/g, ' ');
    const sig = `${selector}{${cleaned}}`;
    if (insertedRules.has(sig)) return;
    try {
      dynSheet.insertRule(sig, dynSheet.cssRules.length);
      insertedRules.add(sig);
    } catch (err) {
      // CSS rule insertion failed, but continue silently
    }
  }

  function toClassToken(str) {
    return String(str).toLowerCase().replace(/[^a-z0-9_-]+/g, '-');
  }

  function cssUrl(u) {
    const safe = String(u).replace(/"/g, '\\"');
    return `"${safe}"`;
  }

  function applyHeroBackground(slideEl, slideId, imagePath) {
    if (!imagePath) return;
    const token = toClassToken(slideId || 'slide');
    const cls = `hero-bg-${token}`;
    slideEl.classList.add(cls);
    const decl = `background-image: url(${cssUrl(imagePath)}),\n                           linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.85) 88%),\n                           ${getGradientForSlide(slideId)};`;
    ensureRule(`.hero .hero-slide.${cls}`, decl);
  }

  // Optional: programmatic arbitrary zoom percentages (only if needed by data-zoom numeric values)
  function ensureZoomRule(zoom) {
    if (!zoom) return;
    // accept either numeric like 1.12 or string tokens
    const num = parseFloat(zoom);
    if (!isFinite(num)) return;
    const pct = Math.round(num * 100);
    ensureRule(`.hero .hero-slide[data-zoom="${zoom}"]::not(.legacy)`, `/* zoom preset */`); // placeholder no-op to mark presence
    ensureRule(`.hero .hero-slide[data-zoom="${zoom}"].is-active`, `background-size: ${pct}% auto;`);
  }

  if (slides.length === 0) return;

  let slidesData = {};
  let currentSlideIndex = 0;
  let autoRotateTimer = null;
  let isTransitioning = false;
  const ROTATION_INTERVAL = 6000; // 6 seconds
  const TRANSITION_DURATION = 570; // match SCSS ~520ms + small buffer (ms)

  // Fallback content for each slide type
  const fallbackContent = {
    'top-pick': {
      headline: 'Skip the Research. Start Trading.',
      subline: 'We compared drawdowns, targets, and fees—these picks win today.',
      ctaLabel: 'See Top Picks'
    },
    'accounts': {
      headline: 'Find the Account Built for You',
      subline: 'Match drawdown, profit target, & rules to your style.',
      ctaLabel: 'Find My Match'
    },
    'discount': {
      headline: 'Today\'s Best Promo Codes',
      subline: 'Save on eval or straight-to-funded accounts.',
      ctaLabel: 'See Discounts'
    }
  };

  /**
   * Populate slide content from data or fallback
   */
  function populateSlide(slideEl, slideData, slideId, metaData = {}) {
    const headlineEl = slideEl.querySelector('.hero-headline');
    const sublineEl = slideEl.querySelector('.hero-subline');
    const ctaEl = slideEl.querySelector('.hero-cta');
    const fallback = fallbackContent[slideId] || {};

    if (headlineEl) {
      headlineEl.textContent = slideData?.headline || fallback.headline || '';
    }
    if (sublineEl) {
      sublineEl.textContent = slideData?.subline || fallback.subline || '';
    }
    if (ctaEl) {
      ctaEl.textContent = slideData?.ctaLabel || fallback.ctaLabel || 'Learn More';
      // Always enable CTA; default to /not-found if missing
      const ctaHref = (slideData?.ctaHref && String(slideData.ctaHref).trim() !== '') ? slideData.ctaHref : '/not-found';
      ctaEl.href = ctaHref;
      ctaEl.removeAttribute('aria-disabled');
      ctaEl.removeAttribute('tabindex');
      ctaEl.classList.remove('is-disabled');
    }

    // Handle dynamic background image and zoom effect
    if (slideData) {
      const imageBasePath = metaData.imageBasePath || '/static/img/slide/';
      // Normalize paths to avoid duplicated segments like 'slide/slide' or double slashes
      let imagePath = '';
      if (slideData.image) {
        const img = String(slideData.image);
        if (img.startsWith('/') || img.startsWith('http')) {
          imagePath = img; // absolute path or URL
        } else {
          const base = String(imageBasePath).replace(/\/+$|\/+/g, '/').replace(/\/$/, '');
          const name = img.replace(/^\/+/, '');
          imagePath = `${base}/${name}`;
        }
      }
      const zoom = slideData.zoom || 'in';
      if (imagePath) {
        applyHeroBackground(slideEl, slideId, imagePath);
        slideEl.setAttribute('data-zoom', zoom);
        ensureZoomRule(zoom); // optional generation of zoom rule for numeric zoom values
      }
    }
  }

  /**
   * Get gradient background for slide based on ID
   */
  function getGradientForSlide(slideId) {
    const gradients = {
      'top-pick': `
        radial-gradient(circle at 25% 15%, rgba(139,92,246,0.38), transparent 58%),
        radial-gradient(circle at 85% 25%, rgba(34,211,238,0.3), transparent 62%),
        linear-gradient(120deg, #181824 0%, #232347 100%)
      `,
      'accounts': `
        radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.32), transparent 60%),
        radial-gradient(circle at 80% 30%, rgba(236, 72, 153, 0.28), transparent 64%),
        linear-gradient(120deg, #1a1b26 0%, #202a3a 100%)
      `,
      'discount': `
        radial-gradient(circle at 22% 18%, rgba(16, 185, 129, 0.32), transparent 60%),
        radial-gradient(circle at 78% 28%, rgba(250, 204, 21, 0.26), transparent 64%),
        linear-gradient(120deg, #161b1d 0%, #1d252a 100%)
      `
    };
    
    return gradients[slideId] || gradients['top-pick'];
  }

  /**
   * Create dots for navigation
   */
  function createDots() {
    if (!dotsContainer) return;

    // Remove only existing dot elements so arrow buttons (if present)
    // inside the container are preserved.
    const existingDots = dotsContainer.querySelectorAll('.hero__dot');
    existingDots.forEach(d => d.remove());

    slides.forEach((_, index) => {
      const dot = document.createElement('button');
      dot.className = 'hero__dot';
      dot.type = 'button';
      dot.setAttribute('role', 'tab');
      dot.setAttribute('aria-label', `Go to slide ${index + 1}`);
      dot.addEventListener('click', () => goToSlide(index));

      // Insert dots before the next arrow so they appear between the
      // prev/next arrows when those buttons are children of the container.
      const nextBtn = dotsContainer.querySelector('.hero__arrow--next');
      if (nextBtn) {
        dotsContainer.insertBefore(dot, nextBtn);
      } else {
        dotsContainer.appendChild(dot);
      }
    });
  }

  /**
   * Update active slide and dots
   */
  function updateActiveSlide() {
    // Update slide classes for the currently active slide only.
    // Do NOT clear `.is-exiting` here — leaving that to the transition
    // timeout allows outgoing slides to animate out smoothly.
    slides.forEach((slide, index) => {
      if (index === currentSlideIndex) {
        slide.classList.add('is-active');
        slide.setAttribute('aria-current', 'true');
      } else {
        slide.classList.remove('is-active');
        slide.removeAttribute('aria-current');
      }
    });

    if (dotsContainer) {
      const dots = dotsContainer.querySelectorAll('.hero__dot');
      dots.forEach((dot, index) => {
        if (index === currentSlideIndex) {
          dot.classList.add('is-active');
          dot.setAttribute('aria-selected', 'true');
          dot.setAttribute('aria-current', 'true');
        } else {
          dot.classList.remove('is-active');
          dot.setAttribute('aria-selected', 'false');
          dot.removeAttribute('aria-current');
        }
      });
    }
  }

  /**
   * Go to specific slide
   */
  function goToSlide(index) {
    if (index < 0 || index >= slides.length) return;
    if (isTransitioning || index === currentSlideIndex) return;

    // Mark transitioning to prevent rapid-fire navigation
    isTransitioning = true;

    const leavingIndex = currentSlideIndex;
    const enteringIndex = index;
    const leavingSlide = slides[leavingIndex];
    const enteringSlide = slides[enteringIndex];

    // Add exiting class to current slide so it animates out (SCSS handles .is-exiting)
    if (leavingSlide) {
      leavingSlide.classList.add('is-exiting');
      leavingSlide.classList.remove('is-active');
      leavingSlide.removeAttribute('aria-current');
    }

    // Prepare entering slide: ensure it's present and then activate
    if (enteringSlide) {
      enteringSlide.classList.remove('is-exiting');
      // Force a reflow so the browser registers the class changes and transition runs
      // eslint-disable-next-line no-unused-expressions
      enteringSlide.offsetHeight; // read to flush
      enteringSlide.classList.add('is-active');
      enteringSlide.setAttribute('aria-current', 'true');
    }

    // Update index and reset timer
    currentSlideIndex = enteringIndex;
  // Update dots/aria for the newly active slide
  updateActiveSlide();
    // Also directly ensure the dot is toggled here as a fallback
    if (dotsContainer) {
      const dots = dotsContainer.querySelectorAll('.hero__dot');
      if (dots && dots.length === slides.length) {
        dots.forEach((d, i) => {
          if (i === currentSlideIndex) d.classList.add('is-active'); else d.classList.remove('is-active');
        });
      }
    }
    resetAutoRotation();

    // After transition duration, clear exiting state and allow navigation
    setTimeout(() => {
      if (leavingSlide) {
        leavingSlide.classList.remove('is-exiting');
      }
      isTransitioning = false;
    }, TRANSITION_DURATION);
  }

  /**
   * Navigate to next slide
   */
  function nextSlide() {
    const nextIndex = (currentSlideIndex + 1) % slides.length;
    goToSlide(nextIndex);
  }

  /**
   * Navigate to previous slide
   */
  function prevSlide() {
    const prevIndex = (currentSlideIndex - 1 + slides.length) % slides.length;
    goToSlide(prevIndex);
  }

  /**
   * Start auto-rotation
   */
  function startAutoRotation() {
    autoRotateTimer = setInterval(nextSlide, ROTATION_INTERVAL);
  }

  /**
   * Stop auto-rotation
   */
  function stopAutoRotation() {
    if (autoRotateTimer) {
      clearInterval(autoRotateTimer);
      autoRotateTimer = null;
    }
  }

  /**
   * Reset auto-rotation (restart the timer)
   */
  function resetAutoRotation() {
    stopAutoRotation();
    startAutoRotation();
  }

  /**
   * Handle keyboard navigation
   */
  function handleKeyboard(event) {
    if (!hero.contains(event.target)) return;

    switch (event.key) {
      case 'ArrowLeft':
        event.preventDefault();
        prevSlide();
        break;
      case 'ArrowRight':
        event.preventDefault();
        nextSlide();
        break;
      case 'Home':
        event.preventDefault();
        goToSlide(0);
        break;
      case 'End':
        event.preventDefault();
        goToSlide(slides.length - 1);
        break;
    }
  }

  /**
   * Handle touch/swipe gestures
   */
  function setupTouchHandlers() {
    let startX = 0;
    let startY = 0;
    let isMoving = false;

    hero.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      isMoving = false;
    }, { passive: true });

    hero.addEventListener('touchmove', (e) => {
      isMoving = true;
    }, { passive: true });

    hero.addEventListener('touchend', (e) => {
      if (!isMoving) return;

      const endX = e.changedTouches[0].clientX;
      const endY = e.changedTouches[0].clientY;
      const deltaX = endX - startX;
      const deltaY = endY - startY;

      // Only handle horizontal swipes (ignore vertical)
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          prevSlide(); // Swipe right = previous
        } else {
          nextSlide(); // Swipe left = next
        }
      }
    }, { passive: true });
  }

  /**
   * Load slides data and initialize carousel
   */
  function initializeCarousel() {
    // First, populate with fallback content to avoid empty slides
    slides.forEach((slideEl, index) => {
      const slideId = slideEl.getAttribute('data-slide-id');
      if (slideId && fallbackContent[slideId]) {
        populateSlide(slideEl, null, slideId);
      }
    });

    // Then try to load from JSON
    fetch('/static/data/slides.json', { cache: 'no-cache' })
      .then(res => res.ok ? res.json() : Promise.reject(new Error('Failed to load slides.json')))
      .then(json => {
        if (json.slides && Array.isArray(json.slides)) {
          // Index slides by ID for easy lookup
          json.slides.forEach(slide => {
            if (slide.id) {
              slidesData[slide.id] = slide;
            }
          });

          // Re-populate slides with JSON data, including meta information
          slides.forEach((slideEl) => {
            const slideId = slideEl.getAttribute('data-slide-id');
            if (slideId && slidesData[slideId]) {
              populateSlide(slideEl, slidesData[slideId], slideId, json.meta || {});
            }
          });
        }
      })
      .catch((error) => {
        console.warn('Failed to load slides data, using fallback content:', error);
      });

    // Set up carousel UI and behavior
    createDots();
    updateActiveSlide();
    startAutoRotation();
    setupTouchHandlers();

    // Arrow navigation
    if (prevArrow) {
      prevArrow.addEventListener('click', prevSlide);
    }
    if (nextArrow) {
      nextArrow.addEventListener('click', nextSlide);
    }

    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboard);
  }

  // Initialize everything
  initializeCarousel();
}
