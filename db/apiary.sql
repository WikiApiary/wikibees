-- MariaDB dump 10.19  Distrib 10.5.18-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: apiary
-- ------------------------------------------------------
-- Server version	10.5.18-MariaDB-0+deb11u1-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `_yoyo_migration`
--

DROP TABLE IF EXISTS `_yoyo_migration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `_yoyo_migration` (
  `id` varchar(255) NOT NULL,
  `ctime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apiary_bot_log`
--

DROP TABLE IF EXISTS `apiary_bot_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apiary_bot_log` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `log_date` datetime NOT NULL,
  `bot` varchar(30) NOT NULL,
  `duration` float DEFAULT NULL,
  `log_type` varchar(10) NOT NULL,
  `message` varchar(255) NOT NULL,
  PRIMARY KEY (`log_id`),
  KEY `idx_log_date` (`log_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=18627857 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apiary_multiprops`
--

DROP TABLE IF EXISTS `apiary_multiprops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apiary_multiprops` (
  `website_id` int(11) NOT NULL,
  `t_name` varchar(255) NOT NULL,
  `t_value` varchar(255) NOT NULL,
  `first_date` datetime NOT NULL,
  `last_date` datetime NOT NULL,
  `occurrences` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`t_name`,`t_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `apiary_website_logs`
--

DROP TABLE IF EXISTS `apiary_website_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `apiary_website_logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `website_id` int(11) NOT NULL,
  `log_date` datetime NOT NULL,
  `website_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `log_type` varchar(30) NOT NULL,
  `log_severity` varchar(30) NOT NULL,
  `log_message` blob DEFAULT NULL,
  `log_bot` varchar(30) DEFAULT NULL,
  `log_url` varchar(255) DEFAULT NULL,
  `log_data` blob DEFAULT NULL,
  PRIMARY KEY (`log_id`),
  KEY `idx_log_date` (`log_date`) USING BTREE,
  KEY `idx_website_id_log_date` (`website_id`,`log_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=27056086 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `apiary_website_logs_summary`
--

