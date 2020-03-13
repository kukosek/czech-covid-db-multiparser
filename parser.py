import urllib.request
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import locale
from datetime import datetime
import csv
import json

class Parser:
    datetimeFormat = "%Y-%m-%dT%H:%M:%S+01:00"
    columnNames = ["Record number", "Date", "All"]
    def __init__(self):
        locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
        pass

    def csvAppendIfNew(self, datetimeObj, value, pathToCsv):
        rows = []
        newInformation = False
        with open(pathToCsv, mode='r', newline='') as records_file:
            csvreader = csv.DictReader(records_file, fieldnames=self.columnNames)
            i = 0
            for row in csvreader:
                
                if i>0:
                    rowData = []
                    for columnName in self.columnNames:
                        rowData.append(row[columnName])
                    rows.append(rowData)
                i+=1
            if len(rows) == 0 or (len(rows) > 0 and rows[-1][2] != value):
                newInformation = True
        if (newInformation == True):
            print("New info, saving to", pathToCsv)
            if datetimeObj.date() == datetime.today().date():
                datetimeObj = datetime.now()
            elif datetimeObj.date() < datetime.today().date():
                if (len(rows) > 0):
                    lastDateWrited = datetime.strptime(rows[-1][1], self.datetimeFormat)
                    if (lastDateWrited.date() == datetimeObj.date()):
                        #place the date in the somewhere in the half
                        nextDayDatetime = datetimeObj.date() + datetime.timedelta(days=1)
                        datetimeObj = lastDateWrited + ( (nextDayDatetime - lastDateWrited) / 2 )
            else:
                print("Error: time is greater than my time. Are we time travelling?")
            datetimeConverted = datetimeObj.strftime(self.datetimeFormat)
            print(datetimeConverted)
            fileOpenMethod = "a"
            # if no rows are in the file, open it with w+, which will delete the contents. this is to avoid having an empty first line
            if len(rows)==0: fileOpenMethod = "w+"
            with open(pathToCsv,fileOpenMethod, newline='') as records_file:
                
                if len(rows) == 0:
                    writer = csv.writer(records_file)
                    writer.writerow(self.columnNames)
                id = 0
                if len(rows) > 0:
                    id = rows[-1][0]
                writer = csv.DictWriter(records_file, fieldnames=self.columnNames)
                writer.writerow({self.columnNames[0]:id, self.columnNames[1]:datetimeConverted, self.columnNames[2]:value})
        return newInformation

    def parse(self, pathToConfirmedCSV, pathToRecoveredCSV, pathToDeathsCSV, pathToCurrentNumbersJSON):
        fp = urllib.request.urlopen("https://cs.wikipedia.org/wiki/Pandemie_COVID-19_v_%C4%8Cesku#Ned%C4%9Ble_1._b%C5%99ezna")
        html = fp.read().decode("utf8")
        fp.close
        
        soup = BeautifulSoup(html, 'html.parser')

        all = {"confirmed":{"number":"", "date":""},
              "recovered":{"number":"", "date":""},
              "deaths":     {"number":"", "date":""}}
        update = False

        print()
        # parsing current numbers
        for trTag in soup.find_all('tr'):
            allThTags = trTag.find_all('th')
            if len(allThTags) == 1:
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
                    appended = self.csvAppendIfNew(dateobject, num, pathToConfirmedCSV)
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
                    appended = self.csvAppendIfNew(dateobject, num, pathToRecoveredCSV)
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
                    appended = self.csvAppendIfNew(dateobject, num, pathToDeathsCSV)
                    if appended: update = True
        with open(pathToCurrentNumbersJSON, "w+") as jsonfile:
            json.dump(all, jsonfile)
        return update