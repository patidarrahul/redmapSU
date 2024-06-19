  // Get a reference to the div element
  var myDiv = document.getElementById("formulation");


  $(document).ready(function () {
    // Handle Delete buttons
    $(".mark-complete-btn").click(function () {
      const selectedId = $('input[name="selected_formulation"]:checked').val();
      if (selectedId) {
        window.location.href = "/formulation/complete/" + selectedId;
      }
    });

    // Handle edit buttons
    $(".update-selected-btn").click(function () {
      const selectedId = $('input[name="selected_formulation"]:checked').val();
      if (selectedId) {
        window.location.href = "/formulation/update/" + selectedId;
      }
    });
  });