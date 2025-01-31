// Select elements
const menuBtn = document.getElementById("hamburger-menu");
const closeBtn = document.getElementById("close-btn");
const sidebar = document.getElementById("sidebar");
const bars = document.querySelectorAll(".bar");

// Open Sidebar
menuBtn.addEventListener("click", () => {
    sidebar.classList.add("open");
    transformHamburger(true);
});

// Close Sidebar
closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("open");
    transformHamburger(false);
});

// Close Sidebar when clicking outside
document.addEventListener("click", (event) => {
    if (!sidebar.contains(event.target) && !menuBtn.contains(event.target)) {
        sidebar.classList.remove("open");
        transformHamburger(false);
    }
});

// Function to Transform Hamburger Menu
function transformHamburger(isOpen) {
    if (isOpen) {
        bars[0].style.transform = "rotate(45deg) translateY(6px)";
        bars[1].style.opacity = "0";
        bars[2].style.transform = "rotate(-45deg) translateY(-6px)";
    } else {
        bars[0].style.transform = "rotate(0)";
        bars[1].style.opacity = "1";
        bars[2].style.transform = "rotate(0)";
    }
}
