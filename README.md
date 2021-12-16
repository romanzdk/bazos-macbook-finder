# Find your secondhand Macbook on Bazos.cz easily

![Bazos ads preview](/img/bazos.png "Bazos preview")

## Requirements
* running locally:
    * python (developed with 3.9.5)
    * python libraries (`requirements.txt`) + `ipykernel` in case of using jupyter notebook
* running in docker:
    * docker

## Run
* **locally**: `python bazos.py` [optional arguments - see [below](#inputs)] or run inside `bazos_macbooks.ipynb` jupyter notebook

* **in docker**: 
    1. `docker build -t bazos .`
    2. `docker run -v "absolute/path/to/your/directory:/app/data" bazos`

<h2 id="inputs">[Optional] Inputs</h2>

If you won't provide any arguments, script takes default ones:
```python
DEFAULT_ARGS = dict(
    zip_code = 10400,
    dist = 50,
    min_p = 15000,
    max_p = 25000,
    n_ads = 100,
    send_mail = False,
    mb_years = [2019, 2020]
)
```

It is possible to pass arguments from command line:

```powershell
usage: bazos.py [-h] [--zip_code [ZIP_CODE]] [--dist [DIST]] [--min_p [MIN_P]] [--max_p [MAX_P]] [--n_ads [N_ADS]] [--mb_years [MB_YEARS ...]] [--send_mail]

optional arguments:
    -h, --help                  show this help message and exit
    --zip_code [ZIP_CODE]       Zip code - e.g. 10500
    --dist [DIST]               Distance in km from zip code - e.g. 50
    --min_p [MIN_P]             Minimum price in CZK - e.g. 10000
    --max_p [MAX_P]             Maximum price in CZK - e.g. 50000
    --n_ads [N_ADS]             Number of ads to go through - e.g. 100
    --mb_years [MB_YEARS ...]   Wanted years of Macbooks - e.g. 2019 2020
    --send_email                Whether to send an email with results
```
or using the same parameters in uppercase with `BAZOS_` prefix as environment variables (for more convenient docker usage):

```powershell
docker run -v "absolute/path/to/your/directory:/app/data" -e BAZOS_ZIP_CODE=10100 -e BAZOS_DIST=100 -e BAZOS_MIN_P=20000 -e BAZOS_SEND_EMAIL=True
```

Script then takes either:
1. Command line arguments
2. OS environments arguments
3. Default arguments

## Output
* csv file with all ads (data/all.csv)
* csv file with macbooks air (data/airs.csv)
* csv file with macbooks pro (data/pros.csv)
* main method also returns list of pandas dataframes with *all*, *airs* and *pros* 
* possibility to send result tables as html to email via google SMTP server (yagmail)

![Script output preview](/img/output.png "Script output preview")

Example email output:
![Example email preview](/img/mail.png "Example email preview")

## Improve
* better parsing (years & cpu mainly)
* run automatically for all existing pages (not specifying page ranges manually)
* more dynamic filtering of final `airs` and `pros` tables
* return only new entries (difference from previous run)
