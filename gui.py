from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
import pyqtgraph as pg
import random
from packetGatherer import PacketGatherer

# Worker thread to gather packets in the background
class PacketGathererWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor

    def run(self):
        print(" Worker thread: capturing packets...")
        self.monitor.data = PacketGatherer()
        self.monitor.data.gather_packets("live")
        self.monitor.df = self.monitor.data.get_Dataframe()
        print(" Packet capture complete.")
        self.finished.emit()

# Live network monitor using background worker
class NetworkMonitor:
    def __init__(self):
        self.data = None
        self.df = None
        self.errors = 0
        self.total_connections = 0

        # Start looping live updates
        self.update_live_data()

    def update_live_data(self):
        print(" Starting live packet capture...")
        self.worker = PacketGathererWorker(self)
        self.worker.finished.connect(self.on_data_ready)
        self.worker.start()

    def on_data_ready(self):
        print("Packet data ready!")
        if self.df is not None and not self.df.empty:
            print("✅ Columns:", self.df.columns.tolist())
            print("✅ Sample:\n", self.df.head())

            # Start the timer only after we have real data
            self.start_timer()
        else:
            print("❌ DataFrame is None or empty")

    def start_timer(self):
        # Tell MainWindow to start the timer
        if hasattr(self, 'main_window'):
            self.main_window.start_auto_refresh()

        # Repeat every 10 seconds
        QTimer.singleShot(10000, self.update_live_data)

    def get_resend_data(self):
        if self.df is not None and not self.df.empty:
            print("✅ DataFrame is not None or empty")
            print("✅ DataFrame columns:", self.df.columns.tolist())
            if "packet_length" in self.df.columns:
                print("✅ Returning last 10 packet lengths")
                return self.df["packet_length"].tail(10).tolist()
            else:
                print("❌ 'packet_length' column not found")
        else:
            print("❌ DataFrame is None or empty")
        return [0] * 10

    def get_errors(self):
        self.errors += random.randint(0, 2)
        return self.errors

    def get_total_connections(self):
        self.total_connections += random.randint(1, 3)
        return self.total_connections

# Graph widget that visualizes data
class GraphWidget(pg.PlotWidget):
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self.plot = self.plot(pen="b")
        self.update_graph()

    def update_graph(self):
        new_data = self.monitor.get_resend_data()
        print("📈 Updating plot with data:", new_data)
        self.plot.setData(new_data)

