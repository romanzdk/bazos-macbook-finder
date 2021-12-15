# Find your secondhand Macbook on Bazos.cz easily

## Requirements
* python
* python libraries (`requirements.txt`)

## [Optional] Inputs
* **ZIP_CODE** - zip code in CZ to search macbooks in (e.g. '50')
* **DISTANCE** - distance in km from selected zip code (e.g. '10100')
* **MIN_PRICE** - minimal price in CZK for the macbook (e.g. '10000')
* **MAX_PRICE** - maximal price in CZK for the macbook (e.g. '50000')
* **ADS** - number of ads to go through (e.g. 20, 40, 80 - 20 per page)

![Bazos ads preview](/img/bazos.png "Bazos preview")

## Output
* csv file with all ads (data/all.csv)
* csv file with macbooks air (data/airs.csv)
* csv file with macbooks pro (data/pros.csv)
* main method also returns list of pandas dataframes with *airs* and *pros* 

![Script output preview](/img/output.png "Script output preview")

## Run
`python bazos.py` or run inside `bazos_macbooks.ipynb` jupyter notebook

## Improve
* better parsing (years & cpu mainly)
* move arguments to command line (e.g. for price, distance...) `python bazos.py -min_p 25000 ...`
* run automatically for all existing pages (not specifying page ranges manually)
* better filtering of final `airs` and `pros` tables
* return only new entries (difference from previous run)