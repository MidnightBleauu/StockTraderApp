document.addEventListener("DOMContentLoaded", function () {
    var modal = document.getElementById("infoModal");
    var helpButton = document.getElementById("helpButton");
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on the button, pop up menu opens
    helpButton.onclick = function() {
        modal.style.display = "block";
    }
    span.onclick = function() {
        modal.style.display = "none";
    }
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});