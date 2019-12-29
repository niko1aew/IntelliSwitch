from microWebSrv import MicroWebSrv
import json
import machine
from time import time

relay = None
dht11 = None
srv = None
DEBUG_MODE = None

def start_server(_relay=None, _dht11=None, _debugMode=False):
    """Run server at configured device"""
    print('Starting regular server...')

    global relay
    global dht11
    global srv
    global DEBUG_MODE

    if (_relay!=None and _dht11!=None):
        relay = _relay
        dht11 = _dht11
    DEBUG_MODE = _debugMode
    
    srv = MicroWebSrv(webPath='www/')
    srv.MaxWebSocketRecvLen = 256
    srv.WebSocketThreaded = True
    srv.AcceptWebSocketCallback = _acceptWebSocketCallback
    srv.Start(threaded=True)

def start_server_init():
    """Run server for device configuration"""
    print('Starting init server...')
    srv = MicroWebSrv(webPath='www/init/')
    srv.Start(threaded=False)

def _acceptWebSocketCallback(webSocket, httpClient):
    """Define action for new WS connection"""
    print("WS ACCEPT")
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = _closedCallback

def get_device_state():
    """Return device state as json object"""
    dht11.getMeasure()
    return '{"msg_type":"state", \
    "temperature":"'+str(dht11.temperature)+'", \
    "humidity":"'+str(dht11.humidity)+'", \
    "relay":"'+str(relay.state)+'"}'

def get_device_label():
    """Return device label as json object"""
    with open('config.json') as config_file:
        config = json.load(config_file)
    return '{"device_label":"%s"}' % config["LABEL"]

def process_command(json_cmd):
    """Parse json command from client"""
    global srv

    if "info" in json_cmd and json_cmd["info"] == "device_label":
        return get_device_label()

    if json_cmd["action"] == "device_state":
        return get_device_state()
    if json_cmd["action"] == "reboot":
        machine.reset()
    if json_cmd["action"] == "stop_server":
        print("Terminating...")
        srv.Stop()
    
    if json_cmd["dev_type"] is "relay":
        if json_cmd["action"] is "on":
            relay.switchON()
        elif json_cmd["action"] is "off":
            relay.switchOFF()
        elif json_cmd["action"] is "switch":
            relay.switchState()
        elif json_cmd["action"] is "get_state":
            return relay.getState()

    if json_cmd["dev_type"] is "dht11":
        if json_cmd["action"] is "get_state":
            return dht11.getState()
    return get_device_state()
    


                                  
def _recvTextCallback(webSocket, msg):
    if DEBUG_MODE:
        print("RECV:" + msg)
    if msg is "ping":
        webSocket.SendText("server_ok")
        return
    try:
        json_obj = json.loads(msg)
        response = process_command(json_obj)
        if DEBUG_MODE:
            print(response)
        webSocket.SendText(response)
    except Exception as e:
        print(str(e))
        webSocket.SendText("ECHO: %s" % msg)

def _recvBinaryCallback(webSocket, data):
    if DEBUG_MODE:
        print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket):
    print("WS CLOSED")

# Endpoint controllers-------------------------------------
@MicroWebSrv.route('/api', 'POST')
def _httpHandlerInitSettingsPost(httpClient, httpResponse):
    if DEBUG_MODE:
        print("api POST method")
    formData = httpClient.ReadRequestContentAsJSON()
    if DEBUG_MODE:
        print(formData)
    content=process_command(formData)
    if DEBUG_MODE:
        print("SEND: %s" % content)
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

@MicroWebSrv.route('/init_settings')
def _httpHandlerInitSettingsGet(httpClient, httpResponse):
    page = open('./www/init/index.html', 'r').read()
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=page)

@MicroWebSrv.route('/init_settings', 'POST')
def _httpHandlerInitSettingsPost(httpClient, httpResponse):
    print("POST")
    formData = httpClient.ReadRequestPostedFormData()
    with open('config.json') as config_file:
	    config = json.load(config_file)
    config['WIFI_SSID']=formData["ssid"]
    config['WIFI_PASS']=formData["pwd"]
    config['AUTO_IP_CONFIG']="YES"
    config['IS_CONFIGURED']="YES"
    with open('config.json', 'w') as f:
        json.dump(config, f,)
    content = "accepted"

    print('Config accepted')
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )
    machine.reset()
# -----------------------------------------------------