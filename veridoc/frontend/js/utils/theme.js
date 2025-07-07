/**
 * Theme manager for VeriDoc
 * Handles theme switching and persistence
 */
class ThemeManager {
    constructor() {
        this.themeKey = 'veridoc-theme';
        this.currentTheme = this.loadTheme();
        this.applyTheme(this.currentTheme);
        this.initializeToggle();
    }

    /**
     * Load theme from localStorage or use system preference
     * @returns {string} 'light' or 'dark'
     */
    loadTheme() {
        const savedTheme = localStorage.getItem(this.themeKey);
        if (savedTheme) {
            return savedTheme;
        }
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        
        return 'dark';
    }

    /**
     * Apply theme to document
     * @param {string} theme - 'light' or 'dark'
     */
    applyTheme(theme) {
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        this.updateToggleButton(theme);
        this.updatePrismTheme(theme);
    }

    /**
     * Update Prism syntax highlighting theme
     * @param {string} theme - Current theme
     */
    updatePrismTheme(theme) {
        const darkTheme = document.getElementById('prism-theme-dark');
        const lightTheme = document.getElementById('prism-theme-light');
        
        if (darkTheme && lightTheme) {
            if (theme === 'light') {
                darkTheme.disabled = true;
                lightTheme.disabled = false;
            } else {
                darkTheme.disabled = false;
                lightTheme.disabled = true;
            }
        }
    }

    /**
     * Update toggle button icon based on current theme
     * @param {string} theme - Current theme
     */
    updateToggleButton(theme) {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            const iconSpan = toggleBtn.querySelector('.btn-icon');
            const textSpan = toggleBtn.querySelector('.btn-text');
            
            if (iconSpan && textSpan) {
                iconSpan.textContent = theme === 'light' ? '🌞' : '🌙';
                textSpan.textContent = theme === 'light' ? 'Light' : 'Dark';
                toggleBtn.title = theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme';
            } else {
                // Fallback for old structure
                toggleBtn.textContent = theme === 'light' ? '🌞' : '🌙';
                toggleBtn.title = theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme';
            }
        }
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        localStorage.setItem(this.themeKey, this.currentTheme);
    }

    /**
     * Initialize theme toggle button
     */
    initializeToggle() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleTheme());
        }

        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
            mediaQuery.addEventListener('change', (e) => {
                // Only apply if user hasn't manually set a preference
                if (!localStorage.getItem(this.themeKey)) {
                    this.currentTheme = e.matches ? 'light' : 'dark';
                    this.applyTheme(this.currentTheme);
                }
            });
        }
    }
}

// Export for use in other modules
window.ThemeManager = ThemeManager;