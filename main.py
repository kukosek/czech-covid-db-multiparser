import parser
import subprocess
import time
import logging
from datetime import datetime
checkWaitTime = 20
pathToConfirmedCsv = "/home/pi/korona/czech-covid-db/records_confirmed.csv"
pathToRecoveredCsv = "/home/pi/korona/czech-covid-db/records_recovered.csv"
pathToDeathsCsv = "/home/pi/korona/czech-covid-db/records_deaths.csv"
pathToCurrentNumbers = "/home/pi/korona/czech-covid-db/current_numbers.json"
updateCommand = "/home/pi/korona/czech-covid-db-wikipediaparser/git_coviddb_update.sh"
logFile = "main.log"


parsing = parser.Parser()
logging.basicConfig(filename=logFile, level=logging.DEBUG)
logging.info("-------------------------------")
logging.info(datetime.now().strftime("%d.%m. %H:%M")+" Starting check loop")

try:
    while True:
        result = parsing.parse(pathToConfirmedCsv, pathToRecoveredCsv, pathToDeathsCsv, pathToCurrentNumbers)
        if result == True:
            logging.info("Running update command")
            logging.info()
            
            logging.info(subprocess.run(updateCommand.split(), capture_output=True).stdout)
        time.sleep(checkWaitTime)
except KeyboardInterrupt:
    logging.info(datetime.now().strftime("%d.%m. %H:%M")+"Interrupted, exiting...")
