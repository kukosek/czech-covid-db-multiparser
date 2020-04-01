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
import sys
from datetime import timedelta
import csvdbtools

class Parser:
    datetimeFormat = "%Y-%m-%dT%H:%M:%S+00:00"
    
    datetimeFormatUzisHtml = "k %d.\xa0%m.\xa0%Y\xa0v\xa0%H.%M\xa0h"
    datetimeFormatUzis = "%Y-%m-%d"
    columnNamesConfirmedUzis = ["Record number", "Date", "All", "Hlavní město Praha",
                   "Středočeský kraj", "Ústecký kraj", "Královéhradecký kraj",
                   "Zlínský kraj", "Olomoucký kraj", "Pardubický kraj",
                   "Kraj Vysočina", "Plzeňský kraj", "Jihomoravský kraj",
                   "Liberecký kraj", "Karlovarský kraj", "Moravskoslezský kraj",
                   "Jihočeský kraj"]
    columnNamesRecoveredDeathsTest = ["Record number", "Date", "All"]
    columnNamesImport = ["Record number", "Date", "All"]
    columnNamesAgeGroups = ["Record number", "Date", "Average age", "0-17","18-34","35-49","50-67","68-85","86+"]

    CZNUTS3 = {"CZ010":"Hlavní město Praha",
               "CZ020":"Středočeský kraj",
               "CZ031":"Jihočeský kraj",
               "CZ032":"Plzeňský kraj",
               "CZ041":"Karlovarský kraj",
               "CZ042":"Ústecký kraj",
               "CZ051":"Liberecký kraj",
               "CZ052":"Královéhradecký kraj",
               "CZ053":"Pardubický kraj",
               "CZ063":"Kraj Vysočina",
               "CZ064":"Jihomoravský kraj",
               "CZ071":"Olomoucký kraj",
               "CZ072":"Zlínský kraj",
               "CZ080":"Moravskoslezský kraj"
            }
    def __init__(self):
        locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
        pass

    def parse_MZCR(self, pathToTestsCSV, pathToConfirmedCSV,pathToRecoveredCSV, pathToDeathsCSV, pathToImportsCSV, pathToAgeGroupsCSV, pathToCurrentNumbersJSON):
        try:
            fp = urllib.request.urlopen("https://onemocneni-aktualne.mzcr.cz/covid-19")
            html = fp.read().decode("utf8")
            fp.close
        except urllib.error.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
            return False
        except urllib.error.URLError as e:
            logging.error('URLError = ' + str(e.reason))
            return False

        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception:
            logging.error("BeatifulSoupException:\n")
            return False
        
        all = {"tested":{"number":"", "date":""},
              "confirmed":{"number":"", "date":""},
              "confirmedImported":{"number":0, "date":""},
              "confirmedBySex":{"male":0, "female":0},
              "confirmedByAgeGroup":{},
              "confirmedAverageAge": 0,
              "recovered":{"number":"", "date":""},
              "deaths":     {"number":"", "date":""},}
        try:
            with open(pathToCurrentNumbersJSON, "r") as file:
                try:
                    fileJson = json.load(file)
                    if len(fileJson) == len(all): all = fileJson
                except ValueError:
                    pass
        except OSError:
            pass
        update = False

        tested = soup.find(id="count-test").get_text().replace(" ", "")
        confirmed = soup.find(id="count-sick").get_text().replace(" ", "")
        recovered = soup.find(id="count-recover").get_text().replace(" ", "")
        deaths = soup.find(id="count-dead").get_text().replace(" ", "")
        if (all["tested"]["number"] != tested or all["confirmed"]["number"] != confirmed or all["recovered"]["number"] != recovered or all["deaths"]["number"] != deaths):
            datep = soup.find_all("p", class_="h3 mt-10 text--center")
            datep += soup.find_all("p", class_="h3 mt-10 text--center text--white")
            all["tested"]["number"] = tested
            all["tested"]["date"] = datetime.strptime(datep[2].get_text(), self.datetimeFormatUzisHtml).strftime(self.datetimeFormat) 

            all["confirmed"]["number"] = confirmed
            all["confirmed"]["date"] = datetime.strptime(datep[3].get_text(), self.datetimeFormatUzisHtml).strftime(self.datetimeFormat)

            recoveredDtObj = datetime.strptime(datep[0].get_text(), self.datetimeFormatUzisHtml)
            csvdbtools.csvAppendIfNew(recoveredDtObj, recovered, None, pathToRecoveredCSV)
            all["recovered"]["number"] = recovered
            all["recovered"]["date"] = recoveredDtObj.strftime(self.datetimeFormat)
            
            deathsDtObj = datetime.strptime(datep[1].get_text(), self.datetimeFormatUzisHtml)
            csvdbtools.csvAppendIfNew(deathsDtObj, deaths, None, pathToDeathsCSV)
            all["deaths"]["number"] = deaths
            all["deaths"]["date"] = datetime.strftime(deathsDtObj, self.datetimeFormat)

            update = True
        if(update):
            totalConfirmedColumns = []
            persons = {}
            try:
                fp = urllib.request.urlopen("https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/testy.csv")
                testsStr = fp.read().decode("utf8")
                fp.close
                reader = csv.reader(testsStr.replace("\r", "").split('\n'), delimiter=',')
                with open(pathToTestsCSV, 'w+') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(self.columnNamesRecoveredDeathsTest)
                    i = 0
                    for row in reader:
                        if (i > 0 and len(row) >= 3):
                            writer.writerow([i, row[0], row[2]])
                        if len(row) >= 3: i+=1
                fp = urllib.request.urlopen("https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/nakaza.csv")
                totalConfirmedStr = fp.read().decode("utf8")
                fp.close
                reader = csv.reader(totalConfirmedStr.replace("\r", "").split('\n'), delimiter=',')
                for row in reader:
                    totalConfirmedColumns.append(row)
                fp = urllib.request.urlopen("https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/osoby.min.json")
                persons = json.loads(fp.read().decode("utf8"))
                fp.close
            except urllib.error.HTTPError as e:
                logging.error('HTTPError = ' + str(e.code))
                return False
            except urllib.error.URLError as e:
                logging.error('URLError = ' + str(e.reason))
                return False
            if len(totalConfirmedColumns[-1]) == 0: totalConfirmedColumns.pop()
            if (totalConfirmedColumns[-1][2] != all["confirmed"]["number"]):
                dtOfCur = datetime.strptime(all["confirmed"]["date"], self.datetimeFormat)
                if datetime.strptime(totalConfirmedColumns[-1][0], self.datetimeFormatUzis).date() == dtOfCur.date():
                    totalConfirmedColumns[-1][2] = all["confirmed"]["number"]
                else:
                    totalConfirmedColumns.append([datetime.strftime(dtOfCur, self.datetimeFormatUzis), totalConfirmedColumns[-1][1], all["confirmed"]["number"]])
            newInDay = {}
            confirmedAgeSum = 0
            importedByCountry = {}
            for person in persons:
                curPersDate = person["DatumHlaseni"]
                if curPersDate not in newInDay:
                    newInDay[curPersDate] = {"ageSum":0, "newConfirmedCases":{"All":0}, "newImportedCases":{"All":0}, "confirmedByAgeGroup":{"0-17":0,"18-34":0,"35-49":0,"50-67":0,"68-85":0,"86+":0}}
                newInDay[curPersDate]["newConfirmedCases"]["All"] += 1
                if person["KHS"] not in newInDay[curPersDate]["newConfirmedCases"]:
                    newInDay[curPersDate]["newConfirmedCases"][person["KHS"]] = 0
                newInDay[curPersDate]["newConfirmedCases"][person["KHS"]] += 1
                if person["Pohlavi"] == 'Z':
                    all["confirmedBySex"]["female"] += 1
                else:
                    all["confirmedBySex"]["male"] += 1

                if person["Import"] == '1':
                    all["confirmedImported"]["number"]+=1
                    if all["confirmedImported"]["date"] != "":
                        lastDateObj = datetime.strptime(all["confirmedImported"]["date"], self.datetimeFormatUzis)
                        curPersDateObj = datetime.strptime(curPersDate, self.datetimeFormatUzis)
                        if (curPersDateObj>lastDateObj):
                            all["confirmedImported"]["date"] = curPersDate
                    else:
                        all["confirmedImported"]["date"] = curPersDate
                    newInDay[curPersDate]["newImportedCases"]["All"] += 1
                    if person["ImportZemeCsuKod"] != "":
                        if person["ImportZemeCsuKod"] not in importedByCountry:
                            importedByCountry[person["ImportZemeCsuKod"]] = 0
                        importedByCountry[person["ImportZemeCsuKod"]] += 1
                        if person["ImportZemeCsuKod"] not in newInDay[curPersDate]["newImportedCases"]:
                            newInDay[curPersDate]["newImportedCases"][person["ImportZemeCsuKod"]] = 0
                        newInDay[curPersDate]["newImportedCases"][person["ImportZemeCsuKod"]] += 1
                personAge = int(person["Vek"])
                if personAge<18:
                    newInDay[curPersDate]["confirmedByAgeGroup"]["0-17"] += 1
                elif personAge >= 18 and personAge <= 34:
                    newInDay[curPersDate]["confirmedByAgeGroup"]["18-34"] += 1
                elif personAge >= 35 and personAge <= 49:
                    newInDay[curPersDate]["confirmedByAgeGroup"]["35-49"] += 1
                elif personAge >= 50 and personAge <= 67:
                    newInDay[curPersDate]["confirmedByAgeGroup"]["50-67"] += 1
                elif personAge >= 68 and personAge <= 85:
                    newInDay[curPersDate]["confirmedByAgeGroup"]["68-85"] += 1
                elif personAge >= 86:
                    newInDay[curPersDate]["confirmedByAgeGroup"]["86+"] += 1
                newInDay[curPersDate]["ageSum"] += personAge
                confirmedAgeSum += personAge
            all["confirmedAverageAge"] = confirmedAgeSum/len(persons)

            importCountriesSorted = list(reversed(sorted(importedByCountry, key=importedByCountry.get)))
            self.columnNamesImport += importCountriesSorted

            with open(pathToAgeGroupsCSV, 'w+') as csvfile0:
                agWriter = csv.DictWriter(csvfile0, fieldnames=self.columnNamesAgeGroups)
                agWriter.writeheader()
                with open(pathToImportsCSV, 'w+') as csvfile1:
                    imWriter = csv.DictWriter(csvfile1, fieldnames=self.columnNamesImport)
                    imWriter.writeheader()
                    with open(pathToConfirmedCSV, 'w+') as csvfile2:
                        conWriter = csv.DictWriter(csvfile2, fieldnames=self.columnNamesConfirmedUzis)
                        conWriter.writeheader()

                        valuesStarted = False
                        lastSum = 0
                        lastNumOfKhsReported = 0
                        lastWorkingDate = None
                        recordNumber = 0
                        lastConfirmedPerRegion = {}
                        importedSum = 0
                        lastImportedPerCountry = {}
                        lastConfirmedByAgeGroup = {"0-17":0,"18-34":0,"35-49":0,"50-67":0,"68-85":0,"86+":0}
                        for i in range(1, len(totalConfirmedColumns)):
                            if (len(totalConfirmedColumns[i]) == 3):
                                if (valuesStarted):
                                    currDate = totalConfirmedColumns[i][0]
                                    currSum = None
                                    currNumOfKhsReported = None
                                    if currDate in newInDay:
                                        lastWorkingDate = datetime.strptime(currDate, self.datetimeFormatUzis)
                                        currSum = lastSum + newInDay[currDate]["ageSum"]
                                        currNumOfKhsReported = lastNumOfKhsReported + newInDay[currDate]["newConfirmedCases"]["All"]
                                        for key, value in newInDay[currDate]["newConfirmedCases"].items():
                                            if (key != "All"):
                                                name = self.CZNUTS3[key]
                                                if name not in lastConfirmedPerRegion: lastConfirmedPerRegion[name] = 0
                                                lastConfirmedPerRegion[name] += value
                                        for key, value in newInDay[currDate]["newImportedCases"].items():
                                            if (key != "All"):
                                                if key not in lastImportedPerCountry: lastImportedPerCountry[key] = 0
                                                lastImportedPerCountry[key] += value
                                            else:
                                                importedSum += value
                                        for key, value in newInDay[currDate]["confirmedByAgeGroup"].items():
                                            lastConfirmedByAgeGroup[key] += value
                                    else:
                                        startCheckDate = None
                                        if i == 0 or lastWorkingDate == None:
                                            startCheckDate = datetime.strptime(sorted(newInDay.keys())[0], self.datetimeFormatUzis)
                                        else:
                                            startCheckDate = lastWorkingDate+timedelta(days=1)
                                        for j in range((datetime.strptime(currDate, self.datetimeFormatUzis)-startCheckDate).days):
                                            tryThatDate = datetime.strftime(startCheckDate+timedelta(days=j), self.datetimeFormatUzis)
                                            if tryThatDate in newInDay:
                                                currSum = lastSum + newInDay[tryThatDate]["ageSum"]
                                                currNumOfKhsReported = lastNumOfKhsReported + newInDay[tryThatDate]["newConfirmedCases"]["All"]
                                                lastSum = currSum
                                                lastNumOfKhsReported = currNumOfKhsReported
                                                for key, value in newInDay[tryThatDate]["newConfirmedCases"].items():
                                                    if (key != "All"):
                                                        name = self.CZNUTS3[key]
                                                        if name not in lastConfirmedPerRegion: lastConfirmedPerRegion[name] = 0
                                                        lastConfirmedPerRegion[name] += value
                                                for key, value in newInDay[tryThatDate]["newImportedCases"].items():
                                                    if (key != "All"):
                                                        if key not in lastImportedPerCountry: lastImportedPerCountry[key] = 0
                                                        lastImportedPerCountry[key] += value
                                                    else:
                                                        importedSum += value
                                                for key, value in newInDay[tryThatDate]["confirmedByAgeGroup"].items():
                                                    lastConfirmedByAgeGroup[key] += value
                                    currRowCon = {**{"Record number":recordNumber, "Date":currDate, "All":totalConfirmedColumns[i][2]}, **lastConfirmedPerRegion}
                                    currRowIm = {**{"Record number":recordNumber, "Date":currDate, "All":importedSum}, **lastImportedPerCountry}
                                    currRowAg = {**{"Record number":recordNumber, "Date":currDate, "Average age":currSum/currNumOfKhsReported}, **lastConfirmedByAgeGroup}
                                    conWriter.writerow(currRowCon)
                                    imWriter.writerow(currRowIm)
                                    agWriter.writerow(currRowAg)
                                    lastSum = currSum
                                    lastNumOfKhsReported = currNumOfKhsReported
                                    recordNumber += 1
                                else:
                                    if (int(totalConfirmedColumns[i][2]) != 0):
                                        valuesStarted = True
                        all["confirmedByAgeGroup"] = lastConfirmedByAgeGroup
            with open(pathToCurrentNumbersJSON, "w+") as jsonfile:
                json.dump(all, jsonfile)