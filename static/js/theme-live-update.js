/**
 * Real-Time Theme Preview System
 * 
 * This module enables instant theme updates across all open frontend pages
 * when admin saves theme settings. Uses BroadcastChannel API (with localStorage fallback)
 * to communicate theme changes in real-time.
 */

(function () {
    'use strict';

    const THEME_UPDATE_CHANNEL = 'theme-updates';
    const THEME_STORAGE_KEY = 'theme_settings_version';

    window.ThemeLiveUpdate = {
        channel: null,
        lastVersion: null,
        pollInterval: null,

        init: function () {
            // Initialize BroadcastChannel if supported
            if ('BroadcastChannel' in window) {
                this.channel = new BroadcastChannel(THEME_UPDATE_CHANNEL);
                this.channel.onmessage = (event) => this.handleMessage(event.data);
                console.log('[ThemeLiveUpdate] Using BroadcastChannel for real-time updates');
            } else {
                // Fallback: poll localStorage for changes
                this.startPolling();
                console.log('[ThemeLiveUpdate] Using localStorage polling (BroadcastChannel not supported)');
            }

            // Listen for localStorage changes (works across tabs)
            window.addEventListener('storage', (event) => this.handleStorageEvent(event));

            // Get initial version
            this.lastVersion = this.getStoredVersion();
        },

        handleMessage: function (data) {
            if (data.type === 'theme_update' && data.settings) {
                this.applyThemeSettings(data.settings);
                this.lastVersion = data.version;
            }
        },

        handleStorageEvent: function (event) {
            if (event.key === THEME_STORAGE_KEY && event.newValue) {
                try {
                    var data = JSON.parse(event.newValue);
                    if (data.type === 'theme_update' && data.settings) {
                        this.applyThemeSettings(data.settings);
                    }
                } catch (e) {
                    console.warn('[ThemeLiveUpdate] Failed to parse storage event:', e);
                }
            }
        },

        startPolling: function () {
            // Poll every 2 seconds for changes (fallback for older browsers)
            this.pollInterval = setInterval(() => {
                var currentVersion = this.getStoredVersion();
                if (currentVersion && currentVersion !== this.lastVersion) {
                    this.lastVersion = currentVersion;
                    this.fetchLatestSettings();
                }
            }, 2000);
        },

        getStoredVersion: function () {
            try {
                var data = localStorage.getItem(THEME_STORAGE_KEY);
                if (data) {
                    return JSON.parse(data).version;
                }
            } catch (e) { }
            return null;
        },

        fetchLatestSettings: function () {
            fetch('/api/design-settings/')
                .then(response => response.json())
                .then(data => {
                    this.applyThemeSettings(data);
                })
                .catch(err => {
                    console.warn('[ThemeLiveUpdate] Failed to fetch settings:', err);
                });
        },

        applyThemeSettings: function (settings) {
            var root = document.documentElement;

            if (!root) return;

            // Color settings
            var colorFields = [
                'primary_color', 'secondary_color', 'accent_color', 'accent_hover_color',
                'text_primary_color', 'text_secondary_color', 'text_white_color', 'text_accent_color',
                'surface_bg_color', 'card_bg_color', 'border_color', 'border_hover_color',
                'header_bg_color', 'header_text_color', 'header_border_color',
                'footer_bg_color', 'footer_text_color', 'footer_heading_color',
                'category_bg_color', 'price_color', 'sale_price_color', 'rating_star_color',
                'button_primary_bg', 'button_primary_text', 'button_primary_hover_bg',
                'button_secondary_bg', 'button_secondary_text', 'button_secondary_border',
                'button_secondary_hover_bg', 'button_secondary_hover_text'
            ];

            colorFields.forEach(function (field) {
                if (settings[field]) {
                    root.style.setProperty('--' + field, settings[field]);
                }
            });

            // Typography
            if (settings.font_main) {
                root.style.setProperty('--font-main', settings.font_main);
            }
            if (settings.font_heading) {
                root.style.setProperty('--font-heading', settings.font_heading);
            }
            if (settings.font_accent) {
                root.style.setProperty('--font-accent', settings.font_accent);
            }

            // Border radius
            if (settings.container_radius) {
                root.style.setProperty('--radius-container', settings.container_radius);
            }
            if (settings.card_radius) {
                root.style.setProperty('--radius-card', settings.card_radius);
            }
            if (settings.button_radius) {
                root.style.setProperty('--radius-btn', settings.button_radius);
            }
            if (settings.image_radius) {
                root.style.setProperty('--radius-img', settings.image_radius);
            }
            if (settings.input_radius) {
                root.style.setProperty('--radius-input', settings.input_radius);
            }

            // Spacing
            if (settings.spacing_unit) {
                root.style.setProperty('--space-unit', settings.spacing_unit + 'px');
            }
            if (settings.section_padding) {
                root.style.setProperty('--section-padding', settings.section_padding + 'px');
            }
            if (settings.container_padding) {
                root.style.setProperty('--container-padding', settings.container_padding + 'px');
            }

            // Site scale
            if (settings.site_scale) {
                root.style.setProperty('--site-scale', settings.site_scale);
            }

            console.log('[ThemeLiveUpdate] Theme settings applied successfully');

            // Dispatch custom event for other scripts to hook into
            window.dispatchEvent(new CustomEvent('themeUpdated', { detail: settings }));
        },

        // Called by admin when saving settings
        broadcastUpdate: function (settings, version) {
            var data = {
                type: 'theme_update',
                settings: settings,
                version: version || Date.now()
            };

            // Use BroadcastChannel if available
            if (this.channel) {
                this.channel.postMessage(data);
            }

            // Also store in localStorage for cross-tab communication
            try {
                localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(data));
            } catch (e) {
                console.warn('[ThemeLiveUpdate] localStorage not available:', e);
            }
        }
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            window.ThemeLiveUpdate.init();
        });
    } else {
        window.ThemeLiveUpdate.init();
    }
})();