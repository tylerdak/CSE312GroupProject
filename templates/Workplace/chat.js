//chat

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
  var text = "";
  for (let i = 0; i < messages.length; i++) {
    console.log(messages[i]);
    console.log(messages[i]["username"]);
    text +=
      "<span><b>" +
      messages[i]["username"] +
      "</b>: " +
      messages[i]["message"] +
      "</span><br>";
  }
  document.getElementById("botStarterMessage").innerHTML += text;
}

// Establish a WebSocket connection with the server
var socket = io(); // new WebSocket("ws://" + window.location.host + "/websocket");
socket.on("connect", function () {
  socket.emit("initialDataRequest", {
    code: thisWorkplaceCode,
    authToken: getCookie("userID"),
  });
});

socket.on("newMessage", function (messageSet) {
  console.log(messageSet);
  addMessagesToChat(messageSet["messages"]);
});

const thisPath = window.location.pathname;
const thisWorkplaceCode = thisPath.split("/").pop();

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
    socket.send(
      JSON.stringify({
        user: getCookie("userID"),
        comment: comment,
        workplaceCode: thisWorkplaceCode,
      })
    );
  }
}

// Add text to chat
function addToButton(userText) {
  sendMessage();
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
  let ca = decodedCookie.split(";");
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

// Brainstorm and poll
let totalVotes = 0;
let options = {};

function handleOptions(option) {
  const optionElem = document.getElementById(option + "Button");
  const percentBarElem = document.getElementById(option);
  const percentBarColor = document.getElementById(option + "Color");

  if (optionElem.classList.contains("checked")) {
    totalVotes -= 1;
    options[option] -= 1;
  } else {
    totalVotes += 1;
    options[option] += 1;
  }

  if (totalVotes === 0 || options[option] === 0) {
    percentBarColor.setAttribute("style", `width:${0}%`);
    percentBarColor.innerHTML = "\u00A0";
  } else {
    percentBarColor.setAttribute(
      "style",
      `width:${Math.round(100 * (options[option] / totalVotes))}%`
    );
    percentBarColor.innerHTML = `${Math.round(
      100 * (options[option] / totalVotes)
    )}%`;
  }

  optionElem.classList.toggle("checked");

  for (const key in options) {
    const percentBarColor2 = document.getElementById(key + "Color");
    if (totalVotes === 0 || options[key] === 0) {
      percentBarColor2.setAttribute("style", `width:${0}%`);
      percentBarColor2.innerHTML = "\u00A0";
    } else {
      percentBarColor2.setAttribute(
        "style",
        `width:${Math.round(100 * (options[key] / totalVotes))}%`
      );
      percentBarColor2.innerHTML = `${Math.round(
        100 * (options[key] / totalVotes)
      )}%`;
    }
  }

  console.log("total", totalVotes);
}

// Create a new list item when clicking on the "Add" button
function newElement() {
  const inputValue = document.getElementById("myInput").value;

  if (inputValue === "") {
    alert("You must write something");
    return;
  } else if (inputValue in options) {
    alert("You must create a new option");
    return;
  }

  const list = document.createElement("li");
  const option = document.createElement("div");
  const percentBar = document.createElement("div");
  const percentBarColor = document.createElement("div");

  const text = document.createTextNode(inputValue);
  const nbsp = document.createTextNode("\u00A0");

  option.appendChild(text);
  option.onclick = function () {
    handleOptions(inputValue);
  };
  option.setAttribute("class", "optionButton");
  option.setAttribute("id", inputValue + "Button");

  percentBar.setAttribute("id", inputValue);
  percentBar.setAttribute("class", "percentBar");
  percentBar.appendChild(percentBarColor);

  percentBarColor.appendChild(nbsp);
  percentBarColor.setAttribute("class", "percentBarColor");
  percentBarColor.setAttribute("id", inputValue + "Color");

  list.appendChild(option);
  list.appendChild(percentBar);

  options[inputValue] = 0;

  let percentage;
  if (totalVotes === 0) {
    percentage = 0;
  } else {
    percentage = 100 * (options[inputValue] / totalVotes);
  }

  console.log(typeof percentage, percentage);
  percentBarColor.setAttribute("style", `width:${percentage}%`);
  percentBar.appendChild(percentBarColor);

  console.log("options", options);

  document.getElementById("myUL").appendChild(list);
  document.getElementById("myInput").value = "";
}
