window.unity_startup = function () {
  console.log("Sending Messages.");

  var user_id = window.VIEW_OWNER_ID;
  var path = window.GAME_URL_PATH;
  var proc = (window.GAME_URL_BASE.substr("http://".length)).split(":");
  var host = proc[0]; // + path;
  var port = proc[1];

  console.log(window.GAME_URL_BASE);
  console.log("Host: " + host);
  console.log("Port: " + port);
  console.log("View owner: " + window.VIEW_OWNER_ID);

  SendMessage("World Manager", "SetGameURL", host);
  SendMessage("World Manager", "SetGamePort", parseInt(port));
  SendMessage("World Manager", "SetUserId", parseInt(user_id))
  SendMessage("World Manager", "EstablishConnection");
}

window.unity_shutdown = function() {
  // Tear down the current unity connection if present
}

function SendAllConnect() {
  window.UNITY_REGISTERED = true;

  if (!window.CONTEXT_REGISTERED)
    return;

  window.unity_startup();
}

function handler(err, url, line) {s
  // We use the socket.io.js from Dependencies/socket.io.js, so this
  // error should not affect our code
  if (url.endsWith("socket.io/socket.io.js")) {
      console.log("Error handler!");
      console.log(err);
      console.log(url);
      console.log(line);
      return true;
  }

  return false;
}