# Main GUI window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CallQual - VoIP Quality Monitor")
        self.setGeometry(100, 100, 1024, 512)

        # Layout setup
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)

        # Graph setup
        self.network_monitor = NetworkMonitor()
        self.graph_widget = GraphWidget(self.network_monitor)
        self.main_layout.addWidget(self.graph_widget)

        self.network_monitor.main_window = self

        # Buttons
        self.buttons = [
            QPushButton("Errors/Dropped Packets"),
            QPushButton("Connection Quality"),
            QPushButton("General Graph"),
            QPushButton("Overall Log / Wireshark"),
            QPushButton("Settings"),
            QPushButton("Exit")
        ]
        self.buttons[0].clicked.connect(self.show_errors)
        self.buttons[1].clicked.connect(self.show_quality)
        self.buttons[2].clicked.connect(self.update_graph)
        self.buttons[3].clicked.connect(self.show_log)
        self.buttons[4].clicked.connect(self.show_settings)
        self.buttons[5].clicked.connect(self.close)

        for button in self.buttons:
            self.left_layout.addWidget(button)

        # Metrics
        self.errors_label = QLabel(f"Errors: {self.network_monitor.get_errors()}")
        self.total_connections_label = QLabel(f"Total Connections: {self.network_monitor.get_total_connections()}")
        self.right_layout.addWidget(self.errors_label)
        self.right_layout.addWidget(self.total_connections_label)

        # Auto-refresh graph every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)

        # Styling
        self.central_widget.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: 2px solid #2980b9;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QLabel {
                font-size: 14px;
                margin: 10px;
            }
        """)

    def start_auto_refresh(self):
        print("✅ Starting auto-refresh timer...")
        self.timer.start(5000)

    def update_graph(self):
        print("🔄 Updating graph...")
        self.graph_widget.update_graph()
        self.update_metrics()

    def update_metrics(self):
        self.errors_label.setText(f"Errors: {self.network_monitor.get_errors()}")
        self.total_connections_label.setText(f"Total Connections: {self.network_monitor.get_total_connections()}")

    def resizeEvent(self, event):
        button_width = max(144, self.width() // 8)
        button_height = max(52, self.height() // 10)
        for button in self.buttons:
            button.setFixedSize(button_width, button_height)

    def show_errors(self):
        QMessageBox.information(self, "Errors", "Displaying dropped packet errors.")

    def show_quality(self):
        QMessageBox.information(self, "Connection Quality", "Displaying connection quality metrics.")

    def show_log(self):
        QMessageBox.information(self, "Log", "Showing log and Wireshark info.")

    def show_settings(self):
        QMessageBox.information(self, "Settings", "Displaying settings panel.")

# Standalone run
if __name__ == "__main__":
    app = QApplication([])
    print(" Starting app...")
    window = MainWindow()
    print(" Creating main window...")
    window.show()
    print(" Entering app loop...")
    app.exec()



# from PyQt6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QVBoxLayout,
#     QHBoxLayout, QPushButton, QLabel
# )
# from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
# import pyqtgraph as pg
# import random
# from packetGatherer import PacketGatherer

# # Worker thread to gather packets in the background
# class PacketGathererWorker(QThread):
#     finished = pyqtSignal()

#     def __init__(self, monitor):
#         super().__init__()
#         self.monitor = monitor

#     def run(self):
#         print(" Worker thread: capturing packets...")
#         self.monitor.data = PacketGatherer()
#         self.monitor.data.gather_packets("live")
#         self.monitor.df = self.monitor.data.get_Dataframe()
#         print(" Packet capture complete.")
#         self.finished.emit()

# # Live network monitor using background worker
# class NetworkMonitor:
#     def __init__(self):
#         self.data = None
#         self.df = None
#         self.errors = 0
#         self.total_connections = 0

#         # Start looping live updates
#         self.update_live_data()

#     def update_live_data(self):
#         print(" Starting live packet capture...")
#         self.worker = PacketGathererWorker(self)
#         self.worker.finished.connect(self.on_data_ready)
#         self.worker.start()

#     def on_data_ready(self):
#         print("Packet data ready!")
#         if self.df is not None and not self.df.empty:
#             print("✅ Columns:", self.df.columns.tolist())
#             print("✅ Sample:\n", self.df.head())

#             # Start the timer only after we have real data
#             self.start_timer()
#         else:
#             print("❌ DataFrame is None or empty")

#     def start_timer(self):
#         # Tell MainWindow to start the timer
#         if hasattr(self, 'main_window'):
#             self.main_window.start_auto_refresh()

#         # Repeat every 10 seconds
#         QTimer.singleShot(10000, self.update_live_data)

#     def get_resend_data(self):
#         if self.df is not None and not self.df.empty:
#             print("✅ DataFrame is not None or empty")
#             print("✅ DataFrame columns:", self.df.columns.tolist())
#             if "packet_length" in self.df.columns:
#                 print("✅ Returning last 10 packet lengths")
#                 return self.df["packet_length"].tail(10).tolist()
#             else:
#                 print("❌ 'packet_length' column not found")
#         else:
#             print("❌ DataFrame is None or empty")
#         return [0] * 10

#     def get_errors(self):
#         self.errors += random.randint(0, 2)
#         return self.errors

#     def get_total_connections(self):
#         self.total_connections += random.randint(1, 3)
#         return self.total_connections

# # Graph widget that visualizes data
# class GraphWidget(pg.PlotWidget):
#     def __init__(self, monitor):
#         super().__init__()
#         self.monitor = monitor
#         self.plot = self.plot(pen="b")
#         self.update_graph()

#     def update_graph(self):
#         new_data = self.monitor.get_resend_data()
#         print("📈 Updating plot with data:", new_data)
#         self.plot.setData(new_data)

# # Main GUI window
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("CallQual - VoIP Quality Monitor")
#         self.setGeometry(100, 100, 1024, 512)

#         # Layout setup
#         self.central_widget = QWidget()
#         self.main_layout = QHBoxLayout()
#         self.central_widget.setLayout(self.main_layout)
#         self.setCentralWidget(self.central_widget)

#         self.left_layout = QVBoxLayout()
#         self.right_layout = QVBoxLayout()
#         self.main_layout.addLayout(self.left_layout)
#         self.main_layout.addLayout(self.right_layout)

#         # Graph setup
#         self.network_monitor = NetworkMonitor()
#         self.graph_widget = GraphWidget(self.network_monitor)
#         self.main_layout.addWidget(self.graph_widget)

#         self.network_monitor.main_window = self

#         # Buttons
#         self.buttons = [
#             QPushButton("Errors/Dropped Packets"),
#             QPushButton("Connection Quality"),
#             QPushButton("General Graph"),
#             QPushButton("Overall Log / Wireshark"),
#             QPushButton("Settings"),
#         ]
#         self.buttons[0].clicked.connect(self.show_errors)
#         self.buttons[1].clicked.connect(self.show_quality)
#         self.buttons[2].clicked.connect(self.update_graph)
#         self.buttons[3].clicked.connect(self.show_log)
#         self.buttons[4].clicked.connect(self.show_settings)

#         for button in self.buttons:
#             self.left_layout.addWidget(button)

#         # Metrics
#         self.errors_label = QLabel(f"Errors: {self.network_monitor.get_errors()}")
#         self.total_connections_label = QLabel(f"Total Connections: {self.network_monitor.get_total_connections()}")
#         self.right_layout.addWidget(self.errors_label)
#         self.right_layout.addWidget(self.total_connections_label)

#         # Auto-refresh graph every 5 seconds
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_graph)

#         # Styling
#         self.central_widget.setStyleSheet("""
#             QPushButton {
#                 background-color: #3498db;
#                 color: white;
#                 border: 2px solid #2980b9;
#                 border-radius: 4px;
#                 padding: 4px 8px;
#                 font-size: 12px;
#             }
#             QPushButton:hover {
#                 background-color: #5dade2;
#             }
#             QPushButton:pressed {
#                 background-color: #1f618d;
#             }
#             QLabel {
#                 font-size: 14px;
#                 margin: 10px;
#             }
#         """)

#     def start_auto_refresh(self):
#         print("✅ Starting auto-refresh timer...")
#         self.timer.start(5000)

#     def update_graph(self):
#         print("🔄 Updating graph...")
#         self.graph_widget.update_graph()
#         self.update_metrics()

#     def update_metrics(self):
#         self.errors_label.setText(f"Errors: {self.network_monitor.get_errors()}")
#         self.total_connections_label.setText(f"Total Connections: {self.network_monitor.get_total_connections()}")

#     def resizeEvent(self, event):
#         button_width = max(144, self.width() // 8)
#         button_height = max(52, self.height() // 10)
#         for button in self.buttons:
#             button.setFixedSize(button_width, button_height)

#     def show_errors(self):
#         print("Showing errors...")

#     def show_quality(self):
#         print("Showing quality...")

#     def show_log(self):
#         print("Showing log...")

#     def show_settings(self):
#         print("Showing settings...")

# # Standalone run
# if __name__ == "__main__":
#     app = QApplication([])
#     print(" Starting app...")
#     window = MainWindow()
#     print(" Creating main window...")
#     window.show()
#     print(" Entering app loop...")
#     app.exec()
