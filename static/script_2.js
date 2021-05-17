$(document).ready(function() {
  var errorLen = $("#errorHidden").val().length;
  var errorMsg = document.getElementById("errorMsg");
  if (errorLen > 0) {
    errorMsg.style.display = "block";
  }

  $("#createDir").click(function() {
    var modal = document.getElementById("myModal");
    var span = document.getElementsByClassName("close")[0];
    modal.style.display = "block";
    span.onclick = function() {
      modal.style.display = "none";
    }

    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }

  });

  var span = document.getElementsByClassName("close")[0];

  //errorMsg.style.display = "block";
  span.onclick = function() {
    errorMsg.style.display = "none";
  }
  window.onclick = function(event) {
    if (event.target == errorMsg) {
      errorMsg.style.display = "none";
    }
  }
});