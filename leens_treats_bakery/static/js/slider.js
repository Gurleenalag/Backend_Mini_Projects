let index = 0;
let slides = document.querySelectorAll(".slide");

function showSlides() {
    slides.forEach(slide => slide.style.display = "none");
    if (slides.length > 0) {
        slides[index].style.display = "block";
        index = (index + 1) % slides.length;
    }
}

// First call
showSlides();

// Change slide every 2 seconds
setInterval(showSlides, 2000);
