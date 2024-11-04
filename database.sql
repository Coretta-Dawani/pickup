-- Create Parents table
CREATE TABLE IF NOT EXISTS Parents (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    qr_code VARCHAR(255) DEFAULT NULL,
    UNIQUE (parent_name, phone_number)
);

-- Create Students table
CREATE TABLE IF NOT EXISTS Students (
    student_id VARCHAR(50) PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL,
    grade VARCHAR(50) NOT NULL
);

-- Create Parent_Student table to link parents and students
CREATE TABLE IF NOT EXISTS Parent_Student (
    parent_student_id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    names VARCHAR(255) NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES Parents(parent_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);

-- Trigger to delete parent if no relationships exist
DELIMITER //
CREATE TRIGGER after_parent_student_delete
AFTER DELETE ON Parent_Student
FOR EACH ROW
BEGIN
    DECLARE parent_count INT;

    -- Check if the parent has any remaining relationships
    SELECT COUNT(*) INTO parent_count FROM Parent_Student WHERE parent_id = OLD.parent_id;

    -- If no relationships, delete the parent
    IF parent_count = 0 THEN
        DELETE FROM Parents WHERE parent_id = OLD.parent_id;
    END IF;
END;
//
DELIMITER ;
