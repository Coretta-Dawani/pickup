<?php
require 'vendor/autoload.php';

use Endroid\QrCode\Builder\Builder;
use Endroid\QrCode\Encoding\Encoding;
use Endroid\QrCode\ErrorCorrectionLevel\ErrorCorrectionLevelLow;
use Endroid\QrCode\Writer\PngWriter;

// Database connection
$host = 'localhost';
$dbname = 'pick_up_db';
$username = 'root';
$password = '';
$conn = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
$conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Check the request method
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['delete_student_id'])) {
        // Delete a student
        $student_id = $_POST['delete_student_id'];
        deleteStudent($conn, $student_id);
    } else {
        // Handle parent and student registration
        registerParentAndStudent($conn);
    }
} elseif ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['action']) && $_GET['action'] === 'list_students') {
    // List all students
    listStudents($conn);
} else {
    echo json_encode(["error" => "Invalid request method or parameters"]);
    exit;
}

// Function to register parent and student
function registerParentAndStudent($conn) {
    $parent_name = htmlspecialchars($_POST['parent_name']);
    $phone_number = htmlspecialchars($_POST['phone_number']);
    $student_id = htmlspecialchars($_POST['student_id']); 
    $student_name = htmlspecialchars($_POST['student_name']);
    $grade = htmlspecialchars($_POST['grade']);
    $existing_parent = isset($_POST['existing_parent']);
    $parent_id = $_POST['parent_id'] ?? null; 

    try {
        // Handle Parent Registration or Retrieval
        if ($existing_parent && !empty($parent_id)) {
            // Retrieve existing parent
            $query = $conn->prepare("SELECT * FROM Parents WHERE parent_id = ?");
            $query->execute([$parent_id]);
            $parent = $query->fetch(PDO::FETCH_ASSOC);
            
            if (!$parent) {
                echo json_encode(["error" => "Parent not found"]);
                exit;
            }
        } else {
            // Insert new parent
            $query = $conn->prepare("INSERT INTO Parents (parent_name, phone_number) VALUES (?, ?)");
            $query->execute([$parent_name, $phone_number]);
            $parent_id = $conn->lastInsertId();

            // Generate QR code
            $qr_code_file = "qr_codes/" . preg_replace('/[^a-zA-Z0-9_]/', '_', $parent_name) . "_" . preg_replace('/[^a-zA-Z0-9_]/', '_', $student_name) . ".png";
            generate_qr_code($parent_id, $qr_code_file);

            // Update Parent table with QR code path
            $query = $conn->prepare("UPDATE Parents SET qr_code = ? WHERE parent_id = ?");
            $query->execute([$qr_code_file, $parent_id]);
        }

        // Check if student ID already exists
        $query = $conn->prepare("SELECT * FROM Students WHERE student_id = ?");
        $query->execute([$student_id]);
        if ($query->fetch()) {
            echo json_encode(["error" => "Student ID already exists"]);
            exit;
        }

        // Insert student
        $query = $conn->prepare("INSERT INTO Students (student_id, student_name, grade) VALUES (?, ?, ?)");
        $query->execute([$student_id, $student_name, $grade]);

        // Link parent and student
        $names = $parent_name . " - " . $student_name; 
        $query = $conn->prepare("INSERT INTO Parent_Student (parent_id, student_id, names) VALUES (?, ?, ?)");
        $query->execute([$parent_id, $student_id, $names]);

        echo json_encode(["success" => "Parent and Student Registered Successfully"]);
    } catch (PDOException $e) {
        echo json_encode(["error" => $e->getMessage()]);
    }
}

// Function to generate QR code
function generate_qr_code($data, $file_path) {
    $result = Builder::create()
        ->writer(new PngWriter())
        ->writerOptions([])
        ->data($data)
        ->encoding(new Encoding('UTF-8'))
        ->errorCorrectionLevel(new ErrorCorrectionLevelLow())
        ->size(300)
        ->margin(10)
        ->build();

    $result->saveToFile($file_path);
}

// Function to delete a student by ID
function deleteStudent($conn, $student_id) {
    try {
        $query = $conn->prepare("DELETE FROM Parent_Student WHERE student_id = ?");
        $query->execute([$student_id]);
        
        $query = $conn->prepare("DELETE FROM Students WHERE student_id = ?");
        $query->execute([$student_id]);

        if ($query->rowCount() > 0) {
            echo json_encode(["success" => "Student with ID $student_id has been deleted successfully"]);
        } else {
            echo json_encode(["error" => "Student not found"]);
        }
    } catch (PDOException $e) {
        echo json_encode(["error" => $e->getMessage()]);
    }
}

// Function to list all students
function listStudents($conn) {
    try {
        $query = $conn->prepare("SELECT * FROM Students");
        $query->execute();
        $students = $query->fetchAll(PDO::FETCH_ASSOC);
        echo json_encode($students);
    } catch (PDOException $e) {
        echo json_encode(["error" => "Error fetching students: " . $e->getMessage()]);
    }
}
?>
