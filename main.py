import parser
import subprocess
import time

checkWaitTime = 20
pathToConfirmedCsv = "/home/pi/korona/czech-covid-db/records_confirmed.csv"
pathToRecoveredCsv = "/home/pi/korona/czech-covid-db/records_recovered.csv"
pathToDeathsCsv = "/home/pi/korona/czech-covid-db/records_deaths.csv"
pathToCurrentNumbers = "/home/pi/korona/czech-covid-db/current_numbers.json"
updateCommand = "git_coviddb_update.sh"

parsing = parser.Parser()

while True:
    result = parsing.parse(pathToConfirmedCsv, pathToRecoveredCsv, pathToDeathsCsv, pathToCurrentNumbers)
    print(result)
    if result == True:
        print("Running update command")
        subprocess.run(updateCommand.split())
    time.sleep(checkWaitTime)
