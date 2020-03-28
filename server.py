import eventlet
import socketio


# *============================================================= SERVER INIT
static_files = {
    '/': 'pages/index.html'
}

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=static_files)

port = 8000


# *============================================================= MAIN
def main():
    eventlet.wsgi.server(eventlet.listen(('', port)), app)


# *============================================================= ENTRYPOINT
if __name__ == '__main__':
    main()
