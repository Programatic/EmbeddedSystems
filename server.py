import asyncio
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

frame = ''
alert_to = 'fms34@case.edu'

class WebServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path != "/":
            super().do_GET()
            return

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
 
    <title>Basic Web Panel</title>
 
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

sockets = []

async def handler(websocket, path):
    global sockets
    global frame

    sockets.append(websocket)
    while True:
        for soc in sockets:
            try:
                await soc.send(frame) 
            except:
                pass

async def ws():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future() 

def run_ws_server():
    asyncio.run(ws())

def run_web_server():
    webServer = HTTPServer(("0.0.0.0", 8080), WebServer)
    thread = Thread(target = webServer.serve_forever)
    thread.start() 

    wsthread = Thread(target = run_ws_server)
    wsthread.start()