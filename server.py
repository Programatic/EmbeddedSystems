import asyncio
import websockets
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

frame = ''
frame2 = ''
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
    <a href="vids"> Videos of intruders! </a>
    <br>
    <img width="640" height="480">
    <img width="640" height="480">
</body>
 
<script>
    const img = document.querySelector('body > img:nth-child(3)');
    const img2 = document.querySelector('body > img:nth-child(4)');
 
    const socket = new WebSocket('ws://' + window.location.hostname + ':8000');
 
socket.addEventListener('open', function (event) {
 
    socket.send('Connection Established');
 
});
 
 
 
socket.onmessage = function (event) {
    // console.log(event.data);
    let data = event.data.split(' : ');
    img.src = 'data:image/jpeg;base64,' + data[0];
    img2.src = 'data:image/jpeg;base64,' + data[1];

    return false;
};
 
</script>
 
</html>
        """, "utf-8"))

sockets = []

async def handler(websocket, path):
    global sockets

    sockets.append(websocket)

    await asyncio.Future()

async def mass_send():
    global frame
    global sockets

    while True:
        for soc in sockets:
            try:
                await soc.send(frame + ' : ' + frame2) 
            except:
                pass


async def ws():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future() 

def mass():
    asyncio.run(mass_send())

def run_ws_server():
    Thread(target = mass).start()
    asyncio.run(ws())

def run_web_server():
    webServer = HTTPServer(("0.0.0.0", 8080), WebServer)
    thread = Thread(target = webServer.serve_forever)
    thread.start() 

    wsthread = Thread(target = run_ws_server)
    wsthread.start()