import sys
from datetime import datetime
import serial
import serial.tools.list_ports
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading

app = Flask(__name__)
socketio = SocketIO(app)
serial_port = None
running = False

def get_available_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

@app.route('/')
def index():
    ports = get_available_ports()
    return render_template('index.html', ports=ports)

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('ports', get_available_ports())
    emit('port_state', {'is_open': serial_port is not None and serial_port.is_open})

@socketio.on('open_port')
def open_port(data):
    global serial_port, running
    port = data.get('port')
    baud = int(data.get('baud', 115200))
    try:
        serial_port = serial.Serial(port, baud, timeout=0.1)
        running = True
        emit('log', {'message': f"Connected to {port} at {baud} baud", 'type': 'system'})
        emit('port_state', {'is_open': True})
        threading.Thread(target=listen_for_data, daemon=True).start()
    except Exception as e:
        emit('log', {'message': f"Error opening port: {str(e)}", 'type': 'system'})
        emit('port_state', {'is_open': False})

@socketio.on('close_port')
def close_port():
    global serial_port, running
    if serial_port and serial_port.is_open:
        running = False
        serial_port.close()
        emit('log', {'message': "Serial port closed", 'type': 'system'})
        emit('port_state', {'is_open': False})
    else:
        emit('log', {'message': "No port open to close", 'type': 'system'})
        emit('port_state', {'is_open': False})

@socketio.on('send_data')
def send_data(data):
    global serial_port
    message = data.get('message')
    if serial_port and serial_port.is_open and message:
        try:
            serial_port.write(message.encode('utf-8'))
            timestamp = datetime.now().strftime("%H:%M:%S")
            emit('log', {'message': f"{timestamp}<br>{message}", 'type': 'sent'})
        except Exception as e:
            emit('log', {'message': f"Error sending: {str(e)}", 'type': 'system'})
    else:
        emit('log', {'message': "Port not open or no message", 'type': 'system'})

@socketio.on('clear_history')
def clear_history():
    # Optional: Log the clear action on the server
    print("History cleared by client")
    emit('log', {'message': "Chat history cleared", 'type': 'system'})

def listen_for_data():
    global serial_port, running
    while running and serial_port and serial_port.is_open:
        try:
            if serial_port.in_waiting > 0:
                data = serial_port.read(serial_port.in_waiting).decode('utf-8', errors='ignore')
                if data:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    socketio.emit('log', {'message': f"{timestamp}<br>{data}", 'type': 'received'})
            else:
                threading.Event().wait(0.01)
        except Exception as e:
            socketio.emit('log', {'message': f"Error reading data: {str(e)}", 'type': 'system'})

if __name__ == "__main__":
    print("Starting web server at http://127.0.0.1:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)