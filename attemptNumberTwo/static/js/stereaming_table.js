document.addEventListener('DOMContentLoaded', () => {
    const scrollContainer = document.querySelector('.table-responsive');
    let isDragging = false;
    let startX;
    let initialScrollLeft;

    // Mouse Down Handler
    const onMouseDown = (e) => {
        isDragging = true;
        scrollContainer.classList.add('active');
        startX = e.clientX - scrollContainer.getBoundingClientRect().left;
        initialScrollLeft = scrollContainer.scrollLeft;
    };

    // Mouse Up and Leave Handler
    const stopDragging = () => {
        isDragging = false;
        scrollContainer.classList.remove('active');
    };

    // Mouse Move Handler with requestAnimationFrame for smoother performance
    const onMouseMove = (e) => {
        if (!isDragging) return;
        e.preventDefault();
        const currentX = e.clientX - scrollContainer.getBoundingClientRect().left;
        const walk = (currentX - startX) * 1; // Adjust scroll speed here
        scrollContainer.scrollLeft = initialScrollLeft - walk;
    };

    // Attach Event Listeners
    scrollContainer.addEventListener('mousedown', onMouseDown);
    scrollContainer.addEventListener('mouseleave', stopDragging);
    scrollContainer.addEventListener('mouseup', stopDragging);
    scrollContainer.addEventListener('mousemove', onMouseMove);

    // Optional: Prevent default drag behavior on images or links inside the container
    scrollContainer.addEventListener('dragstart', (e) => e.preventDefault());
});
    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('toggle_table').addEventListener('click', () => {
            document.querySelectorAll('.display_hidden_row').forEach((row) => {
                row.classList.toggle('extra-row');
            });
        });
    });

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