/**
 * main.js
 * Core commerce functionality and UI handlers.
 */

const Commerce = {
    toggleMobileMenu: () => {
        const menu = document.getElementById('mobile-menu');
        if (menu) menu.classList.toggle('hidden');
    },

    dismissAnnouncement: () => {
        const bar = document.getElementById('announcement-bar');
        const header = document.getElementById('main-header');
        if (bar) {
            bar.classList.add('hidden');
            // Adjust header padding if needed
            document.body.style.paddingTop = '80px'; 
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // 1. Swiper Initialization (Announcement Bar)
    if (document.querySelector('.announcement-swiper')) {
        new Swiper('.announcement-swiper', {
            direction: 'vertical',
            loop: true,
            autoplay: { delay: 4000, disableOnInteraction: false },
            speed: 800
        });
    }

    // 2. Mobile Menu Handlers
    const menuTrigger = document.getElementById('mobile-menu-trigger');
    if (menuTrigger) menuTrigger.addEventListener('click', Commerce.toggleMobileMenu);

    const dismissTrigger = document.getElementById('dismiss-announcement');
    if (dismissTrigger) dismissTrigger.addEventListener('click', Commerce.dismissAnnouncement);

    // 3. Mobile Accordion Logic
    document.querySelectorAll('.accordion-trigger').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const panel = trigger.nextElementSibling;
            const chevron = trigger.querySelector('.chevron');
            if (panel) panel.classList.toggle('hidden');
            if (chevron) chevron.classList.toggle('rotate-180');
        });
    });

    // 4. Close mobile menu on outside click
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('mobile-menu');
        const trigger = document.getElementById('mobile-menu-trigger');
        if (menu && !menu.contains(e.target) && trigger && !trigger.contains(e.target) && !menu.classList.contains('hidden')) {
            Commerce.toggleMobileMenu();
        }
    });

    // 5. Smart Category Selection
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('mouseenter', () => {
            document.querySelectorAll('.category-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // 6. Entrance Animation
    window.addEventListener('load', () => {
        document.body.classList.add('loaded');
    });
});

/**
 * Global Toast Helper
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('premium-toast');
    const toastMsg = document.getElementById('toast-message');
    const toastTitle = document.getElementById('toast-title');
    const toastIcon = document.getElementById('toast-icon');

    if (toastMsg) toastMsg.innerText = message;
    if (toastTitle) toastTitle.innerText = type === 'success' ? 'Success' : 'Attention';
    
    if (toast) {
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 4000);
    }
}

/**
 * Global Wishlist Toggle
 */
async function toggleWishlist(productId, btn) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = `/products/wishlist/toggle/${productId}/`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        });
        
        if (response.status === 401 || response.url.includes('/login')) {
            window.location.href = `/accounts/login/?next=${window.location.pathname}`;
            return;
        }

        const data = await response.json();
        
        if (data.status === 'added' || data.status === 'removed') {
            const icon = btn.querySelector('i');
            const wishCountBadge = document.querySelector('.wishlist-count-badge');
            
            if (data.status === 'added') {
                if (icon) icon.classList.replace('far', 'fas');
                btn.classList.add('bg-red-500', 'text-white', 'border-red-500');
                btn.classList.remove('bg-slate-900/40');
                showToast('Added to wishlist');
            } else {
                if (icon) icon.classList.replace('fas', 'far');
                btn.classList.remove('bg-red-500', 'text-white', 'border-red-500');
                btn.classList.add('bg-slate-900/40');
                showToast('Removed from wishlist');
                
                if (window.location.pathname.includes('/wishlist/')) {
                    const itemCard = btn.closest('[data-item-id]');
                    if (itemCard) {
                        itemCard.style.opacity = '0';
                        itemCard.style.transform = 'scale(0.9)';
                        setTimeout(() => {
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
        console.error('Wishlist failed:', err);
    }
}

/**
 * Global AJAX Handlers (Add to Cart, etc.)
 */
document.addEventListener('click', async (e) => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    if (e.target.closest('.cart-action-btn')) {
        e.preventDefault();
        const btn = e.target.closest('.cart-action-btn');
        const url = btn.getAttribute('data-url');
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });
            if (response.ok) {
                showToast('Item added to your cart!');
                const cartCounters = document.querySelectorAll('.cart-count-val');
                cartCounters.forEach(cartCounter => {
                    let curr = parseInt(cartCounter.innerText) || 0;
                    cartCounter.innerText = curr + 1;
                });
            }
        } catch (err) {
            window.location.href = url;
        }
    }

    if (e.target.closest('.wishlist-btn') && !e.target.closest('[onclick]')) {
        e.preventDefault();
        const btn = e.target.closest('.wishlist-btn');
        const productId = btn.getAttribute('data-product-id');
        if (productId) toggleWishlist(productId, btn);
    }
});

/**
 * Security Deterrents
 */
document.addEventListener('contextmenu', (e) => e.preventDefault());
document.onkeydown = function(e) {
    if (e.keyCode == 123) return false;
    if (e.ctrlKey && e.shiftKey && e.keyCode == 'I'.charCodeAt(0)) return false;
    if (e.ctrlKey && e.shiftKey && e.keyCode == 'C'.charCodeAt(0)) return false;
    if (e.ctrlKey && e.shiftKey && e.keyCode == 'J'.charCodeAt(0)) return false;
    if (e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)) return false;
};
