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
-- Table structure for table `Item`
--

DROP TABLE IF EXISTS `Item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Item` (
  `productname` varchar(50) DEFAULT NULL,
  `description` varchar(400) DEFAULT NULL,
  `itemID` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`itemID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Item`
--

LOCK TABLES `Item` WRITE;
/*!40000 ALTER TABLE `Item` DISABLE KEYS */;
INSERT INTO `Item` VALUES ('testproduct1','does some tests and stuff',1),('alsotestproduct','amazing',2);
/*!40000 ALTER TABLE `Item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Location`
--

DROP TABLE IF EXISTS `Location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Location` (
  `shelf` smallint unsigned DEFAULT NULL,
  `space` smallint unsigned DEFAULT NULL,
  `locationID` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`locationID`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Location`
--

LOCK TABLES `Location` WRITE;
/*!40000 ALTER TABLE `Location` DISABLE KEYS */;
INSERT INTO `Location` VALUES (1,1,1),(1,2,2),(1,3,3),(1,4,4),(1,5,5),(1,6,6),(1,7,7),(1,8,8),(1,9,9),(1,10,10),(2,1,11),(2,2,12),(2,3,13),(2,4,14),(2,5,15),(2,6,16),(2,7,17),(2,8,18),(2,9,19),(2,10,20),(3,1,21),(3,2,22),(3,3,23),(3,4,24),(3,5,25),(3,6,26),(3,7,27),(3,8,28),(3,9,29),(3,10,30),(4,1,31),(4,2,32),(4,3,33),(4,4,34),(4,5,35),(4,6,36),(4,7,37),(4,8,38),(4,9,39),(4,10,40),(5,1,41),(5,2,42),(5,3,43),(5,4,44),(5,5,45),(5,6,46),(5,7,47),(5,8,48),(5,9,49),(5,10,50),(6,1,51),(6,2,52),(6,3,53),(6,4,54),(6,5,55),(6,6,56),(6,7,57),(6,8,58),(6,9,59),(6,10,60),(7,1,61),(7,2,62),(7,3,63),(7,4,64),(7,5,65),(7,6,66),(7,7,67),(7,8,68),(7,9,69),(7,10,70),(8,1,71),(8,2,72),(8,3,73),(8,4,74),(8,5,75),(8,6,76),(8,7,77),(8,8,78),(8,9,79),(8,10,80),(9,1,81),(9,2,82),(9,3,83),(9,4,84),(9,5,85),(9,6,86),(9,7,87),(9,8,88),(9,9,89),(9,10,90),(10,1,91),(10,2,92),(10,3,93),(10,4,94),(10,5,95),(10,6,96),(10,7,97),(10,8,98),(10,9,99),(10,10,100);
/*!40000 ALTER TABLE `Location` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-04-02 21:30:34
