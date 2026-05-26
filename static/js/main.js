/**
 * main.js — JKR International
 * Core commerce UI handlers. Production-ready.
 */

/* ── 1. Body reveal: add 'loaded' ASAP, don't wait for images ── */
(function () {
    function revealBody() {
        document.body.classList.add('loaded');
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', revealBody);
    } else {
        revealBody();
    }
    // Belt-and-suspenders: also on load
    window.addEventListener('load', revealBody);
})();

/* ── 2. Mobile Menu Toggle ── */
(function () {
    const trigger = document.getElementById('mobile-menu-trigger');
    const menu = document.getElementById('mobile-menu');
    const icon = document.getElementById('hamburger-icon');

    if (!trigger || !menu) return;

    function openMenu() {
        menu.style.display = 'block';
        menu.classList.remove('hidden');
        trigger.setAttribute('aria-expanded', 'true');
        if (icon) { icon.classList.remove('fa-bars'); icon.classList.add('fa-times'); }
        // Animate in
        requestAnimationFrame(() => {
            menu.style.opacity = '1';
            menu.style.transform = 'translateY(0)';
        });
    }

    function closeMenu() {
        menu.classList.add('hidden');
        trigger.setAttribute('aria-expanded', 'false');
        if (icon) { icon.classList.add('fa-bars'); icon.classList.remove('fa-times'); }
    }

    function toggleMenu() {
        const isHidden = menu.classList.contains('hidden') || getComputedStyle(menu).display === 'none';
        isHidden ? openMenu() : closeMenu();
    }

    trigger.addEventListener('click', (e) => { e.stopPropagation(); toggleMenu(); });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!menu.classList.contains('hidden') &&
            !menu.contains(e.target) &&
            !trigger.contains(e.target)) {
            closeMenu();
        }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeMenu();
    });
})();

/* ── 3. Mobile Accordion (categories + brands in mobile nav) ── */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.accordion-trigger').forEach(function (trigger) {
        trigger.addEventListener('click', function (e) {
            e.stopPropagation();
            const item = trigger.closest('.mobile-accordion-item, .mobile-accordion');
            const panel = item ? item.querySelector('.mobile-sub') : null;
            const chevron = trigger.querySelector('.chevron, .fa-chevron-down');
            if (!panel) return;

            const isOpen = panel.style.display === 'block';
            // Close all siblings
            if (item && item.parentElement) {
                item.parentElement.querySelectorAll('.mobile-sub').forEach(function (p) {
                    if (p !== panel) {
                        p.style.display = 'none';
                        const parentItem = p.closest('.mobile-accordion-item, .mobile-accordion');
                        if (parentItem) {
                            const c = parentItem.querySelector('.chevron, .fa-chevron-down');
                            if (c) c.style.transform = 'rotate(0deg)';
                        }
                    }
                });
            }

            panel.style.display = isOpen ? 'none' : 'block';
            if (chevron) chevron.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
        });
    });
});

/* ── 4. Mega Menu — fix inline opacity:0 style on hover ── */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.nav-item-mega').forEach(function (item) {
        const dropdown = item.querySelector('[style*="opacity:0"]');
        if (!dropdown) return;

        // Strip inline opacity/transform — CSS group-hover handles it
        dropdown.style.removeProperty('opacity');
        dropdown.style.removeProperty('transform');
    });
});

/* ── 5. Header Scroll State ── */
(function () {
    var header = document.getElementById('main-header');
    if (!header) return;
    function onScroll() {
        if (window.scrollY > 40) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
})();

/* ── 6. Header Category Horizontal Scroller ── */
(function () {
    var scrollContainer = document.getElementById('header-category-scroll');
    var btnLeft = document.getElementById('cat-scroll-left');
    var btnRight = document.getElementById('cat-scroll-right');
    if (!scrollContainer || !btnLeft || !btnRight) return;

    var scrollAmount = 220;

    function scrollLeft() {
        if (scrollContainer.scrollLeft <= 0) {
            scrollContainer.scrollLeft = scrollContainer.scrollWidth;
        }
        scrollContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    }

    function scrollRight() {
        var maxScroll = scrollContainer.scrollWidth - scrollContainer.clientWidth;
        if (scrollContainer.scrollLeft >= maxScroll - 10) {
            scrollContainer.scrollLeft = 0;
        }
        scrollContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }

    btnLeft.addEventListener('click', scrollLeft);
    btnRight.addEventListener('click', scrollRight);

    function checkOverflow() {
        var isOverflowing = scrollContainer.scrollWidth > scrollContainer.clientWidth + 10;
        btnLeft.style.display = isOverflowing ? 'flex' : 'none';
        btnRight.style.display = isOverflowing ? 'flex' : 'none';
    }

    window.addEventListener('resize', checkOverflow);
    setTimeout(checkOverflow, 300);
})();

/* ── 7. Scroll Animation Observer ── */
document.addEventListener('DOMContentLoaded', function () {
    if (!('IntersectionObserver' in window)) return;

    var animateObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                animateObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.stagger-children > *').forEach(function (el, i) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(18px)';
        el.style.transition = 'opacity 0.5s ease ' + (i * 70) + 'ms, transform 0.5s ease ' + (i * 70) + 'ms';
        animateObserver.observe(el);
    });

    document.querySelectorAll('[data-animate]').forEach(function (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(14px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        animateObserver.observe(el);
    });
});

