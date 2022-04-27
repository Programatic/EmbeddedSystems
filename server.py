import asyncio
import websockets
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

frame = ''

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("""
        <!DOCTYPE html>
 
<html lang="en">
 
<head>
 
    <meta charset="UTF-8">
 
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
 
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
 
    <title>WebSocker Client</title>
 
</head>
 
<body>
    <img width="640" height="480">
 
</body>
 
<script>
    const img = document.querySelector('img');
 
    const socket = new WebSocket('ws://' + window.location.hostname + ':8000');
 
socket.addEventListener('open', function (event) {
 
    socket.send('Connection Established');
 
});
 
 
 
socket.onmessage = function (event) {
    // console.log(event.data);
    img.src = 'data:image/jpeg;base64,' + event.data;
 
    return false;
};
 
</script>
 
</html>
        """, "utf-8"))
        # self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        # self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        # self.wfile.write(bytes("<body>", "utf-8"))
        # self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        # self.wfile.write(bytes("</body></html>", "utf-8"))

sockets = []

async def handler(websocket, path):
    global sockets
    global frame

    sockets.append(websocket)
    while True:
        for soc in sockets:
            await soc.send(frame) 

async def ws():
    async with websockets.serve(handler, "192.168.1.23", 8000):
        await asyncio.Future() 

def run_ws_server():
    asyncio.run(ws())

def run_web_server():
    webServer = HTTPServer(("192.168.1.23", 8080), WebServer)
    thread = Thread(target = webServer.serve_forever)
    thread.start() 

    wsthread = Thread(target = run_ws_server)
    wsthread.start()