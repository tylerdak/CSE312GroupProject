
// Modal code provided by W3 schools
// Get the modal
var joinModal = document.getElementById("joinModal");
var createModal = document.getElementById("createModal");

// Get the button that opens the modal
var join = document.getElementById("joinButton");
var create = document.getElementById("createButton");

// Get the <span> element that closes the modal
var joinModalClose = document.getElementById("joinModalClose");
var createModalClose = document.getElementById("createModalClose");

// When the user clicks on the button, open the modal
join.onclick = function() {
  joinModal.style.display = "block";
}

// When the user clicks on the button, open the modal
create.onclick = function() {
  createModal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
joinModalClose.onclick = function() {
  	joinModal.style.display = "none";
}

createModalClose.onclick = function() {
	createModal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == joinModal) {
	joinModal.style.display = "none";
  }
  if (event.target == createModal) {
  	createModal.style.display = "none";
  }
}

function enterWorkplace(code) {
  window.location.replace("/workplace/" + code);
}
