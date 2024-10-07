
import cv2
import mysql.connector
from mysql.connector import Error
from pyzbar.pyzbar import decode
from PIL import Image

# Function to scan QR code from image
def scan_qr_code(image_path):
    try:
        img = Image.open(image_path)
        decoded_objects = decode(img)
        for obj in decoded_objects:
            parent_id_str = obj.data.decode('utf-8')
            parent_id = parent_id_str.split('/')[-1]  # Extract the ID
            print(f"QR Code Detected: {parent_id}")
            return parent_id
    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

# Function to scan QR code continuously using the webcam
def scan_qr_code_from_webcam_continuous():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return None

    detected_ids = set() 

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from webcam.")
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            parent_id_str = obj.data.decode('utf-8')
            parent_id = parent_id_str.split('/')[-1]  # Extract the ID

            # Only process if it's a new QR code that hasn't been scanned yet
            if parent_id not in detected_ids:
                print(f"QR Code Detected: {parent_id}")
                detected_ids.add(parent_id)  # Mark the QR code as scanned
                fetch_students_by_parent_id(parent_id)  # Fetch students linked to the parent ID

        # Display the webcam feed
        cv2.imshow("QR Code Scanner", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to fetch students by parent ID from the database
def fetch_students_by_parent_id(parent_id):
    connection = None  # Initialize connection variable
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
            SELECT s.student_id, s.student_name, s.grade
            FROM Students s
            JOIN Parent_Student ps ON s.student_id = ps.student_id
            WHERE ps.parent_id = %s
            """
            cursor.execute(query, (parent_id,))
            records = cursor.fetchall()

            if records:
                print(f"Students found for parent ID {parent_id}:")
                for row in records:
                    print(f"Student ID: {row[0]}, Student Name: {row[1]}, Grade: {row[2]}")
            else:
                print(f"No students found for parent ID {parent_id}.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection is not None and connection.is_connected():  # Check if connection is initialized
            cursor.close()
            connection.close()

# Main execution
if __name__ == "__main__":
    # Prompt the user for the option: Image file or Webcam
    option = input("Do you want to scan from (1) Image file or (2) Webcam? Enter 1 or 2: ")

    parent_id = None

    if option == '1':
        # Prompt the user for the image path
        image_path = input("Please enter the path to the QR code image (e.g., C:/xampp/htdocs/pick_up/your_qr_code_image.png): ")
        parent_id = scan_qr_code(image_path)
        if parent_id:
            fetch_students_by_parent_id(parent_id)
    elif option == '2':
        # Start continuous scanning from the webcam
        scan_qr_code_from_webcam_continuous()
