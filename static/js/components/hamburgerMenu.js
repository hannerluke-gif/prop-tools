/**
 * Initialize the Mobile Hamburger Menu Toggle logic.
 *
 * - Toggles `.menu-open` on the `.site-banner` at mobile widths
 * - Handles hamburger icon transformation to X
 * - Closes on outside click, ESC key, and resize to ≥ 768px
 * - Defensive reset when loaded on desktop
 * - Gracefully no-ops if root not found
 * - Idempotent: removes previously attached listeners on re-init
 *
 * @param {HTMLElement|null} [root=document.querySelector('.site-banner')] Root site banner element
 * @returns {() => void} teardown function to remove listeners
 */
export function initHamburgerMenu(root = document.querySelector('.site-banner')) {
	const banner = root;
	if (!banner) return () => {};

	// Idempotency: if previously initialized, tear it down first
	const TEARDOWN_KEY = '__hamburgerMenuTeardown__';
	if (banner[TEARDOWN_KEY]) {
		try { banner[TEARDOWN_KEY](); } catch {}
	}

	// Elements
	const hamburgerBtn = banner.querySelector('[data-hamburger-toggle]');
	const mobileMenu = banner.querySelector('.site-banner__mobile-menu');
	const MOBILE_BREAKPOINT = 768; // align with SCSS
	let isMenuOpen = false;

	// For idempotency, track and remove listeners on teardown
	const listeners = [];
	function on(el, evt, handler, opts) {
		if (!el) return;
		el.addEventListener(evt, handler, opts);
		listeners.push(() => el.removeEventListener(evt, handler, opts));
	}

	// Open mobile menu: only on mobile
	function openMenu() {
		if (window.innerWidth >= MOBILE_BREAKPOINT) return; // desktop: ignore
		if (isMenuOpen) return;
		banner.classList.add('menu-open');
		isMenuOpen = true;
		// Prevent body scroll when menu is open (CSP-compliant)
		document.body.classList.add('mobile-menu-open');
	}

	// Close mobile menu
	function closeMenu() {
		if (!isMenuOpen) return;
		banner.classList.remove('menu-open');
		isMenuOpen = false;
		// Restore body scroll (CSP-compliant)
		document.body.classList.remove('mobile-menu-open');
	}

	// Toggle menu state
	function toggleMenu() {
		if (isMenuOpen) {
			closeMenu();
		} else {
			openMenu();
		}
	}

	// Auto-close on desktop resize
	function handleResize() {
		if (window.innerWidth >= MOBILE_BREAKPOINT && isMenuOpen) {
			closeMenu();
		}
	}

	// Close on outside click (click outside menu area)
	function handleOutsideClick(event) {
		if (!isMenuOpen) return;
		
		// Don't close if clicking on hamburger button or menu content
		if (hamburgerBtn && hamburgerBtn.contains(event.target)) return;
		if (mobileMenu && mobileMenu.contains(event.target)) return;
		
		closeMenu();
	}

	// Close on ESC key
	function handleKeydown(event) {
		if (event.key === 'Escape' && isMenuOpen) {
			closeMenu();
		}
	}

	// Defensive reset on desktop load
	if (window.innerWidth >= MOBILE_BREAKPOINT) {
		closeMenu();
	}

	// Attach event listeners
	on(hamburgerBtn, 'click', toggleMenu);
	on(window, 'resize', handleResize);
	on(document, 'click', handleOutsideClick);
	on(document, 'keydown', handleKeydown);

	// Teardown function
	const teardown = () => {
		closeMenu(); // ensure clean state
		listeners.forEach(remove => remove());
		delete banner[TEARDOWN_KEY];
	};

	// Store teardown for idempotency
	banner[TEARDOWN_KEY] = teardown;
	return teardown;
}