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
    authToken: getCookie("auth"),
  });
});

socket.on("newMessage", function (messageSet) {
  console.log("messageSet" + messageSet);
  addMessagesToChat(messageSet["messages"]);
});

socket.on("poll_message", function (poll_message) {
  var test1 = poll_message["poll_message"];
  console.log(test1);

  var idea_input = test1["idea_input"];
  //console.log("Idea "+idea_input)
  var color = test1["color"];

  newElement_create(idea_input, color);
});

socket.on("allUsers", function (allUsers) {
  /* Format:
  {
    "code": <workplace_code>,
    "users":
    {
      <username>:<points>
    }
  }
  */
  var workplaceusers = allUsers["allUsers"];
  console.log(workplaceusers)
  let text2 = "";
  for (let i = 0; i < workplaceusers.length - 1; i++) {
    console.log(workplaceusers[i])
    text2 += "<span onclick=\"enterProfile('"+workplaceusers[i]+"')\" style=\"cursor: pointer;\">"+workplaceusers[i]+"</span><br>"
  }
  document.getElementById("workplaceUsers").innerHTML = text2;
});


socket.on("result_message", function (result_message) {
  var result_message = result_message["result_message"];
  var options_server = result_message["options_server"];
  var total_votes_server = result_message["total_votes_server"];
  total3 = parseInt(total_votes_server);

  totalVotes = total3;
  options = options_server;
  console.log("totalVotes" + totalVotes);
  console.log("options" + options);

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
  //handleOptions(options)
});

var currentTimestamp = '1980-12-05 23:14:02.338718'
var x = setInterval(timer, 1000);
clearInterval(x);

// Source: https://www.w3schools.com/howto/howto_js_countdown.asp
// With some slight modifications for this specific implementation, of course
function timer() {
  // today
  var nowDate = new Date()
  nowDate = new Date(nowDate.toUTCString())//.replace("GMT", ""))
  var now = nowDate.getTime();
  var soon = new Date(currentTimestamp).getTime()
  console.log(currentTimestamp, nowDate)
  var timezone = nowDate.getTimezoneOffset()*60*1000
  console.log(new Date(currentTimestamp), nowDate, timezone)
  console.log(soon, now)

  var diff = soon - now //- timezone;
  console.log(diff)
  
  var minutes = Math.floor(diff / (1000 * 60));
  var seconds = Math.floor(diff % (1000*60) / 1000);

  if (seconds < 10) {
    seconds = "0" + String(seconds)
  }
  
  document.getElementById("timerThing").innerHTML = minutes + ":" + seconds
  
  if (diff < 0) {
    document.getElementById("timerThing").classList.remove("runningTimer"); 
    document.getElementById("timerThing").classList.add("expiredTimer")
    document.getElementById("timerThing").innerHTML = "EXPIRED"

    clearInterval(x)
  }
  else {
   document.getElementById("timerThing").classList.remove("expiredTimer")   
    document.getElementById("timerThing").classList.add("runningTimer")
  }
}




function startTimer() {
  x = setInterval(timer, 1000);
}

function setNewQuestion(question) {
  document.getElementById("questionInput").value = question
}

socket.on("updatedQuestion", function (updatedQuestion) {
  console.log(updatedQuestion)

  clearInterval(x)
  setNewQuestion(updatedQuestion["updatedQuestion"]);
  
  currentTimestamp = updatedQuestion["timestamp"]
  startTimer()
});

socket.on("dataDebrief", function (data) {
  clearInterval(x)
  question = data["question"]
  setNewQuestion(question)
  currentTimestamp = data["timestamp"]
  startTimer()
})

const thisPath = window.location.pathname;
var splitPath = thisPath.split("/");
var thisWorkplaceCode = splitPath.pop();
console.log(thisWorkplaceCode);
while (thisWorkplaceCode.trim() == "") {
  thisWorkplaceCode = splitPath.pop();
}

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
        comment: comment,
        workplaceCode: thisWorkplaceCode,
        authToken: getCookie("auth"),
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

  socket.send(
    JSON.stringify({
      options_server: options,
      totalVotes_server: totalVotes,
      workplaceCode: thisWorkplaceCode,
    })
  );

  console.log("total", totalVotes);
}

// Send updated question to websocket
function sendQuestion() {
  const updatedQuestion = document.getElementById("questionInput").value;
  var questionExpirySeconds = document.getElementById("questionExpiryInput").value;
  document.getElementById("questionExpiryInput").value = "";
  if (questionExpirySeconds.trim() == "") {
    questionExpirySeconds = "60";
  }

  questionExpirySeconds = Number(questionExpirySeconds);
  socket.send(
    JSON.stringify({
      updatedQuestion: updatedQuestion,
      workplaceCode: thisWorkplaceCode,
      questionExpirySeconds: questionExpirySeconds
    })
  );
}

// Create a new list item when clicking on the "Add" button
function newElement() {
  const inputValue = document.getElementById("myInput").value;
  getColor();
  color = getCookie("color");
  if (color === "None") {
    addColor();
    color = getCookie("color");
  }

  if (inputValue === "") {
    alert("You must write something");
    return;
  } else if (inputValue in options) {
    alert("You must create a new option");
    return;
  }

  // EJ
  const question = document.getElementById("questionInput").value;
  const idea = document.getElementById("myInput").value;
  console.log("question", question);
  console.log("idea", idea);

  socket.send(
    JSON.stringify({
      question_input: question,
      idea_input: idea,
      workplaceCode: thisWorkplaceCode,
      color: color,
    })
  );
}

function newElement_create(inputValue, color) {
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

  //The line below will cause some errors, no color now but will fix it later
  // Should work now -Matthew
  option.setAttribute("style", `background-color: ${color}`);

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

function userColor() {
  hsl =
    "hsl(" +
    360 * Math.random() +
    "," +
    (25 + 70 * Math.random()) +
    "%," +
    (85 + 10 * Math.random()) +
    "%)";
  hex = hslToHex(
    360 * Math.random(),
    25 + 70 * Math.random(),
    85 + 10 * Math.random()
  );
  return hex;
}

// Convert hsl to hex color
//https://stackoverflow.com/a/44134328
function hslToHex(h, s, l) {
  l /= 100;
  const a = (s * Math.min(l, 1 - l)) / 100;
  const f = (n) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color)
      .toString(16)
      .padStart(2, "0"); // convert to Hex and prefix "0" if needed
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

function addColor() {
  let xhr = new XMLHttpRequest();
  paths = window.location.pathname.split("/");
  code = paths[2];

  xhr.open("POST", "/usercolor/" + code, false);
  xhr.setRequestHeader(
    "content-type",
    "application/x-www-form-urlencoded;charset=UTF-8"
  );
  xhr.onload = function () {
    // Process our return data
    if (xhr.status >= 200 && xhr.status < 300) {
      // Runs when the request is successful
      document.cookie = "color=" + xhr.responseText;
    } else {
      // Runs when it's not
      document.cookie = "color=None";
    }
  };
  xhr.send("color=" + userColor());
}

function getColor() {
  let xhr = new XMLHttpRequest();
  paths = window.location.pathname.split("/");
  code = paths[2];
  xhr.open("GET", "/usercolor/" + code, false);
  xhr.onload = function () {
    // Process our return data
    if (xhr.status >= 200 && xhr.status < 300) {
      // Runs when the request is successful
      document.cookie = "color=" + xhr.responseText;
    } else {
      // Runs when it's not
      document.cookie = "color=None";
    }
  };
  xhr.send();
}

function enterProfile(user) {
  window.location.replace("/user/" + user + "/");
}
