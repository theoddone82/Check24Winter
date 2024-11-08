document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('toggleSelectedPackagesBtn').addEventListener('click', function () {
        var infoDiv = document.getElementById('selectedPackagesInfo');
        if (infoDiv.style.display === 'none' || infoDiv.style.display === '') {
            infoDiv.style.display = 'block';
        } else {
            infoDiv.style.display = 'none';
        }
    });
    const toggleDarkModeBtn = document.getElementById('darkModeToggle');
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    
    const currentTheme = localStorage.getItem("theme");
    if (currentTheme == "dark") {
        document.body.classList.add("dark-mode");
        toggleDarkModeBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
    } else if (currentTheme == "light") {
        document.body.classList.remove("dark-mode");
    } else if (prefersDarkScheme.matches) {
        document.body.classList.add("dark-mode");
        toggleDarkModeBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
    }
    
    toggleDarkModeBtn.addEventListener("click", function () {
        console.log("clicked");
        document.body.classList.toggle("dark-mode");
        let theme = "light";
        if (document.body.classList.contains("dark-mode")) {
            theme = "dark";
            toggleDarkModeBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
        } else {
            toggleDarkModeBtn.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
        }
        localStorage.setItem("theme", theme);
    });
    });
    