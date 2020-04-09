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
    datetimeFormat = "%Y-%m-%dT%H:%M:%S+02:00"
    columnNames = ["Record number", "Date", "All", "Hlavní město Praha",
                   "Středočeský kraj", "Ústecký kraj", "Královéhradecký kraj",
                   "Zlínský kraj", "Olomoucký kraj", "Pardubický kraj",
                   "Kraj Vysočina", "Plzeňský kraj", "Jihomoravský kraj",
                   "Liberecký kraj", "Karlovarský kraj", "Moravskoslezský kraj",
                   "Jihočeský kraj"]
    def __init__(self):
        locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')
        pass

    def parse(self, pathToConfirmedCSV, pathToRecoveredCSV, pathToDeathsCSV, pathToCurrentNumbersJSON):
        try:
            fp = urllib.request.urlopen("https://cs.wikipedia.org/w/api.php?action=parse&page=Pandemie_covidu-19_v_%C4%8Cesku&prop=text&formatversion=2&format=json")
            html = json.loads(fp.read().decode("utf8"))["parse"]["text"]
            fp.close
        except urllib.error.HTTPError as e:
            logging.error('HTTPError = ' + str(e.code))
            return False
        except urllib.error.URLError as e:
            logging.error('URLError = ' + str(e.reason))
            return False
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logging.error("BeatifulSoupException:\n"+str(e.reason))
        all = {"confirmed":{"number":"", "date":""},
              "recovered":{"number":"", "date":""},
              "deaths":     {"number":"", "date":""}}
        with open(pathToCurrentNumbersJSON, "r") as file:
            try:
                fileJson = json.load(file);
                if len(fileJson) == len(all): all = fileJson
            except ValueError:
                pass
        update = False
        try:
            # parsing current numbers
            confirmedPerKraj = {}
            for trTag in soup.find_all('tr'):
                allThTags = trTag.find_all('th')
                if len(allThTags) == 1:
                    """
                    if allThTags[0].get_text() == "Rozšíření":
                        textRozsireni = trTag.find_all("td")[0].get_text()
                        infoPerKraj = textRozsireni.splitlines()[3:]
                        for krajInfo in infoPerKraj:
                            krajName, confirmedInKraj = krajInfo.split("(")
                            krajName = krajName.strip()
                            confirmedInKraj = "".join(filter(str.isdigit, confirmedInKraj[:-1]))
                            confirmedPerKraj[krajName] = confirmedInKraj
                    """
                    if allThTags[0].get_text() == "Nakažení":
                        textConfirmed = trTag.find_all("td")[0].get_text()
                        num, date = textConfirmed.split("(",2)
                        num = "".join(filter(str.isdigit, num))
                        date = date.strip().replace("(", "").replace(")", "")
                        dateobject = None
                        try:
                            dateobject = datetime.strptime(date, "%d. %B %Y")
                        except ValueError:
                            return False
                        all["confirmed"]["number"]=num
                        
                        
                        # here comes csv handling
                        appended = csvdbtools.csvAppendIfNew(dateobject, num, None, pathToConfirmedCSV)
                        if appended:
                            update = True
                            if dateobject.date() == datetime.today().date():
                                datetimeConverted = datetime.now().strftime(self.datetimeFormat)
                            else:
                                datetimeConverted = dateobject.strftime(self.datetimeFormat)
                            all["confirmed"]["date"]=datetimeConverted
                    if allThTags[0].get_text() == "Zotavení":
                        textConfirmed = trTag.find_all("td")[0].get_text()
                        num, date = textConfirmed.split("(",2)
                        num = "".join(filter(str.isdigit, num))
                        date = date.strip().replace("(", "").replace(")", "")
                        dateobject = None
                        try:
                            dateobject = datetime.strptime(date, "%d. %B %Y")
                        except ValueError:
                            return False
                        all["recovered"]["number"]=num
                        
                        # here comes csv handling
                        appended = csvdbtools.csvAppendIfNew(dateobject, num, None, pathToRecoveredCSV)
                        if appended:
                            update = True
                            if dateobject.date() == datetime.today().date():
                                datetimeConverted = datetime.now().strftime(self.datetimeFormat)
                            else:
                                datetimeConverted = dateobject.strftime(self.datetimeFormat)
                            all["recovered"]["date"]=datetimeConverted
                    if allThTags[0].get_text() == "Úmrtí":
                        textConfirmed = trTag.find_all("td")[0].get_text()
                        num, date = textConfirmed.split("(",2)
                        num = "".join(filter(str.isdigit, num))
                        date = date.strip().replace("(", "").replace(")", "")
                        dateobject = None
                        try:
                            dateobject = datetime.strptime(date, "%d. %B %Y")
                        except ValueError:
                            return False
                        all["deaths"]["number"]=num

                        # here comes csv handling
                        appended = csvdbtools.csvAppendIfNew(dateobject, num, None, pathToDeathsCSV)
                        if appended:
                            update = True
                            if dateobject.date() == datetime.today().date():
                                datetimeConverted = datetime.now().strftime(self.datetimeFormat)
                            else:
                                datetimeConverted = dateobject.strftime(self.datetimeFormat)
                            all["deaths"]["date"]=datetimeConverted
                    if (update):
                        pass
        except:
            logging.error("Unexpected error:\n"+str(sys.exc_info()[0]))
            raise
        if(update):
            with open(pathToCurrentNumbersJSON, "w+") as jsonfile:
                json.dump(all, jsonfile)
        return update
