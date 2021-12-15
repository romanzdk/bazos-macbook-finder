# Find your secondhand Macbook on Bazos.cz easily

## Requirements
* running locally:
    * python (developed with 3.9.5)
    * python libraries (`requirements.txt`) + `ipykernel` in case of using jupyter notebook
* running in docker:
    * docker

## Run
* **locally**: `python bazos.py` or run inside `bazos_macbooks.ipynb` jupyter notebook
* **in docker**: 
    1. `docker build -t bazos .`
    2. `docker run -v "absolute/path/to/your/directory:/app/data" bazos`

## [Optional] Inputs
```
usage: bazos.py [-h] [--zip_code [ZIP_CODE]] [--dist [DIST]] [--min_p [MIN_P]] [--max_p [MAX_P]] [--n_ads [N_ADS]] [--send_email]

optional arguments:
    -h, --help            show this help message and exit
    --zip_code [ZIP_CODE] Zip code - e.g. 10500
    --dist [DIST]         Distance in km from zip code - e.g. 50
    --min_p [MIN_P]       Minimum price in CZK - e.g. 10000
    --max_p [MAX_P]       Maximum price in CZK - e.g. 50000
    --n_ads [N_ADS]       Number of ads to go through - e.g. 100
    --send_email          Whether to send an email with results
```

![Bazos ads preview](/img/bazos.png "Bazos preview")

## Output
* csv file with all ads (data/all.csv)
* csv file with macbooks air (data/airs.csv)
* csv file with macbooks pro (data/pros.csv)
* main method also returns list of pandas dataframes with *airs* and *pros* 
* possibility to send result tables as html to email via google SMTP server (yagmail)

![Script output preview](/img/output.png "Script output preview")

Example email output:
![Example email preview](/img/mail.png "Example email preview")

## Improve
* better parsing (years & cpu mainly)
* run automatically for all existing pages (not specifying page ranges manually)
* better filtering of final `airs` and `pros` tables
* return only new entries (difference from previous run)