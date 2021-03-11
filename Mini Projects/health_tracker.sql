-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 08, 2020 at 06:59 PM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `health_tracker`
--

-- --------------------------------------------------------

--
-- Table structure for table `dashboard`
--

CREATE TABLE `dashboard` (
  `DashBoardId` int(11) NOT NULL,
  `UserId` int(11) NOT NULL,
  `IdealBMRValue` float NOT NULL,
  `CalorieInput` float NOT NULL,
  `CalorieOutput` float NOT NULL,
  `FinalCalorie` float NOT NULL,
  `Variation` float NOT NULL,
  `Date` date NOT NULL,
  `IsActive` tinyint(1) NOT NULL,
  `DateCreated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `personalprofile`
--

CREATE TABLE `personalprofile` (
  `ProfileId` int(11) NOT NULL,
  `UserId` int(11) NOT NULL,
  `FirstName` varchar(50) NOT NULL,
  `MiddleName` varchar(50) NOT NULL,
  `LastName` varchar(50) NOT NULL,
  `DateOfBirth` date NOT NULL,
  `Height` float NOT NULL,
  `Weight` float NOT NULL,
  `Sex` varchar(10) NOT NULL,
  `Age` int(11) NOT NULL,
  `BMIValue` float NOT NULL,
  `BMICategory` varchar(50) NOT NULL,
  `Address` varchar(100) NOT NULL,
  `PhoneNumber` varchar(50) NOT NULL,
  `MinWeight` float NOT NULL,
  `MaxWeight` float NOT NULL,
  `BMRValue` float NOT NULL,
  `SuggestedBMRValue` float NOT NULL,
  `Message` varchar(100) NOT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `personalprofile`
--

INSERT INTO `personalprofile` (`ProfileId`, `UserId`, `FirstName`, `MiddleName`, `LastName`, `DateOfBirth`, `Height`, `Weight`, `Sex`, `Age`, `BMIValue`, `BMICategory`, `Address`, `PhoneNumber`, `MinWeight`, `MaxWeight`, `BMRValue`, `SuggestedBMRValue`, `Message`, `IsActive`) VALUES
(1, 1, 'harnath', 'rock', 'atmakuri', '1998-05-28', 160, 60, 'Male', 23, 23, 'Normal Weight', '14-1-52,KUSUMA HARA NIVAS,DOMALAPALEM,ONGOLE', '9701185467', 50, 60, 1490, 1490, 'You are all right pls maintain the same daily routine and diet ', 0),
(2, 1, 'Harnath', 'changed', 'Atmakuri', '2020-04-01', 160, 60, 'Male', 23, 23, 'Normal Weight', '12345', '9701185467', 50, 60, 1490, 1490, 'You are all right pls maintain the same daily routine and diet ', 1);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `UserId` int(11) NOT NULL,
  `UserEmail` varchar(100) NOT NULL,
  `UserPassword` varchar(50) NOT NULL,
  `IsActive` tinyint(1) NOT NULL,
  `DateCreated` datetime NOT NULL,
  `DateModified` datetime NOT NULL,
  `IsProfileCreated` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`UserId`, `UserEmail`, `UserPassword`, `IsActive`, `DateCreated`, `DateModified`, `IsProfileCreated`) VALUES
(1, 'harnath@gmail.com', 'harnath', 1, '2020-04-08 16:19:27', '0000-00-00 00:00:00', 1);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dashboard`
--
ALTER TABLE `dashboard`
  ADD PRIMARY KEY (`DashBoardId`);

--
-- Indexes for table `personalprofile`
--
ALTER TABLE `personalprofile`
  ADD PRIMARY KEY (`ProfileId`),
  ADD KEY `UserId` (`UserId`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`UserId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `dashboard`
--
ALTER TABLE `dashboard`
  MODIFY `DashBoardId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `personalprofile`
--
ALTER TABLE `personalprofile`
  MODIFY `ProfileId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `UserId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `personalprofile`
--
ALTER TABLE `personalprofile`
  ADD CONSTRAINT `personalprofile_ibfk_1` FOREIGN KEY (`UserId`) REFERENCES `user` (`UserId`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
