// dark_mode_toggle.js

document.addEventListener("DOMContentLoaded", function () {
    const toggleDarkModeBtn = document.getElementById('darkModeToggle');
    if (!toggleDarkModeBtn) return; // Prevent errors if the element doesn't exist

    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    const THEME_KEY = 'theme';

    const setTheme = (theme) => {
        if (theme === "dark") {
            document.body.classList.add("dark-mode");
            toggleDarkModeBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
        } else {
            document.body.classList.remove("dark-mode");
            toggleDarkModeBtn.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
        }
    };

    // Initialize Theme
    const initializeTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme) {
            setTheme(savedTheme);
        } else if (prefersDarkScheme.matches) {
            setTheme("dark");
            localStorage.setItem(THEME_KEY, "dark");
        }
    };

    // Toggle Theme on Button Click
    toggleDarkModeBtn.addEventListener("click", function () {
        const isDarkMode = document.body.classList.toggle("dark-mode");
        const theme = isDarkMode ? "dark" : "light";
        toggleDarkModeBtn.innerHTML = isDarkMode
            ? '<i class="fas fa-sun"></i> Light Mode'
            : '<i class="fas fa-moon"></i> Dark Mode';
        localStorage.setItem(THEME_KEY, theme);
    });

    initializeTheme();
});
