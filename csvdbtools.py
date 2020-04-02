import csv
import logging
from datetime import datetime
from datetime import timedelta

datetimeFormatLong = "%Y-%m-%dT%H:%M:%S+02:00"
datetimeFormatShort = "%Y-%m-%d"
columnNamesRecoveredDeathsTest = ["Record number", "Date", "All"]
def csvAppendIfNew(datetimeObj, value, casesPerKraj, pathToCsv):
    headerRow = []
    rows = []
    newInformation = False
    with open(pathToCsv, mode='r', newline='') as records_file:
        csvreader = csv.reader(records_file)
        for row in csvreader:
            headerRow = row
            break
        
        csvreader = csv.DictReader(records_file, fieldnames=columnNamesRecoveredDeathsTest)
        i = 0
        for row in csvreader:
            rowData = []
            for columnName in columnNamesRecoveredDeathsTest:
                rowData.append(row[columnName])
            rows.append(rowData)
    lastRow = rows[-1]
    if len(rows) == 0 or (len(rows) == 1 and rows[0][0] == columnNamesRecoveredDeathsTest[0]) or (len(rows) > 0 and lastRow[2] != value):
        newInformation = True
    elif casesPerKraj != None:
        i = 0
        for krajName in columnNamesRecoveredDeathsTest[3:]:
            if lastRow[i+3] != casesPerKraj[krajName]:
                newInformation = True
                break
            i+=1
    #check if confirmed cases in kraj is different
    
    if len(rows) != 0 and headerRow != columnNamesRecoveredDeathsTest:
        with open(pathToCsv, mode='w', newline='') as records_file:
            writer = csv.writer(records_file)
            writer.writerow(columnNamesRecoveredDeathsTest)
            for row in rows:
                writer.writerow(row)
    if (newInformation == True):
        logging.info("New info, saving to "+pathToCsv)
        if ("uzis" not in pathToCsv):
            if datetimeObj.date() == datetime.today().date():
                datetimeObj = datetime.now()
            elif datetimeObj.date() < datetime.today().date():
                if (len(rows) > 0):
                    datetimeObj.replace(hour=0, minute=0)
                    
                    lastDateWrited = None
                    if len(lastRow[1]) > 10:
                        lastDateWrited = datetime.strptime(lastRow[1], datetimeFormatLong)
                    else:
                        lastDateWrited = datetime.strptime(lastRow[1], datetimeFormatShort)
                    if (lastDateWrited.date() == datetimeObj.date()):
                        #place the date in the somewhere in the half
                        nextDayDatetime = (datetimeObj + timedelta(days=1)).replace(hour=0, minute=0)
                        datetimeObj = lastDateWrited + ( (nextDayDatetime - lastDateWrited) / 2 )
            else:
                logging.error("Error: time is greater than my time. Are we time travelling?")
        
        datetimeConverted = None
        if (datetimeObj.hour == 0 and datetimeObj.minute ==0):
            datetimeConverted = datetimeObj.strftime(datetimeFormatShort)
        else:
            datetimeConverted = datetimeObj.strftime(datetimeFormatLong)
        fileOpenMethod = "a"
        # if no rows are in the file, open it with w+, which will delete the contents. this is to avoid having an empty first line
        
        
        
        if len(rows)==0: fileOpenMethod = "w+"
        with open(pathToCsv,fileOpenMethod, newline='') as records_file:
            
            if len(rows) == 0:
                writer = csv.writer(records_file)
                writer.writerow(columnNamesRecoveredDeathsTest)
            id = 0
            if len(rows) > 0:
                id = str(int(rows[-1][0])+1)
            writer = csv.DictWriter(records_file, fieldnames=columnNamesRecoveredDeathsTest)
            rowToWrite = {columnNamesRecoveredDeathsTest[0]:id, columnNamesRecoveredDeathsTest[1]:datetimeConverted, columnNamesRecoveredDeathsTest[2]:value}
            if casesPerKraj != None and  len(casesPerKraj)==len(columnNamesRecoveredDeathsTest[3:]):
                for key, value in casesPerKraj.items():
                    rowToWrite[key] = value
            writer.writerow(rowToWrite)
    return newInformation