DROP TABLE IF EXISTS `apiary_website_logs_summary`;
/*!50001 DROP VIEW IF EXISTS `apiary_website_logs_summary`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `apiary_website_logs_summary` AS SELECT
 1 AS `website_id`,
  1 AS `log_count`,
  1 AS `log_date_last`,
  1 AS `lot_date_first` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `smwextinfo`
--

DROP TABLE IF EXISTS `smwextinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smwextinfo` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `response_timer` float DEFAULT NULL,
  `query_count` int(11) NOT NULL,
  `query_pages` int(11) NOT NULL,
  `query_concepts` int(11) NOT NULL,
  `query_pageslarge` int(11) NOT NULL,
  `size1` int(11) NOT NULL,
  `size2` int(11) NOT NULL,
  `size3` int(11) NOT NULL,
  `size4` int(11) NOT NULL,
  `size5` int(11) NOT NULL,
  `size6` int(11) NOT NULL,
  `size7` int(11) NOT NULL,
  `size8` int(11) NOT NULL,
  `size9` int(11) NOT NULL,
  `size10plus` int(11) NOT NULL,
  `format_broadtable` int(11) NOT NULL,
  `format_csv` int(11) NOT NULL,
  `format_category` int(11) NOT NULL,
  `format_count` int(11) NOT NULL,
  `format_dsv` int(11) NOT NULL,
  `format_debug` int(11) NOT NULL,
  `format_embedded` int(11) NOT NULL,
  `format_feed` int(11) NOT NULL,
  `format_json` int(11) NOT NULL,
  `format_list` int(11) NOT NULL,
  `format_ol` int(11) NOT NULL,
  `format_rdf` int(11) NOT NULL,
  `format_table` int(11) NOT NULL,
  `format_template` int(11) NOT NULL,
  `format_ul` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`capture_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smwinfo`
--

DROP TABLE IF EXISTS `smwinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smwinfo` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `response_timer` float DEFAULT NULL,
  `propcount` bigint(20) NOT NULL,
  `proppagecount` int(11) NOT NULL,
  `usedpropcount` int(11) NOT NULL,
  `declaredpropcount` int(11) NOT NULL,
  `querycount` int(11) DEFAULT NULL,
  `querysize` int(11) DEFAULT NULL,
  `conceptcount` int(11) DEFAULT NULL,
  `subobjectcount` int(11) DEFAULT NULL,
  `errorcount` int(11) DEFAULT NULL,
  PRIMARY KEY (`website_id`,`capture_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `smwinfo_formats`
--

DROP TABLE IF EXISTS `smwinfo_formats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `smwinfo_formats` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `format_name` varchar(50) NOT NULL,
  `format_count` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`capture_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `statistics`
--

DROP TABLE IF EXISTS `statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statistics` (
  `website_id` int(11) NOT NULL,
  `capture_date` datetime NOT NULL,
  `response_timer` float DEFAULT NULL,
  `users` bigint(20) NOT NULL,
  `activeusers` bigint(20) DEFAULT NULL,
  `admins` bigint(20) NOT NULL,
  `articles` bigint(20) NOT NULL,
  `edits` bigint(20) NOT NULL,
  `images` bigint(20) DEFAULT NULL,
  `jobs` bigint(20) DEFAULT NULL,
  `pages` bigint(20) NOT NULL,
  `views` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`website_id`,`capture_date`),
  KEY `idx_capture_date` (`capture_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci
 PARTITION BY HASH (`website_id`)
PARTITIONS 15;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `statistics_daily`
--

DROP TABLE IF EXISTS `statistics_daily`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statistics_daily` (
  `website_id` int(11) NOT NULL,
  `website_date` date NOT NULL,
  `users_min` bigint(20) NOT NULL,
  `users_max` bigint(20) NOT NULL,
  `activeusers_max` bigint(20) NOT NULL,
  `admins_max` bigint(20) NOT NULL,
  `articles_min` bigint(20) NOT NULL,
  `articles_max` bigint(20) NOT NULL,
  `edits_min` bigint(20) NOT NULL,
  `edits_max` bigint(20) NOT NULL,
  `jobs_max` bigint(20) NOT NULL,
  `pages_min` bigint(20) NOT NULL,
  `pages_max` bigint(20) NOT NULL,
  `pages_last` bigint(20) NOT NULL,
  `views_min` bigint(20) NOT NULL,
  `views_max` bigint(20) NOT NULL,
  `smw_propcount_min` bigint(20) NOT NULL,
  `smw_propcount_max` bigint(20) NOT NULL,
  `smw_proppagecount_last` int(11) NOT NULL,
  `smw_usedpropcount_last` int(11) NOT NULL,
  `smw_declaredpropcount_last` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`website_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `statistics_weekly`
--

DROP TABLE IF EXISTS `statistics_weekly`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statistics_weekly` (
  `website_id` int(11) NOT NULL,
  `website_date` date NOT NULL,
  `users_min` bigint(20) NOT NULL,
  `users_max` bigint(20) NOT NULL,
  `activeusers_max` bigint(20) NOT NULL,
  `admins_max` bigint(20) NOT NULL,
  `articles_min` bigint(20) NOT NULL,
  `articles_max` bigint(20) NOT NULL,
  `edits_min` bigint(20) NOT NULL,
  `edits_max` bigint(20) NOT NULL,
  `jobs_max` bigint(20) NOT NULL,
  `pages_min` bigint(20) NOT NULL,
  `pages_max` bigint(20) NOT NULL,
  `pages_last` bigint(20) NOT NULL,
  `views_min` bigint(20) NOT NULL,
  `views_max` bigint(20) NOT NULL,
  `smw_propcount_min` bigint(20) NOT NULL,
  `smw_propcount_max` bigint(20) NOT NULL,
  `smw_proppagecount_last` int(11) NOT NULL,
  `smw_usedpropcount_last` int(11) NOT NULL,
  `smw_declaredpropcount_last` int(11) NOT NULL,
  PRIMARY KEY (`website_id`,`website_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=COMPACT;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `website_status`
--

DROP TABLE IF EXISTS `website_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `website_status` (
  `website_id` int(11) NOT NULL,
  `check_every_limit` int(11) DEFAULT 60,
  `last_statistics` datetime DEFAULT NULL,
  `last_general` datetime DEFAULT NULL,
  `last_general_hash` char(64) DEFAULT NULL,
  `last_extension` datetime DEFAULT NULL,
  `last_extension_hash` char(64) DEFAULT NULL,
  `last_skin` datetime DEFAULT NULL,
  `last_skin_hash` char(64) DEFAULT NULL,
  PRIMARY KEY (`website_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `apiary_website_logs_summary`
--

/*!50001 DROP VIEW IF EXISTS `apiary_website_logs_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`192.168.189.13` SQL SECURITY DEFINER */
/*!50001 VIEW `apiary_website_logs_summary` AS select `apiary`.`apiary_website_logs`.`website_id` AS `website_id`,count(0) AS `log_count`,max(`apiary`.`apiary_website_logs`.`log_date`) AS `log_date_last`,min(`apiary`.`apiary_website_logs`.`log_date`) AS `lot_date_first` from `apiary_website_logs` group by `apiary`.`apiary_website_logs`.`website_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-09 15:34:46
