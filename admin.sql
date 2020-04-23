-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Nov 20, 2019 at 01:06 PM
-- Server version: 5.7.26
-- PHP Version: 7.2.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pcd_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
CREATE TABLE IF NOT EXISTS `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employeeid` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `firstname` varchar(70) NOT NULL,
  `lastname` varchar(70) NOT NULL,
  `address` varchar(200) NOT NULL,
  `userlevel` int(11) NOT NULL DEFAULT '0',
  `photo` varchar(255) DEFAULT NULL,
  `age` date NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`,`employeeid`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `employeeid`, `email`, `password`, `firstname`, `lastname`, `address`, `userlevel`, `photo`, `age`, `date`) VALUES
(1, 'PCD22391', 'adminc@gmail.com', '0192023a7bbd73250516f069df18b500', 'Adam', 'Adena', '12 serida st \r\nmasvingo', 1, NULL, '1996-10-13', '2019-11-15 03:37:45'),
(2, 'PCD44213', 'dian@gmail.com', '5e18f1c165f76d229c151fa37250c65e', 'Dian', 'Resa', '12 Aedot\r\nMutare', 1, NULL, '1999-04-12', '2019-11-18 15:26:19'),
(3, 'PCD53904', 'adam@gmail.com', '3e7b522b9756d2578d3a86d8f366be6e', 'Adam', 'Adena', '12 zawa st', 1, NULL, '1990-12-12', '2019-11-19 07:50:05');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
