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

// Collect form data
$parent_name = $_POST['parent_name'];
$phone_number = $_POST['phone_number'];
$student_id = $_POST['student_id']; 
$student_name = $_POST['student_name'];
$grade = $_POST['grade'];
$existing_parent = isset($_POST['existing_parent']);
$parent_id = $_POST['parent_id'] ?? null; 

// Handle Parent Registration or Retrieval
if ($existing_parent && !empty($parent_id)) {
    // If the parent already exists, retrieve parent details using parent_id
    $query = $conn->prepare("SELECT * FROM Parents WHERE parent_id = ?");
    $query->execute([$parent_id]);
    $parent = $query->fetch(PDO::FETCH_ASSOC);
    
    if (!$parent) {
        echo "Error: Parent not found!";
        exit;
    }
} else {
    // If the parent is new, insert into the Parents table
    $query = $conn->prepare("INSERT INTO Parents (parent_name, phone_number) VALUES (?, ?)");
    $query->execute([$parent_name, $phone_number]);
    $parent_id = $conn->lastInsertId(); // Get the newly inserted parent ID

    // QR Code generation
    $qr_code_file = "qr_codes/" . preg_replace('/[^a-zA-Z0-9_]/', '_', $parent_name) . "_" . preg_replace('/[^a-zA-Z0-9_]/', '_', $student_name) . ".png";
    // $qr_code_url = "https://your-system.com/parent/" . $parent_id; 
    generate_qr_code($qr_code_url, $qr_code_file);

    // Update the Parent table to save the QR code path for the parent
    $query = $conn->prepare("UPDATE Parents SET qr_code = ? WHERE parent_id = ?");
    $query->execute([$qr_code_file, $parent_id]);
}

// Insert the student into the Students table
$query = $conn->prepare("INSERT INTO Students (student_id, student_name, grade) VALUES (?, ?, ?)");
$query->execute([$student_id, $student_name, $grade]);

// Link the parent and the student in the Parent_Student table
$names = $parent_name . " - " . $student_name; 
$query = $conn->prepare("INSERT INTO Parent_Student (parent_id, student_id, names) VALUES (?, ?, ?)");
$query->execute([$parent_id, $student_id, $names]);

echo "Parent and Student Registered Successfully!";

// Function to generate QR code
function generate_qr_code($data, $file_path) {
    $result = Builder::create()
        ->writer(new PngWriter())
        ->writerOptions([])
        ->data($data)
        ->encoding(new Encoding('UTF-8'))
        ->errorCorrectionLevel(new ErrorCorrectionLevelLow()) // Low error correction level
        ->size(300) // Size of the QR code
        ->margin(10) // Margin around the QR code
        ->build();

    // Save the generated QR code as a PNG file
    $result->saveToFile($file_path);
}

?>