/* ── 8. Toast Notification ── */
window.showToast = function (message, type) {
    type = type || 'success';
    var toast = document.getElementById('premium-toast');
    var toastMsg = document.getElementById('toast-message');
    var toastTitle = document.getElementById('toast-title');
    var toastIcon = document.getElementById('toast-icon');

    if (toastMsg) toastMsg.innerText = message;
    if (toastTitle) toastTitle.innerText = type === 'success' ? 'Success' : type === 'error' ? 'Error' : 'Notice';
    if (toastIcon) {
        toastIcon.innerHTML = type === 'success'
            ? '<i class="fas fa-check text-xs"></i>'
            : type === 'error'
                ? '<i class="fas fa-times text-xs"></i>'
                : '<i class="fas fa-info text-xs"></i>';
    }

    if (toast) {
        toast.classList.add('show');
        clearTimeout(toast._hideTimer);
        toast._hideTimer = setTimeout(function () {
            toast.classList.remove('show');
        }, 4000);
    }
};

/* ── 9. Wishlist Toggle ── */
window.toggleWishlist = async function (productId, btn) {
    var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfInput) return;
    var csrfToken = csrfInput.value;
    var url = '/products/wishlist/toggle/' + productId + '/';

    try {
        var response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });

        if (response.status === 401 || (response.url && response.url.includes('/login'))) {
            window.location.href = '/accounts/login/?next=' + window.location.pathname;
            return;
        }

        var data = await response.json();

        if (data.status === 'added' || data.status === 'removed') {
            var icon = btn ? btn.querySelector('i') : null;
            var wishCountBadge = document.querySelector('.wishlist-count-badge');

            if (data.status === 'added') {
                if (icon) { icon.classList.remove('far'); icon.classList.add('fas'); }
                if (btn) { btn.classList.add('active'); }
                showToast('Added to wishlist ❤️');
            } else {
                if (icon) { icon.classList.remove('fas'); icon.classList.add('far'); }
                if (btn) { btn.classList.remove('active'); }
                showToast('Removed from wishlist');

                if (window.location.pathname.includes('/wishlist/')) {
                    var itemCard = btn ? btn.closest('[data-item-id]') : null;
                    if (itemCard) {
                        itemCard.style.opacity = '0';
                        itemCard.style.transform = 'scale(0.9)';
                        itemCard.style.transition = 'all 0.3s ease';
                        setTimeout(function () {
                            itemCard.remove();
                            if (document.querySelectorAll('[data-item-id]').length === 0) {
                                location.reload();
                            }
                        }, 300);
                    }
                }
            }

            if (wishCountBadge) {
                if (data.count > 0) {
                    wishCountBadge.classList.remove('hidden');
                    wishCountBadge.innerText = data.count;
                } else {
                    wishCountBadge.classList.add('hidden');
                }
            }
        }
    } catch (err) {
        console.error('Wishlist error:', err);
        showToast('Something went wrong. Please try again.', 'error');
    }
};

/* ── 10. AJAX Cart Handler ── */
document.addEventListener('click', async function (e) {
    var cartBtn = e.target.closest('.cart-action-btn');
    if (!cartBtn) return;

    e.preventDefault();
    var url = cartBtn.getAttribute('data-url');
    var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!url || !csrfInput) { if (url) window.location.href = url; return; }

    try {
        var response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfInput.value
            }
        });
        if (response.ok) {
            showToast('Added to your enquiry cart!');
            document.querySelectorAll('.cart-count-badge').forEach(function (badge) {
                var count = (parseInt(badge.innerText) || 0) + 1;
                badge.innerText = count;
                badge.classList.remove('hidden');
            });
        }
    } catch (err) {
        if (url) window.location.href = url;
    }
});

/* ── 11. Delegated wishlist-btn (no-onclick variant) ── */
document.addEventListener('click', function (e) {
    var btn = e.target.closest('.wishlist-btn');
    if (!btn || btn.hasAttribute('onclick')) return;
    e.preventDefault();
    var productId = btn.getAttribute('data-product-id');
    if (productId) window.toggleWishlist(productId, btn);
});
