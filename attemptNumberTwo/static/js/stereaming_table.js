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