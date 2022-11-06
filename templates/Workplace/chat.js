// Collapsible for chat
var coll = document.getElementsByClassName("collapsible");
for (let i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function () {
    this.classList.toggle("active");

    var content = this.nextElementSibling;

    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
  });
}

// Establish a WebSocket connection with the server
const socket = new WebSocket("ws://" + window.location.host + "/websocket");

// Tyler
// Sends JSON data to websocket
// Read the comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
function sendMessage() {
  const chatBox = document.getElementById("textInput");
  const comment = chatBox.value;
  console.log("hi");
  chatBox.value = "";
  chatBox.focus();
  if (comment !== "") {
    addToButton(comment);
    //Change the username here
    socket.send(JSON.stringify({ user: "Taylor", comment: comment }));
  }
}

// Add text to chat
function addToButton(userText) {
  const chat = document.getElementById("chatbox");
  chat.innerHTML +=
    `<p class=${"botText"}><span class=${"botText"}><b>` +
    userText +
    "</b>: " +
    userText +
    "<br/></span></p>";
  chat.scrollIntoView(true);
}

// Matt
// This will render the messages sent by the server for any 200 request
// It will try to get a request to /chat-history
// Code provided by Jesse for homework
function get_chat_history() {
  const request = new XMLHttpRequest();
  request.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      const messages = JSON.parse(this.response);
      for (const message of messages) {
        addMessage(message);
      }
    }
  };
  request.open("GET", "/chat-history");
  request.send();
}
