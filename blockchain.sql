-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Erstellungszeit: 17. Dez 2020 um 11:07
-- Server-Version: 10.3.27-MariaDB-0+deb10u1
-- PHP-Version: 7.3.19-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Datenbank: `blockchain`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `chain`
--

CREATE TABLE `chain` (
  `id` int(11) NOT NULL,
  `ind` text NOT NULL,
  `data` text NOT NULL,
  `prevHash` text NOT NULL,
  `nonce` text NOT NULL,
  `timestampReal` text NOT NULL,
  `fee` text NOT NULL,
  `submitted` text NOT NULL,
  `timestamp` text NOT NULL,
  `status` text NOT NULL,
  `difficulty` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `miners`
--

CREATE TABLE `miners` (
  `id` int(11) NOT NULL,
  `name` text NOT NULL,
  `hashrate` text NOT NULL,
  `acceptedShares` text NOT NULL,
  `rejectedShares` text NOT NULL,
  `payout` text NOT NULL,
  `registered` text NOT NULL,
  `status` text NOT NULL,
  `currentStatus` text NOT NULL,
  `password` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `chain`
--
ALTER TABLE `chain`
  ADD PRIMARY KEY (`id`);

--
-- Indizes für die Tabelle `miners`
--
ALTER TABLE `miners`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `chain`
--
ALTER TABLE `chain`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT für Tabelle `miners`
--
ALTER TABLE `miners`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
