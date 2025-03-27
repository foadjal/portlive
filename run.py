import eventlet
eventlet.monkey_patch()

from app import create_app
from flask_socketio import SocketIO
from app.services.vessel_lookup import init_flag_db

app = create_app()
socketio = SocketIO(app, async_mode='eventlet')

init_flag_db()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
