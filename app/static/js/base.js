let currentSlide = 0; // Tracks the index of the current slide
const slides = document.querySelectorAll('.carousel-images img');
const totalSlides = slides.length;

// Function to show the active slide
function showSlide(index) {
    // Reset all slides to hidden
    slides.forEach((slide) => slide.classList.remove('active-slide'));
    
    // Show the current slide
    slides[index].classList.add('active-slide');
}

// Automatic sliding functionality
function autoSlide() {
    currentSlide = (currentSlide + 1) % totalSlides; // Loop back to the first slide after the last one
    showSlide(currentSlide);
}

// Button functionality for next and previous
document.getElementById('nextButton').addEventListener('click', () => {
    currentSlide = (currentSlide + 1) % totalSlides;
    showSlide(currentSlide);
});

document.getElementById('prevButton').addEventListener('click', () => {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides; // Loop back to the last slide
    showSlide(currentSlide);
});

// Start the automatic sliding (change every 3 seconds)
setInterval(autoSlide, 3000);

// Show the first slide when the page loads
showSlide(currentSlide);
