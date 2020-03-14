import urllib.request
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import locale
from datetime import datetime
import csv
import json
import logging

class Parser:
    datetimeFormat = "%Y-%m-%dT%H:%M:%S+01:00"
    columnNames = ["Record number", "Date", "All", "hlavní město Praha",
                   "Středočeský kraj", "Ústecký kraj", "Královéhradecký kraj",
                   "Zlínský kraj", "Olomoucký kraj", "Pardubický kraj",
                   "Kraj Vysočina", "Plzeňský kraj", "Jihomoravský kraj",
                   "Liberecký kraj", "Karlovarský kraj", "Moravskoslezský kraj",
                   "Jihočeský kraj"]
    def __init__(self):
        locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
        pass

    def csvAppendIfNew(self, datetimeObj, value, casesPerKraj, pathToCsv):
        headerRow = []
        rows = []
        newInformation = False
        with open(pathToCsv, mode='r', newline='') as records_file:
            csvreader = csv.reader(records_file)
            for row in csvreader:
                headerRow = row
                break
            
            csvreader = csv.DictReader(records_file, fieldnames=self.columnNames)
            i = 0
            for row in csvreader:
                rowData = []
                for columnName in self.columnNames:
                    rowData.append(row[columnName])
                rows.append(rowData)
        lastRow = rows[-1]
        if len(rows) == 0 or (len(rows) == 1 and rows[0][0] == self.columnNames[0]) or (len(rows) > 0 and lastRow[2] != value):
            newInformation = True
        elif casesPerKraj != None:
            i = 0
            for krajName in self.columnNames[3:]:
                if lastRow[i+3] != casesPerKraj[krajName]:
                    newInformation = True
                    break
                i+=1
        #check if confirmed cases in kraj is different
        
        if len(rows) != 0 and headerRow != self.columnNames:
            with open(pathToCsv, mode='w', newline='') as records_file:
                writer = csv.writer(records_file)
                writer.writerow(self.columnNames)
                for row in rows:
                    writer.writerow(row)
        if (newInformation == True):
            logging.info("New info, saving to", pathToCsv)
            if datetimeObj.date() == datetime.today().date():
                datetimeObj = datetime.now()
            elif datetimeObj.date() < datetime.today().date():
                if (len(rows) > 0):
                    lastDateWrited = datetime.strptime(lastRow[1], self.datetimeFormat)
                    if (lastDateWrited.date() == datetimeObj.date()):
                        #place the date in the somewhere in the half
                        nextDayDatetime = datetimeObj.date() + datetime.timedelta(days=1)
                        datetimeObj = lastDateWrited + ( (nextDayDatetime - lastDateWrited) / 2 )
            else:
                logging.error("Error: time is greater than my time. Are we time travelling?")
            datetimeConverted = datetimeObj.strftime(self.datetimeFormat)
            fileOpenMethod = "a"
            # if no rows are in the file, open it with w+, which will delete the contents. this is to avoid having an empty first line
            
            
            
            if len(rows)==0: fileOpenMethod = "w+"
            with open(pathToCsv,fileOpenMethod, newline='') as records_file:
                
                if len(rows) == 0:
                    writer = csv.writer(records_file)
                    writer.writerow(self.columnNames)
                id = 0
                if len(rows) > 0:
                    id = str(int(rows[-1][0])+1)
                writer = csv.DictWriter(records_file, fieldnames=self.columnNames)
                rowToWrite = {self.columnNames[0]:id, self.columnNames[1]:datetimeConverted, self.columnNames[2]:value}
                if casesPerKraj != None and  len(casesPerKraj)==len(self.columnNames[3:]):
                    for key, value in casesPerKraj.items():
                        rowToWrite[key] = value
                writer.writerow(rowToWrite)
        return newInformation

    def parse(self, pathToConfirmedCSV, pathToRecoveredCSV, pathToDeathsCSV, pathToCurrentNumbersJSON):
        try:
            fp = urllib.request.urlopen("https://cs.wikipedia.org/w/api.php?action=parse&page=Pandemie_COVID-19_v_%C4%8Cesku&prop=text&formatversion=2&format=json")
            html = json.loads(fp.read().decode("utf8"))["parse"]["text"]
            fp.close
        except urllib.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
        except urllib.URLError as e:
            logging.error('URLError = ' + str(e.reason))
        except httplib.HTTPException as e:
            logging.error('HTTPException')
        
        soup = BeautifulSoup(html, 'html.parser')

        all = {"confirmed":{"number":"", "date":""},
              "recovered":{"number":"", "date":""},
              "deaths":     {"number":"", "date":""}}
        update = False
        # parsing current numbers
        confirmedPerKraj = {}
        for trTag in soup.find_all('tr'):
            allThTags = trTag.find_all('th')
            if len(allThTags) == 1:
                if allThTags[0].get_text() == "Rozšíření":
                    textRozsireni = trTag.find_all("td")[0].get_text()[:-9].replace("," , ";")
                    infoPerKraj = textRozsireni.split(";")
                    for krajInfo in infoPerKraj:
                        krajName, confirmedInKraj = krajInfo.split("(")
                        krajName = krajName.strip()
                        confirmedInKraj = confirmedInKraj[:-1].strip()
                        confirmedPerKraj[krajName] = confirmedInKraj
                if allThTags[0].get_text() == "Nakažení":
                    textConfirmed = trTag.find_all("td")[0].get_text()
                    num, date = textConfirmed.split("(",2)
                    num = num.strip()
                    date = date.strip().replace("(", "").replace(")", "")
                    dateobject = datetime.strptime(date, "%d. %B %Y")
                    all["confirmed"]["number"]=num
                    datetimeConverted = dateobject.strftime(self.datetimeFormat)
                    all["confirmed"]["date"]=datetimeConverted
                    
                    # here comes csv handling
                    appended = self.csvAppendIfNew(dateobject, num, confirmedPerKraj, pathToConfirmedCSV)
                    if appended: update = True
                if allThTags[0].get_text() == "Zotavení":
                    textConfirmed = trTag.find_all("td")[0].get_text()
                    num, date = textConfirmed.split("(",2)
                    num = num.strip()
                    date = date.strip().replace("(", "").replace(")", "")
                    dateobject = datetime.strptime(date, "%d. %B %Y")
                    all["recovered"]["number"]=num
                    datetimeConverted = dateobject.strftime(self.datetimeFormat)
                    all["recovered"]["date"]=datetimeConverted
                    # here comes csv handling
                    appended = self.csvAppendIfNew(dateobject, num, None, pathToRecoveredCSV)
                    if appended: update = True
                if allThTags[0].get_text() == "Úmrtí":
                    textConfirmed = trTag.find_all("td")[0].get_text()
                    num, date = textConfirmed.split("(",2)
                    num = num.strip()
                    date = date.strip().replace("(", "").replace(")", "")
                    dateobject = datetime.strptime(date, "%d. %B %Y")
                    all["deaths"]["number"]=num
                    datetimeConverted = dateobject.strftime(self.datetimeFormat)
                    all["deaths"]["date"]=datetimeConverted
                    # here comes csv handling
                    appended = self.csvAppendIfNew(dateobject, num, None, pathToDeathsCSV)
                    if appended: update = True
                if (update):
                    pass
        if(update):
            with open(pathToCurrentNumbersJSON, "w+") as jsonfile:
                json.dump(all, jsonfile)
        return update
