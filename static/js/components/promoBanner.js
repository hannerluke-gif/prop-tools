/**
 * Initialize the promo banner rotation logic.
 *
 * - Auto-rotates with slight randomized delay (4.5s–6s)
 * - Hover pause on fine pointers
 * - Click/tap advances to next and restarts timer
 * - Loads promos from /static/data/promos.json and updates text + CTA
 * - Gracefully no-ops if root or required elements are missing
 * - Idempotent: can be called multiple times; previous timers/listeners are cleaned up
 *
 * @param {HTMLElement|null} [root=document.getElementById('promoBanner')] Root banner element
 * @returns {() => void} teardown function to remove listeners and timers
 */
export function initPromoBanner(root = document.getElementById('promoBanner')) {
	const banner = root;
	if (!banner) return () => {};

	// Idempotency: if previously initialized, tear it down first
	const TEARDOWN_KEY = '__promoBannerTeardown__';
	if (banner[TEARDOWN_KEY]) {
		try { banner[TEARDOWN_KEY](); } catch {}
	}

	// Elements
	const slides = Array.from(banner.querySelectorAll('.promo-banner__slide'));
	const primaryLine = banner.querySelector('.promo-banner__line--primary');
	const secondaryLine = banner.querySelector('.promo-banner__line--secondary');

		if (!slides.length || !primaryLine || !secondaryLine) {
		return () => {};
	}

		if (slides.length <= 1) {
			// Nothing to rotate; keep original behavior: no fetch, no bindings.
			return () => {};
		}

	// State
	let current = 0;
	let timerId = null;
	const baseInterval = 4500; // ms
	let promos = [];

	// For idempotency, ensure we don't attach duplicate listeners if re-initialized
	// We'll attach listeners and return a cleanup that removes them.
	const listeners = [];

	function on(el, evt, handler, opts) {
		if (!el) return;
		el.addEventListener(evt, handler, opts);
		listeners.push(() => el.removeEventListener(evt, handler, opts));
	}

	// Fetch promos.json, returning an array (or empty array on error)
	function fetchPromos() {
		return fetch('/static/data/promos.json')
			.then(r => (r.ok ? r.json() : Promise.resolve([])))
			.catch(() => []);
	}

	// Update the text lines for the given slide index
	function updateTextForSlide(index) {
		const promo = promos[index] || {};
		const firm = promo.firm || '';
		const pct = promo.discount_pct || '';

		// Mobile: two lines. Desktop: inline single line.
		const isMobile = window.matchMedia('(max-width: 540px)').matches;

		if (isMobile) {
			// Line 1: "Firm • 20% OFF"
			primaryLine.textContent = firm ? `${firm} • ${pct} OFF` : '';
			// Line 2: "Use code MAXX"
			secondaryLine.textContent = 'Use code MAXX';
		} else {
			// Single line: "Firm • 20% OFF • Use code MAXX"
			primaryLine.textContent = firm ? `${firm} • ${pct} OFF • Use code MAXX` : '';
			secondaryLine.textContent = '';
		}
	}

	// Set the active slide by index, updating classes and text
	function setActive(index) {
		slides.forEach((el, i) => {
			if (i === index) {
				el.classList.add('is-active');
			} else {
				el.classList.remove('is-active');
			}
		});
		updateTextForSlide(index);
	}

	// Advance to next slide, optionally restarting timer if manual
	function nextSlide(manual = false) {
		current = (current + 1) % slides.length;
		setActive(current);
		if (manual) restartTimer();
	}

	// Timer logic with slight randomization to avoid robotic feel
	function startTimer() {
		const variance = Math.random() * 1500; // 0–1.5s
		const delay = baseInterval + variance; // 4.5s–6s
		timerId = window.setTimeout(() => {
			nextSlide();
			startTimer();
		}, delay);
	}

	function stopTimer() {
		if (timerId) {
			clearTimeout(timerId);
			timerId = null;
		}
	}

	function restartTimer() {
		stopTimer();
		startTimer();
	}

	// Click / tap advance
	on(banner, 'click', () => {
		nextSlide(true);
	});

	// Hover pause (desktop only: use matchMedia to detect coarse pointers)
	const prefersCoarse = window.matchMedia('(pointer: coarse)').matches;
	if (!prefersCoarse) {
		on(banner, 'mouseenter', stopTimer);
		on(banner, 'mouseleave', restartTimer);
	}

	// Initialize
	setActive(current);

	// load promos.json and start timer after initial text render
	fetchPromos().then(data => {
		promos = Array.isArray(data) ? data : [];
		updateTextForSlide(current);
		startTimer();

		// Populate CTA hrefs and prevent banner-advance on CTA click
		const cta = document.getElementById('promoBannerCta');
		if (cta) {
			function updateCtaFor(index) {
				const promo = promos[index] || {};
				const href = promo.source || promo.details_url || '';
				if (href) {
					cta.setAttribute('href', href);
					cta.setAttribute('target', '_blank');
					cta.setAttribute('rel', 'noopener noreferrer');
					cta.removeAttribute('aria-hidden');
					if (cta.hasAttribute('role')) cta.removeAttribute('role');
					if (cta.hasAttribute('data-href')) cta.removeAttribute('data-href');
				} else {
					if (cta.hasAttribute('href')) cta.removeAttribute('href');
					cta.setAttribute('aria-hidden', 'true');
				}
			}
			updateCtaFor(current);
			const origUpdateText = updateTextForSlide;
			// Wrap updateTextForSlide to also update CTA in lockstep
			const wrappedUpdate = function(index) {
				origUpdateText(index);
				updateCtaFor(index);
			};
			// Replace function reference used inside module scope
			updateTextForSlide = wrappedUpdate;

			on(cta, 'click', function(e) {
				e.stopPropagation();
			});
		}
	});

	// Teardown that clears timers and removes listeners
		const teardown = function teardown() {
		stopTimer();
		while (listeners.length) {
			const off = listeners.pop();
			try { off && off(); } catch {}
		}
		};

		// Store teardown on element for future re-inits
		try { banner[TEARDOWN_KEY] = teardown; } catch {}
		return teardown;
}

