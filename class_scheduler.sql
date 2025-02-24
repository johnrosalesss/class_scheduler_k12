-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Feb 21, 2025 at 08:43 AM
-- Server version: 11.5.2-MariaDB
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `class_scheduler`
--

-- --------------------------------------------------------

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
CREATE TABLE IF NOT EXISTS `rooms` (
  `room_id` varchar(10) NOT NULL,
  `room_name` varchar(50) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL,
  PRIMARY KEY (`room_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rooms`
--

INSERT INTO `rooms` (`room_id`, `room_name`, `capacity`) VALUES
('R001', 'Room 101', 30),
('R002', 'Room 102', 40),
('R003', 'Room 103', 50),
('R004', 'Room 104', 30),
('R005', 'Room 105', 40),
('R006', 'Room 106', 50),
('R007', 'Room 107', 30),
('R008', 'Room 108', 40),
('R009', 'Room 109', 50),
('R010', 'Room 110', 30),
('R011', 'Room 111', 40),
('R012', 'Room 112', 50),
('R013', 'Room 113', 30),
('R014', 'Room 114', 40),
('R015', 'Room 115', 50),
('R016', 'Room 116', 30),
('R017', 'Room 117', 40),
('R018', 'Room 118', 50),
('R019', 'Room 119', 30),
('R020', 'Room 120', 40);

-- --------------------------------------------------------

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
CREATE TABLE IF NOT EXISTS `schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_code` varchar(10) DEFAULT NULL,
  `teacher_name` varchar(100) DEFAULT NULL,
  `room_name` varchar(50) DEFAULT NULL,
  `day` varchar(10) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subject_code` (`subject_code`)
) ENGINE=MyISAM AUTO_INCREMENT=378 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `schedule`
--

INSERT INTO `schedule` (`id`, `subject_code`, `teacher_name`, `room_name`, `day`, `start_time`, `end_time`) VALUES
(325, 'DS102', 'Prof. Blue', 'Room 113', 'Monday', '14:00:00', '15:00:00'),
(326, 'DS102', 'Prof. Blue', 'Room 104', 'Monday', '15:00:00', '16:00:00'),
(327, 'DS102', 'Prof. Blue', 'Room 103', 'Wednesday', '16:00:00', '17:00:00'),
(328, 'IT102', 'Prof. Green', 'Room 101', 'Friday', '15:00:00', '16:00:00'),
(329, 'IT102', 'Prof. Green', 'Room 102', 'Wednesday', '07:00:00', '08:00:00'),
(330, 'IT102', 'Prof. Green', 'Room 104', 'Wednesday', '11:00:00', '12:00:00'),
(331, 'CS102', 'Prof. Jones', 'Room 119', 'Friday', '07:00:00', '08:00:00'),
(332, 'CS102', 'Prof. Jones', 'Room 110', 'Thursday', '08:00:00', '09:00:00'),
(333, 'CS102', 'Prof. Jones', 'Room 117', 'Tuesday', '07:00:00', '08:00:00'),
(334, 'CY101', 'Prof. Cyan', 'Room 116', 'Saturday', '13:00:00', '14:00:00'),
(335, 'CY101', 'Prof. Cyan', 'Room 115', 'Tuesday', '15:00:00', '16:00:00'),
(336, 'CY101', 'Prof. Cyan', 'Room 120', 'Saturday', '16:00:00', '17:00:00'),
(337, 'SE101', 'Prof. Red', 'Room 106', 'Wednesday', '14:00:00', '15:00:00'),
(338, 'SE101', 'Prof. Red', 'Room 103', 'Monday', '16:00:00', '17:00:00'),
(339, 'SE101', 'Prof. Red', 'Room 119', 'Tuesday', '13:00:00', '14:00:00'),
(340, 'DS101', 'Prof. Grey', 'Room 112', 'Thursday', '09:00:00', '10:00:00'),
(341, 'DS101', 'Prof. Grey', 'Room 112', 'Friday', '08:00:00', '09:00:00'),
(342, 'DS101', 'Prof. Grey', 'Room 101', 'Thursday', '11:00:00', '12:00:00'),
(343, 'IT101', 'Prof. White', 'Room 101', 'Tuesday', '11:00:00', '12:00:00'),
(344, 'IT101', 'Prof. White', 'Room 104', 'Saturday', '11:00:00', '12:00:00'),
(345, 'IT101', 'Prof. White', 'Room 102', 'Monday', '11:00:00', '12:00:00'),
(346, 'CS101', 'Prof. Smith', 'Room 117', 'Monday', '09:00:00', '10:00:00'),
(347, 'CS101', 'Prof. Smith', 'Room 116', 'Friday', '16:00:00', '17:00:00'),
(348, 'CS101', 'Prof. Smith', 'Room 106', 'Saturday', '08:00:00', '09:00:00'),
(349, 'SE102', 'Prof. Yellow', 'Room 104', 'Saturday', '10:00:00', '11:00:00'),
(350, 'SE102', 'Prof. Yellow', 'Room 104', 'Monday', '08:00:00', '09:00:00'),
(351, 'SE102', 'Prof. Yellow', 'Room 111', 'Monday', '10:00:00', '11:00:00'),
(352, 'CY102', 'Prof. Magenta', 'Room 117', 'Friday', '13:00:00', '14:00:00'),
(353, 'CY102', 'Prof. Magenta', 'Room 120', 'Saturday', '14:00:00', '15:00:00'),
(354, 'CY102', 'Prof. Magenta', 'Room 108', 'Thursday', '15:00:00', '16:00:00'),
(355, 'CS103', 'Prof. Brown', 'Room 109', 'Thursday', '10:00:00', '11:00:00'),
(356, 'CS103', 'Prof. Brown', 'Room 105', 'Friday', '10:00:00', '11:00:00'),
(357, 'CS103', 'Prof. Brown', 'Room 115', 'Friday', '11:00:00', '12:00:00'),
(358, 'IT103', 'Prof. Black', 'Room 113', 'Wednesday', '13:00:00', '14:00:00'),
(359, 'IT103', 'Prof. Black', 'Room 108', 'Tuesday', '08:00:00', '09:00:00'),
(360, 'DS103', 'Prof. Orange', 'Room 105', 'Wednesday', '15:00:00', '16:00:00'),
(361, 'DS103', 'Prof. Orange', 'Room 108', 'Wednesday', '10:00:00', '11:00:00'),
(362, 'DS103', 'Prof. Orange', 'Room 111', 'Tuesday', '09:00:00', '10:00:00'),
(363, 'SE103', 'Prof. Purple', 'Room 114', 'Wednesday', '09:00:00', '10:00:00'),
(364, 'SE103', 'Prof. Purple', 'Room 120', 'Friday', '14:00:00', '15:00:00'),
(365, 'SE103', 'Prof. Purple', 'Room 115', 'Saturday', '07:00:00', '08:00:00'),
(366, 'CY103', 'Prof. Lime', 'Room 110', 'Thursday', '16:00:00', '17:00:00'),
(367, 'CY103', 'Prof. Lime', 'Room 102', 'Thursday', '13:00:00', '14:00:00'),
(368, 'AI101', 'Prof. Turing', 'Room 114', 'Monday', '13:00:00', '14:00:00'),
(369, 'SEC301', 'Prof. Schneier', 'Room 119', 'Saturday', '09:00:00', '10:00:00'),
(370, 'SEC301', 'Prof. Schneier', 'Room 112', 'Friday', '09:00:00', '10:00:00'),
(371, 'SEC301', 'Prof. Schneier', 'Room 118', 'Saturday', '15:00:00', '16:00:00'),
(372, 'CS104', 'Prof. Tanenbaum', 'Room 112', 'Thursday', '07:00:00', '08:00:00'),
(373, 'RES401', 'Prof. Chomsky', 'Room 107', 'Tuesday', '10:00:00', '11:00:00'),
(374, 'RES401', 'Prof. Chomsky', 'Room 110', 'Wednesday', '08:00:00', '09:00:00'),
(375, 'RES401', 'Prof. Chomsky', 'Room 109', 'Monday', '07:00:00', '08:00:00'),
(376, 'CAP401', 'Prof. Gates', 'Room 110', 'Tuesday', '14:00:00', '15:00:00'),
(377, 'ENT401', 'Prof. Musk', 'Room 118', 'Thursday', '14:00:00', '15:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
CREATE TABLE IF NOT EXISTS `students` (
  `section_id` varchar(10) NOT NULL,
  `program` varchar(50) DEFAULT NULL,
  `year_level` int(11) DEFAULT NULL,
  `num_students` int(11) DEFAULT NULL,
  PRIMARY KEY (`section_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`section_id`, `program`, `year_level`, `num_students`) VALUES
('SEC001', 'BS Computer Science', 1, 30),
('SEC002', 'BS Information Technology', 1, 40),
('SEC003', 'BS Computer Science', 2, 35),
('SEC004', 'BS Information Technology', 2, 45),
('SEC005', 'BS Computer Science', 3, 32),
('SEC006', 'BS Information Technology', 3, 42),
('SEC007', 'BS Computer Science', 4, 30),
('SEC008', 'BS Information Technology', 4, 40),
('SEC009', 'BS Data Science', 1, 28),
('SEC010', 'BS Data Science', 2, 34),
('SEC011', 'BS Data Science', 3, 30),
('SEC012', 'BS Data Science', 4, 36),
('SEC013', 'BS Software Engineering', 1, 32),
('SEC014', 'BS Software Engineering', 2, 38),
('SEC015', 'BS Software Engineering', 3, 40),
('SEC016', 'BS Software Engineering', 4, 30),
('SEC017', 'BS Cyber Security', 1, 30),
('SEC018', 'BS Cyber Security', 2, 35),
('SEC019', 'BS Cyber Security', 3, 30),
('SEC020', 'BS Cyber Security', 4, 32);

-- --------------------------------------------------------

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
CREATE TABLE IF NOT EXISTS `subjects` (
  `subject_code` varchar(10) NOT NULL,
  `subject_name` varchar(100) DEFAULT NULL,
  `program` varchar(50) DEFAULT NULL,
  `year_level` int(11) DEFAULT NULL,
  `lecture_hours` int(11) DEFAULT NULL,
  PRIMARY KEY (`subject_code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `subjects`
--

INSERT INTO `subjects` (`subject_code`, `subject_name`, `program`, `year_level`, `lecture_hours`) VALUES
('DS102', 'Machine Learning Basics', 'BS Data Science', 2, 1),
('IT102', 'Networking Basics', 'BS Information Technology', 2, 1),
('CS102', 'Data Structures', 'BS Computer Science', 2, 1),
('PHY101', 'Physics for Computing', 'All', 1, 1),
('ENG101', 'Technical Writing', 'All', 1, 1),
('MATH101', 'Discrete Mathematics', 'All', 1, 1),
('CY101', 'Cyber Security Fundamentals', 'BS Cyber Security', 1, 1),
('SE101', 'Software Engineering Basics', 'BS Software Engineering', 1, 1),
('DS101', 'Intro to Data Science', 'BS Data Science', 1, 1),
('IT101', 'Fundamentals of IT', 'BS Information Technology', 1, 1),
('CS101', 'Introduction to CS', 'BS Computer Science', 1, 1),
('SE102', 'Agile Development', 'BS Software Engineering', 2, 1),
('CY102', 'Ethical Hacking', 'BS Cyber Security', 2, 1),
('MATH201', 'Linear Algebra', 'All', 2, 1),
('STAT201', 'Probability and Statistics', 'All', 2, 1),
('DB101', 'Database Management', 'All', 2, 1),
('CS103', 'Algorithms', 'BS Computer Science', 3, 1),
('IT103', 'Database Systems', 'BS Information Technology', 3, 1),
('DS103', 'Deep Learning', 'BS Data Science', 3, 1),
('SE103', 'DevOps', 'BS Software Engineering', 3, 1),
('CY103', 'Digital Forensics', 'BS Cyber Security', 3, 1),
('MATH301', 'Computational Mathematics', 'All', 3, 1),
('AI101', 'Artificial Intelligence', 'All', 3, 1),
('SEC301', 'Cybersecurity Policies', 'All', 3, 1),
('CS104', 'Operating Systems', 'BS Computer Science', 4, 1),
('IT104', 'Cloud Computing', 'BS Information Technology', 4, 1),
('DS104', 'Big Data Analytics', 'BS Data Science', 4, 1),
('SE104', 'Software Architecture', 'BS Software Engineering', 4, 1),
('CY104', 'Penetration Testing', 'BS Cyber Security', 4, 1),
('RES401', 'Research Methods', 'All', 4, 1),
('CAP401', 'Capstone Project', 'All', 4, 1),
('ENT401', 'Technopreneurship', 'All', 4, 1);

-- --------------------------------------------------------

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
CREATE TABLE IF NOT EXISTS `teachers` (
  `teacher_id` varchar(10) NOT NULL,
  `teacher_name` varchar(100) DEFAULT NULL,
  `subject_code` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`teacher_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `teachers`
--

INSERT INTO `teachers` (`teacher_id`, `teacher_name`, `subject_code`) VALUES
('T001', 'Prof. Smith', 'CS101'),
('T002', 'Prof. Jones', 'CS102'),
('T003', 'Prof. Brown', 'CS103'),
('T004', 'Prof. White', 'IT101'),
('T005', 'Prof. Green', 'IT102'),
('T006', 'Prof. Black', 'IT103'),
('T007', 'Prof. Grey', 'DS101'),
('T008', 'Prof. Blue', 'DS102'),
('T009', 'Prof. Orange', 'DS103'),
('T010', 'Prof. Red', 'SE101'),
('T011', 'Prof. Yellow', 'SE102'),
('T012', 'Prof. Purple', 'SE103'),
('T013', 'Prof. Cyan', 'CY101'),
('T014', 'Prof. Magenta', 'CY102'),
('T015', 'Prof. Lime', 'CY103'),
('T016', 'Prof. Euler', 'MATH301'),
('T017', 'Prof. Turing', 'AI101'),
('T018', 'Prof. Schneier', 'SEC301'),
('T019', 'Prof. Tanenbaum', 'CS104'),
('T020', 'Prof. Bezos', 'IT104'),
('T021', 'Prof. McKinney', 'DS104'),
('T022', 'Prof. Gamma', 'SE104'),
('T023', 'Prof. Mitnick', 'CY104'),
('T024', 'Prof. Chomsky', 'RES401'),
('T025', 'Prof. Gates', 'CAP401'),
('T026', 'Prof. Musk', 'ENT401');

-- --------------------------------------------------------

--
-- Table structure for table `time_slots`
--

DROP TABLE IF EXISTS `time_slots`;
CREATE TABLE IF NOT EXISTS `time_slots` (
  `time_slot_id` varchar(10) NOT NULL,
  `day` varchar(10) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  PRIMARY KEY (`time_slot_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `time_slots`
--

INSERT INTO `time_slots` (`time_slot_id`, `day`, `start_time`, `end_time`) VALUES
('TS001', 'Monday', '07:00:00', '08:00:00'),
('TS002', 'Monday', '08:00:00', '09:00:00'),
('TS003', 'Monday', '09:00:00', '10:00:00'),
('TS004', 'Monday', '10:00:00', '11:00:00'),
('TS005', 'Monday', '11:00:00', '12:00:00'),
('TS006', 'Monday', '13:00:00', '14:00:00'),
('TS007', 'Monday', '14:00:00', '15:00:00'),
('TS008', 'Monday', '15:00:00', '16:00:00'),
('TS009', 'Monday', '16:00:00', '17:00:00'),
('TS010', 'Tuesday', '07:00:00', '08:00:00'),
('TS011', 'Tuesday', '08:00:00', '09:00:00'),
('TS012', 'Tuesday', '09:00:00', '10:00:00'),
('TS013', 'Tuesday', '10:00:00', '11:00:00'),
('TS014', 'Tuesday', '11:00:00', '12:00:00'),
('TS015', 'Tuesday', '13:00:00', '14:00:00'),
('TS016', 'Tuesday', '14:00:00', '15:00:00'),
('TS017', 'Tuesday', '15:00:00', '16:00:00'),
('TS018', 'Tuesday', '16:00:00', '17:00:00'),
('TS019', 'Wednesday', '07:00:00', '08:00:00'),
('TS020', 'Wednesday', '08:00:00', '09:00:00'),
('TS021', 'Wednesday', '09:00:00', '10:00:00'),
('TS022', 'Wednesday', '10:00:00', '11:00:00'),
('TS023', 'Wednesday', '11:00:00', '12:00:00'),
('TS024', 'Wednesday', '13:00:00', '14:00:00'),
('TS025', 'Wednesday', '14:00:00', '15:00:00'),
('TS026', 'Wednesday', '15:00:00', '16:00:00'),
('TS027', 'Wednesday', '16:00:00', '17:00:00'),
('TS028', 'Thursday', '07:00:00', '08:00:00'),
('TS029', 'Thursday', '08:00:00', '09:00:00'),
('TS030', 'Thursday', '09:00:00', '10:00:00'),
('TS031', 'Thursday', '10:00:00', '11:00:00'),
('TS032', 'Thursday', '11:00:00', '12:00:00'),
('TS033', 'Thursday', '13:00:00', '14:00:00'),
('TS034', 'Thursday', '14:00:00', '15:00:00'),
('TS035', 'Thursday', '15:00:00', '16:00:00'),
('TS036', 'Thursday', '16:00:00', '17:00:00'),
('TS037', 'Friday', '07:00:00', '08:00:00'),
('TS038', 'Friday', '08:00:00', '09:00:00'),
('TS039', 'Friday', '09:00:00', '10:00:00'),
('TS040', 'Friday', '10:00:00', '11:00:00'),
('TS041', 'Friday', '11:00:00', '12:00:00'),
('TS042', 'Friday', '13:00:00', '14:00:00'),
('TS043', 'Friday', '14:00:00', '15:00:00'),
('TS044', 'Friday', '15:00:00', '16:00:00'),
('TS045', 'Friday', '16:00:00', '17:00:00'),
('TS046', 'Saturday', '07:00:00', '08:00:00'),
('TS047', 'Saturday', '08:00:00', '09:00:00'),
('TS048', 'Saturday', '09:00:00', '10:00:00'),
('TS049', 'Saturday', '10:00:00', '11:00:00'),
('TS050', 'Saturday', '11:00:00', '12:00:00'),
('TS051', 'Saturday', '13:00:00', '14:00:00'),
('TS052', 'Saturday', '14:00:00', '15:00:00'),
('TS053', 'Saturday', '15:00:00', '16:00:00'),
('TS054', 'Saturday', '16:00:00', '17:00:00');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
