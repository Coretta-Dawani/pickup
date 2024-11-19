import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from pyzbar.pyzbar import decode
from PIL import Image
import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime

# Function to fetch students by parent ID from the database
def fetch_students_by_parent_id(parent_id, result_window, csv_writer):
    connection = None 
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='pick_up_db',
            user='root',
            password='', 
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = """
            SELECT p.parent_name, s.student_id, s.student_name, s.grade
            FROM Parents p
            JOIN Parent_Student ps ON p.parent_id = ps.parent_id
            JOIN Students s ON s.student_id = ps.student_id
            WHERE ps.parent_id = %s
            """
            cursor.execute(query, (parent_id,))
            records = cursor.fetchall()

            if records:
                # Format results for each student
                results = []
                for row in records:
                    parent_name = row[0]
                    student_id = row[1]
                    student_name = row[2]
                    grade = row[3]
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Append formatted results
                    results.append(
                        f"Parent ID: {parent_id}\n"
                        f"Parent Name: {parent_name}\n"
                        f"Student ID: {student_id}\n"
                        f"Student Name: {student_name}\n"
                        f"Grade: {grade}\n"
                        f"Time: {timestamp}\n"
                    )

                    # Write to the CSV file
                    csv_writer.writerow([parent_name, student_name, student_id, grade, timestamp])

                # Update the result window with the new results
                result_window.update_results(results)
            else:
                result_window.update_results([f"No students found for parent ID {parent_id}."])
    except Error as e:
        result_window.update_results([f"Error: {e}"])
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Function to scan QR code from image
def scan_qr_code_from_image(image_path, result_window, csv_writer):
    try:
        img = Image.open(image_path)
        decoded_objects = decode(img)
        for obj in decoded_objects:
            parent_id_str = obj.data.decode('utf-8')
            parent_id = parent_id_str.split('/')[-1]  # Extract the ID
            result_window.update_results([f"QR Code Detected: {parent_id}"])  # Update results in the window
            fetch_students_by_parent_id(parent_id, result_window, csv_writer)  # Fetch students linked to the parent ID
            return
        result_window.update_results(["No QR code found in the image."])
    except FileNotFoundError:
        result_window.update_results([f"Error: The file '{image_path}' was not found."])
    except Exception as e:
        result_window.update_results([f"An error occurred: {e}"])

# Result Window Class for displaying database results
class ResultWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Scanner Results")
        self.setGeometry(200, 200, 600, 400)

        # Main layout
        layout = QVBoxLayout()

        # Create a QLabel to display the header
        header_label = QLabel("QR Code Scan Results")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(header_label)

        # Create a QScrollArea to make the result text scrollable
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)  # Initialize layout here

        # Set the container widget for the scroll area
        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)  # Add the scroll area to the main layout

        # Set central widget with layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_results(self, results):
        # Clear previous results
        for i in reversed(range(self.scroll_layout.count())):  # Remove items in reverse order
            widget = self.scroll_layout.itemAt(i).widget()
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()  # Clean up to free memory

        # Add new results as QLabel
        for result in results:
            label = QLabel(result)  # Create a new label for each result
            label.setStyleSheet("font-size: 14px; color: #444; margin: 5px;")  # Style for the label
            self.scroll_layout.addWidget(label)  # Add label to the layout

# Main PyQt Window Class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QR Code Scanner")
        self.setGeometry(100, 100, 900, 600)

        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left side layout for webcam feed and control buttons
        left_layout = QVBoxLayout()

        # Create buttons for image or webcam option
        self.image_button = QPushButton("Scan from Image", self)
        self.image_button.clicked.connect(self.scan_from_image)

        self.webcam_button = QPushButton("Scan from DroidCam", self)
        self.webcam_button.clicked.connect(self.scan_from_webcam)

        # Label to display the webcam feed
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(640, 480)  # Set fixed size for webcam feed

        # quit button 
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)

        # Add widgets to the left layout
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(self.image_button)
        left_layout.addWidget(self.webcam_button)
        left_layout.addWidget(self.quit_button)

        # Add left layout to the main layout
        main_layout.addLayout(left_layout)

        # Set up a timer to update the webcam feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Placeholder for webcam feed
        self.cap = None

        # Open CSV file in append mode
        self.csv_file = open('pick_up_data/Pick Data.csv', mode='a', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write header to CSV if the file is new
        self.csv_writer.writerow(['Parent Name', 'Student Name', 'Student ID', 'Grade', 'Timestamp'])

        # Instantiate result window
        self.result_window = ResultWindow()

    def scan_from_image(self):
        # Open a file dialog to select an image
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.xpm *.jpg *.bmp)")
        if image_path:
            scan_qr_code_from_image(image_path, self.result_window, self.csv_writer)
            self.result_window.show()  # Display the result window

    def scan_from_webcam(self):
        # Attempt to open DroidCam feed via IP URL
        self.cap = cv2.VideoCapture("http://192.168.1.117:4747/video") 
        if not self.cap.isOpened():
            self.result_window.update_results(["Error: Could not open DroidCam feed"])
            self.result_window.show()
            return
        self.timer.start(20)  # Update every 20ms (~50 frames per second)
        self.result_window.show()

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Scan for QR codes
                decoded_objects = decode(frame)
                for obj in decoded_objects:
                    parent_id_str = obj.data.decode('utf-8')
                    parent_id = parent_id_str.split('/')[-1]  # Extract the ID

                    # Display detected QR code and fetch students
                    self.result_window.update_results([f"QR Code Detected: {parent_id}"])
                    fetch_students_by_parent_id(parent_id, self.result_window, self.csv_writer)

                # Convert the frame to RGB and display it in the QLabel
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap)

    def closeEvent(self, event):
        # close webcam and close the CSV file when the window is closed
        if self.cap:
            self.cap.release()
        self.csv_file.close()  
        event.accept()  

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
