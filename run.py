# run.py
from app import create_app, socketio
from app.services.vessel_lookup import init_flag_db

init_flag_db()

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
