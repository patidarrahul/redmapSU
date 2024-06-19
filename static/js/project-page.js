document.addEventListener("DOMContentLoaded", function () {
    // Get all cards
    var cards = document.querySelectorAll(".card-body");

    // Loop through each card
    for (var i = 0; i < cards.length; i++) {
      // If it's the first card, display as block, otherwise set to none
      if (i === 0) {
        cards[i].style.display = "block";
      } else {
        cards[i].style.display = "none";
      }
    }
  });

  function toggleDetails(event, id) {
    event.preventDefault();
    var details = document.getElementById(id);
    details.style.display = details.style.display === "none" ? "block" : "none";
  }