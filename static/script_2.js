$(document).ready(function() {
  var signoutvalue = document.getElementById('sign-out').getAttribute('soutvalue');
  if (signoutvalue = true) {
    ;
    setTimeout(function() {
      document.getElementById('sign-out').click();
    }, 500);
  }

  var errorLen = $("#errorHidden").val().length;
  var errorMsg = document.getElementById("errorMsg");
  if (errorLen > 0) {
    errorMsg.style.display = "block";
  }
  $('.sharedir').click(function() {
    id = this.id;
    var value = id.split("share_");
    if (value[0] == "d1") {
      $('#isDirectory').val(1);
    } else {
      $('#isDirectory').val(2);
    }
    $('#hiddendir').val(value[1]);
    var shareModel = document.getElementById("shareModel");
    var span4 = document.getElementsByClassName("close4")[0];
    shareModel.style.display = "block";
    span4.onclick = function() {
      shareModel.style.display = "none";
    }

    window.onclick = function(event) {
      if (event.target == shareModel) {
        shareModel.style.display = "none";
      }
    }

  });

  $("#createDir").click(function() {
    var modal = document.getElementById("myModal");
    var span = document.getElementsByClassName("close2")[0];
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


  $("#fileUpload").click(function() {
    var fileUploadModal = document.getElementById("fileUploadModal");
    var span = document.getElementsByClassName("close3")[0];
    fileUploadModal.style.display = "block";
    span.onclick = function() {
      fileUploadModal.style.display = "none";
    }

    window.onclick = function(event) {
      if (event.target == fileUploadModal) {
        fileUploadModal.style.display = "none";
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