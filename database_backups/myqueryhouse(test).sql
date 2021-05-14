-- MySQL dump 10.13  Distrib 8.0.23, for Linux (x86_64)
--
-- Host: localhost    Database: myqueryhouse
-- ------------------------------------------------------
-- Server version	8.0.23-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Category`
--

CREATE DATABASE IF NOT EXISTS `myqueryhouse`;
USE `myqueryhouse`;

DROP TABLE IF EXISTS `Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Category` (
  `CategoryID` int unsigned NOT NULL AUTO_INCREMENT,
  `storageid` int unsigned DEFAULT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`CategoryID`),
  UNIQUE KEY `CategoryID_UNIQUE` (`CategoryID`),
  KEY `storageid_idx` (`storageid`),
  CONSTRAINT `storageid` FOREIGN KEY (`storageid`) REFERENCES `Storage` (`StorageID`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Category`
--

LOCK TABLES `Category` WRITE;
/*!40000 ALTER TABLE `Category` DISABLE KEYS */;
INSERT INTO `Category` VALUES (1,6,'Electronics'),(2,NULL,'Stuff'),(3,13,'Things');
/*!40000 ALTER TABLE `Category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Customer`
--

DROP TABLE IF EXISTS `Customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Customer` (
  `CustomerID` int unsigned NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(45) NOT NULL,
  `LastName` varchar(45) NOT NULL,
  `PhoneNumber` int unsigned NOT NULL,
  PRIMARY KEY (`CustomerID`),
  UNIQUE KEY `CustomerID_UNIQUE` (`CustomerID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Customer`
--

LOCK TABLES `Customer` WRITE;
/*!40000 ALTER TABLE `Customer` DISABLE KEYS */;
INSERT INTO `Customer` VALUES (1,'Simon','Lærer',13371337),(2,'Konrad','Sommer',12345678),(3,'Fornavn','Efternavn',34645654),(4,'Coolguy','Niceman',87645457);
/*!40000 ALTER TABLE `Customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Item`
--

DROP TABLE IF EXISTS `Item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Item` (
  `ItemID` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`ItemID`),
  UNIQUE KEY `ItemID_UNIQUE` (`ItemID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Item`
--

LOCK TABLES `Item` WRITE;
/*!40000 ALTER TABLE `Item` DISABLE KEYS */;
INSERT INTO `Item` VALUES (1,'Cykel'),(2,'Sten'),(3,'Grus'),(4,'Kage'),(5,'Gamer PC'),(6,'Gamer Headset'),(7,'Gamer Mus');
/*!40000 ALTER TABLE `Item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ItemMtmCategory`
--

DROP TABLE IF EXISTS `ItemMtmCategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ItemMtmCategory` (
  `itemid` int unsigned NOT NULL,
  `categoryid` int unsigned NOT NULL,
  PRIMARY KEY (`itemid`,`categoryid`),
  KEY `categoryid_idx` (`categoryid`),
  KEY `mtm_categoryid_idx` (`categoryid`),
  CONSTRAINT `mtm_categoryid` FOREIGN KEY (`categoryid`) REFERENCES `Category` (`CategoryID`),
  CONSTRAINT `mtm_itemid` FOREIGN KEY (`itemid`) REFERENCES `Item` (`ItemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ItemMtmCategory`
--

LOCK TABLES `ItemMtmCategory` WRITE;
/*!40000 ALTER TABLE `ItemMtmCategory` DISABLE KEYS */;
/*!40000 ALTER TABLE `ItemMtmCategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ItemPurchase`
--

DROP TABLE IF EXISTS `ItemPurchase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ItemPurchase` (
  `ItemPurchaseID` int unsigned NOT NULL AUTO_INCREMENT,
  `itemid` int unsigned NOT NULL,
  `purchaseorderid` int unsigned NOT NULL,
  `Quantity` int unsigned NOT NULL,
  PRIMARY KEY (`ItemPurchaseID`),
  UNIQUE KEY `ItemPurchaseID_UNIQUE` (`ItemPurchaseID`),
  KEY `itemid_idx` (`itemid`),
  KEY `purchaseorderid_idx` (`purchaseorderid`),
  CONSTRAINT `itemid` FOREIGN KEY (`itemid`) REFERENCES `Item` (`ItemID`),
  CONSTRAINT `purchaseorderid` FOREIGN KEY (`purchaseorderid`) REFERENCES `PurchaseOrder` (`PurchaseOrderID`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ItemPurchase`
--

LOCK TABLES `ItemPurchase` WRITE;
/*!40000 ALTER TABLE `ItemPurchase` DISABLE KEYS */;
INSERT INTO `ItemPurchase` VALUES (1,1,2,13),(2,2,2,25),(3,3,2,12),(4,3,3,1),(5,5,3,2),(6,3,4,3),(7,2,4,4),(8,1,4,5);
/*!40000 ALTER TABLE `ItemPurchase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `ItemPurchaseWithName`
--

DROP TABLE IF EXISTS `ItemPurchaseWithName`;
/*!50001 DROP VIEW IF EXISTS `ItemPurchaseWithName`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `ItemPurchaseWithName` AS SELECT 
 1 AS `Name`,
 1 AS `Quantity`,
 1 AS `Received`,
 1 AS `ReceivedDate`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Order`
--

DROP TABLE IF EXISTS `Order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Order` (
  `OrderID` int unsigned NOT NULL AUTO_INCREMENT,
  `customerid` int unsigned NOT NULL,
  `Received` tinyint unsigned NOT NULL,
  `Purchased` tinyint unsigned NOT NULL,
  PRIMARY KEY (`OrderID`),
  UNIQUE KEY `OrderID_UNIQUE` (`OrderID`),
  KEY `customerid_idx` (`customerid`),
  CONSTRAINT `customerid` FOREIGN KEY (`customerid`) REFERENCES `Customer` (`CustomerID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Order`
--

LOCK TABLES `Order` WRITE;
/*!40000 ALTER TABLE `Order` DISABLE KEYS */;
INSERT INTO `Order` VALUES (1,1,0,0),(2,2,0,0),(3,3,0,0);
/*!40000 ALTER TABLE `Order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `OrderItemCount`
--

DROP TABLE IF EXISTS `OrderItemCount`;
/*!50001 DROP VIEW IF EXISTS `OrderItemCount`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `OrderItemCount` AS SELECT 
 1 AS `itemid`,
 1 AS `amount`,
 1 AS `Name`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Orderline`
--

DROP TABLE IF EXISTS `Orderline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Orderline` (
  `OrderlineID` int unsigned NOT NULL AUTO_INCREMENT,
  `itemid` int unsigned NOT NULL,
  `orderid` int unsigned NOT NULL,
  `Quantity` int unsigned NOT NULL,
  PRIMARY KEY (`OrderlineID`),
  UNIQUE KEY `OrderlineID_UNIQUE` (`OrderlineID`),
  KEY `itemid_idx` (`itemid`),
  KEY `orderid_idx` (`orderid`),
  CONSTRAINT `orderid` FOREIGN KEY (`orderid`) REFERENCES `Order` (`OrderID`) ON DELETE RESTRICT,
  CONSTRAINT `orderline_itemid` FOREIGN KEY (`itemid`) REFERENCES `Item` (`ItemID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Orderline`
--

LOCK TABLES `Orderline` WRITE;
/*!40000 ALTER TABLE `Orderline` DISABLE KEYS */;
INSERT INTO `Orderline` VALUES (1,2,1,25),(2,3,1,1),(3,4,1,23),(4,2,2,3);
/*!40000 ALTER TABLE `Orderline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PurchaseOrder`
--

DROP TABLE IF EXISTS `PurchaseOrder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PurchaseOrder` (
  `PurchaseOrderID` int unsigned NOT NULL AUTO_INCREMENT,
  `Received` tinyint unsigned NOT NULL,
  `ReceivedDate` date DEFAULT NULL,
  PRIMARY KEY (`PurchaseOrderID`),
  UNIQUE KEY `PurchaseOrderID_UNIQUE` (`PurchaseOrderID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PurchaseOrder`
--

LOCK TABLES `PurchaseOrder` WRITE;
/*!40000 ALTER TABLE `PurchaseOrder` DISABLE KEYS */;
INSERT INTO `PurchaseOrder` VALUES (2,0,NULL),(3,0,NULL),(4,0,NULL);
/*!40000 ALTER TABLE `PurchaseOrder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Storage`
--

DROP TABLE IF EXISTS `Storage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Storage` (
  `StorageID` int unsigned NOT NULL AUTO_INCREMENT,
  `RoomNumber` int unsigned NOT NULL,
  PRIMARY KEY (`StorageID`),
  UNIQUE KEY `StorageID_UNIQUE` (`StorageID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Storage`
--

LOCK TABLES `Storage` WRITE;
/*!40000 ALTER TABLE `Storage` DISABLE KEYS */;
INSERT INTO `Storage` VALUES (6,6),(13,8),(14,5),(16,11),(17,12),(18,13);
/*!40000 ALTER TABLE `Storage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `ItemPurchaseWithName`
--

/*!50001 DROP VIEW IF EXISTS `ItemPurchaseWithName`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `ItemPurchaseWithName` AS select `Item`.`Name` AS `Name`,`ItemPurOrder`.`Quantity` AS `Quantity`,`ItemPurOrder`.`Received` AS `Received`,`ItemPurOrder`.`ReceivedDate` AS `ReceivedDate` from ((select `ItemPurchase`.`itemid` AS `itemid`,`ItemPurchase`.`Quantity` AS `Quantity`,`PurchaseOrder`.`Received` AS `Received`,`PurchaseOrder`.`ReceivedDate` AS `ReceivedDate` from (`ItemPurchase` join `PurchaseOrder`) where (`ItemPurchase`.`purchaseorderid` = `PurchaseOrder`.`PurchaseOrderID`)) `ItemPurOrder` join `Item`) where (`ItemPurOrder`.`itemid` = `Item`.`ItemID`) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `OrderItemCount`
--

/*!50001 DROP VIEW IF EXISTS `OrderItemCount`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `OrderItemCount` AS select `subquery`.`itemid` AS `itemid`,`subquery`.`amount` AS `amount`,`item`.`Name` AS `Name` from (`Item` `item` left join (select `ol`.`itemid` AS `itemid`,sum(`ol`.`Quantity`) AS `amount` from `Orderline` `ol` group by `ol`.`itemid`) `subquery` on((`subquery`.`itemid` = `item`.`ItemID`))) */;
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

-- Dump completed on 2021-05-06 12:10:52
-- query aborted
