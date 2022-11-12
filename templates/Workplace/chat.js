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

function addMessagesToChat(messages) {
  var text = ""
  for (let i = 0; i < messages.length; i++) {
    console.log(messages[i])
    console.log(messages[i]["username"])
    text += "<span><b>"+messages[i]["username"]+"</b>: "+messages[i]["message"]+"</span><br>"
  }
  document.getElementById("botStarterMessage").innerHTML += text;
}

// Establish a WebSocket connection with the server
var socket = io(); // new WebSocket("ws://" + window.location.host + "/websocket");
socket.on('connect', function() {
  socket.emit('initialDataRequest', {
      code: thisWorkplaceCode,
      authToken: getCookie("userID")
  });
});

socket.on('newMessage', function(messageSet) {
  console.log(messageSet);
  addMessagesToChat(messageSet["messages"]);
});

const thisPath = window.location.pathname
const thisWorkplaceCode = thisPath.split("/").pop()


// Tyler
// Sends JSON data to websocket
// Read the comment the user is sending to chat and send it to the server over the WebSocket as a JSON string
function sendMessage() {
  const chatBox = document.getElementById("textInput");
  const comment = chatBox.value;
  chatBox.value = "";
  chatBox.focus();
  if (comment !== "") {
    // addToButton(comment);
    //Change the username here
    socket.send(JSON.stringify({ 
      user: getCookie("userID"), 
      comment: comment,
      workplaceCode: thisWorkplaceCode
     }));
  }
}

// Add text to chat
function addToButton(userText) {
  sendMessage()
  // user = getCookie("userID");
  // const chat = document.getElementById("chatbox");
  // chat.innerHTML +=
  //   `<p class=${"botText"}><span class=${"botText"}><b>` +
  //   user +
  //   "</b>: " +
  //   userText +
  //   "<br/></span></p>";
  // chat.scrollIntoView(true);
  // const request = new XMLHttpRequest();
  // let url = window.location.href
  // let arr = url.split("/")
  // let code = arr[arr.length-1]
  // request.open("POST", "/chat-history");
  // request.send(userText+","+code);
}

// Matt
// This will render the messages sent by the server for any 200 request
// It will try to get a request to /chat-history
// Code provided by Jesse for homework
//function get_chat_history() {
  // console.log("/chat-history")
  // const request = new XMLHttpRequest();
  // request.onreadystatechange = function () {
  //   if (this.readyState === 4 && this.status === 200) {
  //     const messages = JSON.parse(this.response);
  //     for (const message of messages) {
  //       addMessage(message);
  //     }
  //   }
  // };
  // let url = window.location.href
  // let arr = url.split("/")
  // let code = arr[arr.length-1]
  // request.open("GET", "/chat-history/"+code);
  // request.send();
//}

// Given the name of the cookie it will return the value
// Source: https://www.w3schools.com/js/js_cookies.asp
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}