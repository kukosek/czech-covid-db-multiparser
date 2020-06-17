import uzisparser
import parser
import subprocess
import time
import logging
from datetime import datetime
checkWaitTime = 60
pathToTestsUZISCsv = "/home/pi/korona/czech-covid-db/uzis/records_tests_uzis.csv"
pathToConfirmedUZISCsv = "/home/pi/korona/czech-covid-db/uzis/records_confirmed_uzis.csv"
pathToRecoveredUZISCsv = "/home/pi/korona/czech-covid-db/uzis/records_recovered_uzis.csv"
pathToDeathsUZISCsv = "/home/pi/korona/czech-covid-db/uzis/records_deaths_uzis.csv"
pathToImportsUZISCsv = "/home/pi/korona/czech-covid-db/uzis/records_imports_uzis.csv"
pathToAgeGroupsUZISCsv = "/home/pi/korona/czech-covid-db/uzis/records_confirmed-agegroups_uzis.csv"
pathToCurrentNumbersUZIS = "/home/pi/korona/czech-covid-db/uzis/current_numbers_uzis.json"

pathToConfirmedCsv = "/home/pi/korona/czech-covid-db/records_confirmed.csv"
pathToRecoveredCsv = "/home/pi/korona/czech-covid-db/records_recovered.csv"
pathToDeathsCsv = "/home/pi/korona/czech-covid-db/records_deaths.csv"
pathToCurrentNumbers = "/home/pi/korona/czech-covid-db/current_numbers.json"

updateCommand = "/home/pi/korona/czech-covid-db-multiparser/git_coviddb_update.sh"
logFile = "main.log"


parsing = parser.Parser()
uzisparsing = uzisparser.Parser()


logging.basicConfig(filename=logFile, level=logging.DEBUG)
logging.info("-------------------------------")
logging.info(datetime.now().strftime("%d.%m. %H:%M")+" Starting check loop")

try:
    while True:
        resultUzis = uzisparsing.parse_MZCR(pathToTestsUZISCsv, pathToConfirmedUZISCsv,pathToRecoveredUZISCsv, pathToDeathsUZISCsv, pathToImportsUZISCsv, pathToAgeGroupsUZISCsv, pathToCurrentNumbersUZIS)
        result = parsing.parse(pathToConfirmedCsv, pathToRecoveredCsv, pathToDeathsCsv, pathToCurrentNumbers)
        if updateCommand != "" and (result == True or resultUzis == True):
            logging.info("Running update command")
            logging.info("")
            
            logging.info(subprocess.run(updateCommand.split(), capture_output=True).stdout)
        time.sleep(checkWaitTime)
except KeyboardInterrupt:
    logging.info(datetime.now().strftime("%d.%m. %H:%M")+"Interrupted, exiting...")
