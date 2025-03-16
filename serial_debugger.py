import sys
from datetime import datetime
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QMessageBox
)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
import threading

# Signal class for thread-safe UI updates
class SerialSignals(QObject):
    data_received = pyqtSignal(str)

class SerialDebugger(QWidget):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.running = False
        self.signals = SerialSignals()
        self.initUI()
        self.signals.data_received.connect(self.append_received_log)

    def initUI(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Serial port selection
        self.port_label = QLabel("Select Serial Port:")
        self.port_dropdown = QComboBox()
        self.refresh_ports()

        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)

        # Baud rate input
        self.baud_label = QLabel("Enter Baud Rate:")
        self.baud_input = QLineEdit()
        self.baud_input.setPlaceholderText("e.g., 115200")
        self.baud_input.setText("115200")

        # Port control buttons
        self.open_button = QPushButton("Open Port")
        self.open_button.clicked.connect(self.open_serial_port)
        self.close_button = QPushButton("Close Port")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.close_serial_port)

        # Log display (bubble bar)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        # Updated HTML with CSS
        self.log.setHtml("""
            <style>
                .bubble {padding: 5px 10px; border-radius: 10px; margin: 5px; max-width: 80%; word-wrap: break-word;}
                .sent {background-color: #FFD700; align-self: flex-end; float: right; clear: both;}
                .received {background-color: #FFD700; align-self: flex-start; float: left; clear: both;}
                .system {color: #555555; text-align: center;}
                .timestamp {font-size: 0.5em; color: #888888;}
            </style>
            <div id='chat'></div>
        """)

        # Input and send controls
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type message here...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_data)

        # Add widgets to layout
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_dropdown)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.baud_label)
        layout.addWidget(self.baud_input)
        layout.addWidget(self.open_button)
        layout.addWidget(self.close_button)
        layout.addWidget(self.log)
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
        self.setWindowTitle("Serial Debugger")
        self.resize(400, 300)

    def refresh_ports(self):
        """Refresh the list of available serial ports."""
        self.port_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        if ports:
            for port in ports:
                self.port_dropdown.addItem(port.device)
        else:
            self.append_log("No serial ports found.", "system")

    def open_serial_port(self):
        """Open the selected serial port."""
        port = self.port_dropdown.currentText()
        try:
            baud = int(self.baud_input.text())
            if baud <= 0:
                raise ValueError("Baud rate must be positive")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid baud rate! Enter a positive number.")
            return

        if not port:
            QMessageBox.warning(self, "Error", "No serial port selected!")
            return

        try:
            self.serial_port = serial.Serial(port, baud, timeout=0.1)
            self.append_log(f"Connected to {port} at {baud} baud", "system")
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.running = True
            self.listen_for_data()
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def close_serial_port(self):
        """Close the serial port."""
        if self.serial_port and self.serial_port.is_open:
            self.running = False
            self.serial_port.close()
            self.append_log("Serial port closed", "system")
            self.open_button.setEnabled(True)
            self.close_button.setEnabled(False)

    def send_data(self):
        """Send data over the serial port."""
        if self.serial_port and self.serial_port.is_open:
            message = self.input_field.text()
            if message:
                try:
                    self.serial_port.write(message.encode())
                    self.append_log(message, "sent")
                    self.input_field.clear()
                except Exception as e:
                    self.append_log(f"Error sending: {e}", "system")
            else:
                QMessageBox.warning(self, "Error", "Please enter a message to send.")
        else:
            QMessageBox.warning(self, "Error", "Serial port not open!")

    def listen_for_data(self):
        """Listen for incoming serial data in a separate thread."""
        def read_data():
            while self.running and self.serial_port and self.serial_port.is_open:
                try:
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting).decode('utf-8', errors='ignore')
                        if data:
                            self.signals.data_received.emit(data)
                    else:
                        threading.Event().wait(0.01)
                except Exception as e:
                    self.signals.data_received.emit(f"Error reading data: {e}")
                    break

        threading.Thread(target=read_data, daemon=True).start()

    def append_log(self, text, message_type):
        """Append a message to the log as a styled bubble with optional timestamp."""
        # Determine alignment and bubble class based on message type
        if message_type == "sent":
            alignment = "right"
            bubble_class = "sent"
        elif message_type == "received":
            alignment = "left"
            bubble_class = "received"
        else:
            alignment = "center"
            bubble_class = "system"

        # Process the content based on message type
        if message_type in ["sent", "received"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            text_processed = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            bubble_content = f'<div class="timestamp">{timestamp}</div><div>{text_processed}</div>'
        else:
            text_escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            bubble_content = text_escaped

        # Construct the bubble HTML with alignment container
        bubble_html = f'<div style="text-align: {alignment};">' \
                      f'<div class="bubble {bubble_class}">{bubble_content}</div>' \
                      f'</div>'

        # Append to the log and scroll to bottom
        self.log.append(bubble_html)
        scrollbar = self.log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def append_received_log(self, text):
        """Append received data to the log."""
        self.append_log(text, "received")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialDebugger()
    window.show()
    sys.exit(app.exec())