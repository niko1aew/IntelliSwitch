
const connection_state_view = document.querySelector('#connection_state');
const room_temp_view = document.querySelector('#room_temp');
const room_humidity_view = document.querySelector('#room_hum');
const switch_button_view = document.querySelector('#switch_button');
const settings_button_view = document.querySelector('#settings_button');
const connection_block_view = document.querySelector('#connection_block');
const sensor_output_block_view = document.querySelector('#sensor_output_block');
var espSocket;
var isSupported = (("WebSocket" in window && window.WebSocket != undefined) ||
    ("MozWebSocket" in window));
switch_button_view.addEventListener('click', switchRelay);
settings_button_view.addEventListener('click', () => {
    window.location.href = './settings.html'
});

document.addEventListener("DOMContentLoaded", onLoad);

setInterval(() => {
    if (espSocket) {
        try {
            let socketState = getStringSocketState();
            showSocketState(socketState);

            switch (socketState) {
                case "OPEN":
                    getLightBulbState();
                    getDHT11state();
                    break;
                case "CLOSED":
                    console.warn('Sokcet closed. Attepting to reconnect...')
                    createSocket()
            }
        } catch (e) {
            console.error("Sync error: " + e)
        }
    }

}, 5000);

function createSocket() {

    espSocket = new WebSocket("ws://"+device_ip);

    espSocket.addEventListener('error', (err) => {
        console.error('socket error: ', err)
    })
    espSocket.addEventListener('close', (event) => {

        if (event.code == 1000)
            reason = "Normal closure, meaning that the purpose for which the connection was established has been fulfilled.";
        else if (event.code == 1001)
            reason = "An endpoint is \"going away\", such as a server going down or a browser having navigated away from a page.";
        else if (event.code == 1002)
            reason = "An endpoint is terminating the connection due to a protocol error";
        else if (event.code == 1003)
            reason = "An endpoint is terminating the connection because it has received a type of data it cannot accept (e.g., an endpoint that understands only text data MAY send this if it receives a binary message).";
        else if (event.code == 1004)
            reason = "Reserved. The specific meaning might be defined in the future.";
        else if (event.code == 1005)
            reason = "No status code was actually present.";
        else if (event.code == 1006)
            reason = "The connection was closed abnormally, e.g., without sending or receiving a Close control frame";
        else if (event.code == 1007)
            reason = "An endpoint is terminating the connection because it has received data within a message that was not consistent with the type of the message (e.g., non-UTF-8 [http://tools.ietf.org/html/rfc3629] data within a text message).";
        else if (event.code == 1008)
            reason = "An endpoint is terminating the connection because it has received a message that \"violates its policy\". This reason is given either if there is no other sutible reason, or if there is a need to hide specific details about the policy.";
        else if (event.code == 1009)
            reason = "An endpoint is terminating the connection because it has received a message that is too big for it to process.";
        else if (event.code == 1010)
            reason = "An endpoint (client) is terminating the connection because it has expected the server to negotiate one or more extension, but the server didn't return them in the response message of the WebSocket handshake. <br /> Specifically, the extensions that are needed are: " + event.reason;
        else if (event.code == 1011)
            reason = "A server is terminating the connection because it encountered an unexpected condition that prevented it from fulfilling the request.";
        else if (event.code == 1015)
            reason = "The connection was closed due to a failure to perform a TLS handshake (e.g., the server certificate can't be verified).";
        else
            reason = "Unknown reason";
        console.log(event.code, reason)
        switch_button_view.style.display = 'none'
        sensor_output_block_view.style.display = 'none'
        connection_block_view.style.display = ''
    })

    espSocket.addEventListener('open', () => {
        console.log('socket open')
        switch_button_view.style.removeProperty('display');
        connection_block_view.style.display = 'none'
        sensor_output_block_view.style.removeProperty('display');
        showSocketState(getStringSocketState());;
        getLightBulbState();
        getDHT11state();
    })

    espSocket.addEventListener('message', (event) => {
        try {
            let jMSG = JSON.parse(event.data);
            if (jMSG.dev_type) {
                switch (jMSG.dev_type) {
                    case "relay":
                        showLightStateFromMsg(jMSG);
                        break;
                    case "dht11":
                        showDHT11stateFromMsg(jMSG);
                        break;
                }
            }
            if (jMSG.msg_type) {
                switch (jMSG.msg_type) {
                    case "state":
                        updateViewState(jMSG);
                        break;
                }
            }
            
        } catch {
            console.error("Failed to handle server message: " + event.data);
        }
    })

}

function updateViewState(jMSG){
    switch_button_view.textContent = `Switch light ${jMSG.relay==="True" ? "OFF" : "ON"}`;
    room_temp_view.innerHTML = `${jMSG.temperature}&deg;C`;
    room_humidity_view.innerHTML = `${jMSG.humidity}`;
}

function switchRelay() {
    if (espSocket.readyState == 1)
        espSocket.send('{"dev_type":"relay", "action":"switch"}');
    else {
        connectSocket();
        espSocket.send('{"dev_type":"relay", "action":"switch"}');
    }
}


function onSocketRecv(event) {
    // console.log('Server message:', event.data);

}

function onSocketOpen(event) {

}

function getStringSocketState() {
    let socketState = espSocket.readyState;
    switch (socketState) {
        case 0:
            return "CONNECTING"
        case 1:
            return "OPEN"
        case 2:
            return "CLOSING"
        case 3:

            return "CLOSED"
        default:
            return "UNKNOWN"
    }

}

function getLightBulbState() {
    try {
        if (espSocket.readyState == 1)
            espSocket.send('{"dev_type":"relay", "action":"get_state"}');
        else {
            showSocketState(getStringSocketState());
        }
    } catch {
        console.error('getStringSocketState():', getStringSocketState());
    }

}

function getDHT11state() {
    let msgDht = '{"dev_type":"dht11", "action":"get_state"}';
    if (espSocket.readyState == 1)
        espSocket.send(msgDht);
    else {
        connectSocket();
        espSocket.send(msgDht);
    }
}

function showSocketState(state) {
    if (state != null)
        connection_state_view.innerHTML = state;
}

function showLightStateFromMsg(jMSG) {
    let light_state_str = '';
    if (jMSG.state == 'off') light_state_str = 'ON';
    else light_state_str = 'OFF';
    switch_button_view.textContent = `Switch light ${light_state_str}`;
}

function showDHT11stateFromMsg(jMSG) {
    room_temp_view.innerHTML = `${jMSG.temperature}&deg;C`;
    room_humidity_view.innerHTML = `${jMSG.humidity}`;
}

function onLoad() {
    if (!isSupported) {
        bulb_state_view.innerHTML("Browser is not supported!");
    }
    switch_button_view.style.display = 'none';
    sensor_output_block_view.style.display = 'none';
    createSocket();
    showSocketState(getStringSocketState());

}