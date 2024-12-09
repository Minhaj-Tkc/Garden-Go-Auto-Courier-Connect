// JavaScript to handle flash message display
document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll(".flash-message");
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            // Show the message for 3 seconds
            setTimeout(() => {
                message.style.display = "none";
            }, 3000);
        });
    }
});