Description of what's this purpose is at [czech-covid-db](https://github.com/kukosek/czech-covid-db). It runs on my raspberry pi
because I don't have a server with working python3.
## Files
* **csvdbtools.py** is a module with the function that handles CSV file row appending. It is used, when you have a number
you want to add to the CSV only if the previous record has a different number. So you provide the function these parameters:
datetime (the date, can be with time, when it changed to the value), value (the new number), casesPerKraj (currently not used),
pathToCsv (path to the csv file). When there is no previous record, it just appends it.
Otherwise it compares the value with the value of last row, and based on the result, it appends a new row.
It returns true or false, to let know
it the number was new and it appended, or same as the previous record and it did nothing.
* **parser.py** has a class with a function that parses the data from wikipedia, and if something changed,
it updates the current numbers JSON and calls the
csv function. The functions returns true if something changed
* **uzisparser.py** has a class with a function that parses from the [official website](https://onemocneni-aktualne.mzcr.cz/covid-19).  
Some info of what is does is at czech-covid-db readme. If something changed, it updates the current numbers JSON and calls the
csv function. The functions returns true if something changed
* **main.py** calls the parse functions every 60 seconds.  If one or both of the functions return true,
it runs the specified update command. The command is now set to run the script git_coviddb_update.sh, which
makes a new commit in the git repo and pushes it to github.
* _Other files in this repo aren't used_
