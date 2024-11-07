document.addEventListener("DOMContentLoaded", function () {
    var assistModal = document.getElementById("assistmodal");
    var closeModal = document.querySelector("#assistmodal .close");
    var helpButton = document.getElementById("helpButton");

    // Show the modal when help button is clicked
    if (helpButton) {
        helpButton.onclick = function () {
            assistModal.style.display = "block";
        }
    }

    // Close the modal when close (x) is clicked
    closeModal.onclick = function () {
        assistModal.style.display = "none";
    }

    // Close the modal if the user clicks outside of it
    window.onclick = function (event) {
        if (event.target == assistModal) {
            assistModal.style.display = "none";
        }
    }
});