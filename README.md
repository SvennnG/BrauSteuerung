# BrauSteuerung
Raspberry Pi with LCD, TempSensor, Output Pins for Heating and stirring

**w1** for tempsensor (need to be enabled by raspberry)

**i2c** for LCD (driver from adabus)


#Mysql:
#####root / braupi2
(allowed from localhost + others)

```
sudo apt install mariadb-server
sudo mysql_secure_installation
sudo mysql -u root -p

    CREATE DATABASE brauSteuerung;
    CREATE USER 'brauer'@'localhost' IDENTIFIED BY 'Seelze!Bier8';
    GRANT ALL PRIVILEGES ON brauSteuerung.* TO 'brauer'@'localhost';
    FLUSH PRIVILEGES;

    CREATE TABLE `config` (
      `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `Proportionalbereich.neg` int NOT NULL DEFAULT '-11',
      `Proportionalbereich.pos` int NOT NULL DEFAULT '5'
    );

    CREATE TABLE `profil` (
      `id` tinyint NOT NULL AUTO_INCREMENT PRIMARY KEY,
      `Name` text NOT NULL,
      `Time1` int NOT NULL,
      `Temp1` int NOT NULL,
      `Time2` int NOT NULL,
      `Temp2` int NOT NULL,
      `Time3` int NOT NULL,
      `Temp3` int NOT NULL,
      `Time4` int NOT NULL,
      `Temp4` int NOT NULL
    );
```

db: brauSteuerung  
user: brauer  
pw: Seelze!Bier8  

Manage e.g. by Adminer (former phpmyadmin)  
http://192.168.178.59/adminer.php?username=brauer&db=brauSteuerung&select=config