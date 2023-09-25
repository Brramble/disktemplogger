# DiskTempLogger
Record disk temps from `smartctl` to csv and interpret them via HTML and PHP.

# Installation
1. Run `temp.py` on cronjob. E.g every 30 minutes.
2. Include `index.php` within your webserver.
3. Point `index.php` to location of csv generated by Python

![Temp chart](https://i.imgur.com/1BsSggz.png)
