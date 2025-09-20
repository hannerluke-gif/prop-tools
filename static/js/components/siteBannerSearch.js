/**
 * Initialize the Site Banner Mobile Search Toggle logic.
 *
 * - Toggles `.is-searching` on the `.site-banner` at mobile widths
 * - Focuses input on open
 * - Closes on ESC, outside click, and resize to ≥ 768px
 * - Defensive reset when loaded on desktop
 * - Gracefully no-ops if root not found
 * - Idempotent: removes previously attached listeners on re-init
 *
 * @param {HTMLElement|null} [root=document.querySelector('.site-banner')] Root site banner element
 * @returns {() => void} teardown function to remove listeners
 */
export function initSiteBannerSearch(root = document.querySelector('.site-banner')) {
	const banner = root;
	if (!banner) return () => {};

	// Idempotency: if previously initialized, tear it down first
	const TEARDOWN_KEY = '__siteBannerSearchTeardown__';
	if (banner[TEARDOWN_KEY]) {
		try { banner[TEARDOWN_KEY](); } catch {}
	}

	// Elements
	const toggleBtn = banner.querySelector('[data-site-banner-toggle]');
	const searchInputs = banner.querySelectorAll('.site-banner__input');
	const MOBILE_BREAKPOINT = 768; // align with SCSS
	let isSearching = false;

	// For idempotency, track and remove listeners on teardown
	const listeners = [];
	function on(el, evt, handler, opts) {
		if (!el) return;
		el.addEventListener(evt, handler, opts);
		listeners.push(() => el.removeEventListener(evt, handler, opts));
	}

	// Open search mode: only on mobile
	function openSearch() {
		if (window.innerWidth >= MOBILE_BREAKPOINT) return; // desktop: ignore
		if (isSearching) return;
		banner.classList.add('is-searching');
		isSearching = true;
		// focus first available search input in mobile search container
		const mobileSearch = banner.querySelector('.site-banner__mobile-search .site-banner__input');
		window.requestAnimationFrame(() => {
			(mobileSearch || searchInputs[0])?.focus();
		});
	}

	// Close search mode
	function closeSearch() {
		if (!isSearching) return;
		banner.classList.remove('is-searching');
		isSearching = false;
	}

	// Toggle button click
	function handleToggleClick(e) {
		e.preventDefault();
		if (isSearching) {
			closeSearch();
		} else {
			openSearch();
		}
	}

	// Outside click: only when in searching mode and on mobile
	function handleDocumentClick(e) {
		if (!isSearching) return;
		if (window.innerWidth >= MOBILE_BREAKPOINT) return; // desktop resets separately
		if (banner.contains(e.target)) return; // inside banner
		closeSearch();
	}

	// ESC key: only when in searching mode
	function handleKeydown(e) {
		if (e.key === 'Escape') {
			closeSearch();
		}
	}

	// Debounced resize: exit search mode once at desktop size
	let resizeTimer = null;
	function handleResize() {
		if (resizeTimer) clearTimeout(resizeTimer);
		resizeTimer = setTimeout(() => {
			if (window.innerWidth >= MOBILE_BREAKPOINT) {
				closeSearch();
			}
		}, 120);
	}

	// Bind events
	if (toggleBtn) on(toggleBtn, 'click', handleToggleClick);
	on(document, 'click', handleDocumentClick);
	on(document, 'keydown', handleKeydown);
	on(window, 'resize', handleResize);

	// Defensive: if loaded already on desktop ensure clean state
	if (window.innerWidth >= MOBILE_BREAKPOINT) {
		banner.classList.remove('is-searching');
		isSearching = false;
	}

	// Teardown removes listeners
		const teardown = function teardown() {
		while (listeners.length) {
			const off = listeners.pop();
			try { off && off(); } catch {}
		}
		};
		try { banner[TEARDOWN_KEY] = teardown; } catch {}
		return teardown;
}

