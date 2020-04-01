import uzisparser
import parser
import subprocess
import time
import logging
from datetime import datetime
checkWaitTime = 20
pathToTestsUZISCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/records_tests_uzis.csv"
pathToConfirmedUZISCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/records_confirmed_uzis.csv"
pathToRecoveredUZISCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/records_recovered_uzis.csv"
pathToDeathsUZISCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/records_deaths_uzis.csv"
pathToImportsUZISCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/records_imports_uzis.csv"
pathToAgeGroupsUZISCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/records_confirmed-agegroups_uzis.csv"
pathToCurrentNumbersUZIS = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/uzis/current_numbers_uzis.json"

pathToConfirmedCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/records_confirmed.csv"
pathToRecoveredCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/records_recovered.csv"
pathToDeathsCsv = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/records_deaths.csv"
pathToCurrentNumbers = "/media/lukas/Data/Dokumenty/Programovani_Kodovani_Vsehochut/projects-bigger/korona/czech-covid-db/current_numbers.json"

updateCommand = ""
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
