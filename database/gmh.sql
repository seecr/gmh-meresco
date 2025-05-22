CREATE DATABASE  IF NOT EXISTS `gmh` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `gmh`;
-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: tgharvester31.dans.knaw.nl    Database: tst_nbnresolver
-- ------------------------------------------------------
-- Server version	5.5.5-10.3.17-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `credentials`
--

DROP TABLE IF EXISTS `credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `credentials` (
  `credentials_id` int(11) NOT NULL AUTO_INCREMENT,
  `registrant_id` int(11) NOT NULL,
  `username` varchar(150) DEFAULT NULL,
  `password` varchar(150) DEFAULT NULL,
  `token` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`credentials_id`),
  KEY `FK_registrant_id_idx` (`registrant_id`),
  CONSTRAINT `FK_registrant_id` FOREIGN KEY (`registrant_id`) REFERENCES `registrant` (`registrant_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `identifier`
--

DROP TABLE IF EXISTS `identifier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `identifier` (
  `identifier_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `identifier_value` varchar(510) NOT NULL,
  PRIMARY KEY (`identifier_id`),
  UNIQUE KEY `identifier_value_UNIQUE` (`identifier_value`),
  KEY `idxIdentifierValue` (`identifier_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `identifier_location`
--

DROP TABLE IF EXISTS `identifier_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `identifier_location` (
  `location_id` bigint(20) NOT NULL,
  `identifier_id` bigint(20) NOT NULL,
  `last_modified` timestamp(4) NOT NULL DEFAULT current_timestamp(4),
  `isFailover` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`identifier_id`,`location_id`),
  KEY `FkLocation_idx` (`location_id`),
  CONSTRAINT `FkIdentifier` FOREIGN KEY (`identifier_id`) REFERENCES `identifier` (`identifier_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FkLocation` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `identifier_registrant`
--

DROP TABLE IF EXISTS `identifier_registrant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `identifier_registrant` (
  `identifier_id` bigint(20) NOT NULL,
  `registrant_id` int(11) NOT NULL,
  PRIMARY KEY (`identifier_id`,`registrant_id`),
  KEY `FK_tbl_registrant_idx` (`registrant_id`),
  CONSTRAINT `FK_tbl_identifier` FOREIGN KEY (`identifier_id`) REFERENCES `identifier` (`identifier_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_tbl_registrant` FOREIGN KEY (`registrant_id`) REFERENCES `registrant` (`registrant_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location` (
  `location_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `location_url` varchar(1022) NOT NULL,
  PRIMARY KEY (`location_id`),
  UNIQUE KEY `location_url_UNIQUE` (`location_url`),
  KEY `idxLocationUrl` (`location_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `location_registrant`
--

DROP TABLE IF EXISTS `location_registrant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location_registrant` (
  `location_id` bigint(20) NOT NULL,
  `registrant_id` int(11) NOT NULL,
  PRIMARY KEY (`location_id`,`registrant_id`),
  KEY `FK_Registrant_idx` (`registrant_id`),
  CONSTRAINT `FK_Location` FOREIGN KEY (`location_id`) REFERENCES `location` (`location_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Registrant` FOREIGN KEY (`registrant_id`) REFERENCES `registrant` (`registrant_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `registrant`
--

DROP TABLE IF EXISTS `registrant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registrant` (
  `registrant_id` int(11) NOT NULL AUTO_INCREMENT,
  `registrant_groupid` varchar(255) NOT NULL,
  `created` datetime NOT NULL DEFAULT current_timestamp(),
  `isLTP` tinyint(1) NOT NULL DEFAULT '0',
  `prefix` varchar(45) DEFAULT 'urn:nbn:nl:',
  PRIMARY KEY (`registrant_id`),
  UNIQUE KEY `registrant_groupid_UNIQUE` (`registrant_groupid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'act_nbnresolver'
--
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `addNbnLocation` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`gmh`@`localhost` PROCEDURE `addNbnLocation`(IN nbn_value VARCHAR(510), IN nbn_location VARCHAR(1022), IN registrant_id INT(11) , IN failover BOOLEAN)
BEGIN
DECLARE loc_identifierid BIGINT(20);
DECLARE loc_locationid BIGINT(20);
START TRANSACTION;
        SELECT I.identifier_id INTO loc_identifierid from identifier I where I.identifier_value = nbn_value;
        SELECT L.location_id INTO loc_locationid from location L where L.location_url = nbn_location;

        IF (loc_identifierid IS NULL) THEN
                INSERT INTO identifier (identifier_value) VALUES (nbn_value);
                SET loc_identifierid = LAST_INSERT_ID();
        END IF;
        INSERT IGNORE INTO identifier_registrant (identifier_id, registrant_id) VALUES (loc_identifierid, registrant_id );

        IF (loc_locationid IS NULL) THEN
                INSERT INTO location (location_url) VALUES (nbn_location);
                SET loc_locationid = LAST_INSERT_ID();
        END IF;
        INSERT IGNORE INTO location_registrant (location_id, registrant_id) VALUES (loc_locationid, registrant_id );

        IF (failover) THEN
                SET @location = loc_locationid, @identifier = loc_identifierid, @last_update=NOW(4), @failover=failover;
                INSERT INTO identifier_location (location_id, identifier_id, last_modified, isFailover) VALUES (@location, @identifier, @last_update, @failover)
                ON DUPLICATE KEY UPDATE location_id=@location, identifier_id=@identifier, last_modified=@last_update, isFailover=@failover;
        ELSE
                SET @location = loc_locationid, @identifier = loc_identifierid, @last_update=NOW(4), @failover=failover;
                INSERT INTO identifier_location (location_id, identifier_id, last_modified, isFailover) VALUES (@location, @identifier, @last_update, @failover)
                ON DUPLICATE KEY UPDATE location_id=@location, identifier_id=@identifier, last_modified=@last_update;
        END IF;
COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `deleteNbnLocationsByRegistrantId` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
DELIMITER ;;
CREATE DEFINER=`gmh`@`localhost` PROCEDURE `deleteNbnLocationsByRegistrantId`(IN nbn_value VARCHAR(510), IN registrantid INT(11), IN failover BOOLEAN)
BEGIN
DECLARE identifierid BIGINT(20);
START TRANSACTION;
        SELECT I.identifier_id INTO identifierid FROM identifier I WHERE I.identifier_value = nbn_value;
    IF (identifierid IS NOT NULL) THEN

            DELETE identifier_location FROM identifier_location INNER JOIN location_registrant ON identifier_location.location_id = location_registrant.location_id WHERE location_registrant.registrant_id = registrantid AND identifier_location.identifier_id = identifierid AND identifier_location.isFailover = failover;
    END IF;
COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;





