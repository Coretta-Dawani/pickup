-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 04, 2024 at 09:14 AM
-- Server version: 11.5.2-MariaDB
-- PHP Version: 7.4.24

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pick_up_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `parents`
--

CREATE TABLE `parents` (
  `parent_id` int(11) NOT NULL,
  `parent_name` varchar(255) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `qr_code` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parents`
--

INSERT INTO `parents` (`parent_id`, `parent_name`, `phone_number`, `qr_code`) VALUES
(2, 'Jessica Doe', '123-456-7890', 'qr_codes/Jessica_Doe_Jane_Doe.png'),
(3, 'Maren Mill', '123-456-7891', 'qr_codes/Maren_Mill_Maria_Mill.png'),
(4, 'Leilani Barajas', '123-456-7892', 'qr_codes/Leilani_Barajas_Davis_Barajas.png'),
(5, 'Maverick Wiley', '123-456-7893', 'qr_codes/Maverick_Wiley_Jay_Wiley.png'),
(6, 'Maria Fletcher', '123-456-7895', 'qr_codes/Maria_Fletcher_Oakley_Fletcher.png');

-- --------------------------------------------------------

--
-- Table structure for table `parent_student`
--

CREATE TABLE `parent_student` (
  `parent_student_id` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `student_id` varchar(50) NOT NULL,
  `names` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parent_student`
--

INSERT INTO `parent_student` (`parent_student_id`, `parent_id`, `student_id`, `names`) VALUES
(2, 2, '20240101', 'Jessica Doe - Jane Doe'),
(3, 2, '20240102', 'Jessica Doe - Joseph Doe'),
(4, 3, '20240201', 'Maren Mill - Maria Mill'),
(5, 4, '20240401', 'Leilani Barajas - Davis Barajas'),
(6, 5, '20240302', 'Maverick Wiley - Jay Wiley'),
(7, 6, '20240301', 'Maria Fletcher - Oakley Fletcher'),
(8, 6, '20240303', 'Maria Fletcher  - Finley Fletcher');

--
-- Triggers `parent_student`
--
DELIMITER $$
CREATE TRIGGER `after_parent_student_delete` AFTER DELETE ON `parent_student` FOR EACH ROW BEGIN
    DECLARE parent_count INT;

    -- Check if the parent has any remaining relationships
    SELECT COUNT(*) INTO parent_count FROM Parent_Student WHERE parent_id = OLD.parent_id;

    -- If no relationships, delete the parent
    IF parent_count = 0 THEN
        DELETE FROM Parents WHERE parent_id = OLD.parent_id;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `student_id` varchar(50) NOT NULL,
  `student_name` varchar(255) NOT NULL,
  `grade` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`student_id`, `student_name`, `grade`) VALUES
('20240101', 'Jane Doe', '1'),
('20240102', 'Joseph Doe', '1'),
('20240201', 'Maria Mill', '2'),
('20240301', 'Oakley Fletcher', '3'),
('20240302', 'Jay Wiley', '3'),
('20240303', 'Finley Fletcher', '3'),
('20240401', 'Davis Barajas', '4');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `parents`
--
ALTER TABLE `parents`
  ADD PRIMARY KEY (`parent_id`),
  ADD UNIQUE KEY `unique_parent` (`parent_name`,`phone_number`);

--
-- Indexes for table `parent_student`
--
ALTER TABLE `parent_student`
  ADD PRIMARY KEY (`parent_student_id`),
  ADD KEY `parent_id` (`parent_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`student_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `parents`
--
ALTER TABLE `parents`
  MODIFY `parent_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `parent_student`
--
ALTER TABLE `parent_student`
  MODIFY `parent_student_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `parent_student`
--
ALTER TABLE `parent_student`
  ADD CONSTRAINT `parent_student_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`parent_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `parent_student_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
