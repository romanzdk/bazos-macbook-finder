import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

################################################################################

DEFAULT_ARGS = dict(
    zip_code = 10400,
    dist = 50,
    min_p = 15000,
    max_p = 25000,
    n_ads = 100,
    send_mail = False,
    mb_years = [2019, 2020]
)

BASE_YEARS = [i for i in range(2010,2022)]

try:
    CURR_DIR = os.path.dirname(os.path.realpath(__file__))
except:
    CURR_DIR = os.getcwd() # if run from jupyter notebook

################################################################################

def make_soup(url:str) -> BeautifulSoup:
    """
    Creates Beautiful Soup from given url

    Args:
        url (str): url to make soup from

    Returns:
        BeautifulSoup: soup from given url
    """
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')

################################################################################

class RegexOperator():
    def __init__(self, url, text, title):
        self.url = url
        self.text = text
        self.title = title

    def instr(self, to_search:str) -> bool:
        """
        Finds passed string in the ad

        Args:
            to_search (str): string to search for

        Returns:
            bool: True if found in header, False if found in description, None 
                  if not found
        """
        if re.search(fr'\b{to_search}\b', self.url) is not None: return True
        if re.search(fr'\b{to_search}\b', self.title) is not None: return True
        if re.search(fr'\b{to_search}\b', self.text) is not None: return False

        return None

    def pro_or_air(self) -> str:
        """
        Determines whether the ad is for Macbook Air or Pro

        Returns:
            str: 'Air', 'Pro' or 'Pro or Air' if not sure 
        """
        is_pro = self.instr('macbook pro')
        is_air = self.instr('air')
        
        if (not is_air is None): 
            return 'Air'
        else:
            return 'Pro'
        
        return 'Pro or Air'

    def inor(self, only_numbers=True, *args):
        """
        Finds multiple arguments in the ad

        Returns:
            [str]/[set]/[None]: returns single string if only one value found
                                set of multiple values or None if nothing found
        """
        l = []
        for arg in args[0]:
            if self.instr(arg) == True: # present in the title
                if only_numbers:
                    return re.sub('\D*', "", str(arg))
                else:
                    return arg
            elif self.instr(arg) == False: # present in the text
                if only_numbers:
                    l.append(re.sub('\D*', "", str(arg)))
                else:
                    l.append(arg)

        if len(set(l)) == 1: return l[0]
        if len(l) == 0: return None
        return set(l)
    
    def get_cpu(self):
        """
        Gets CPU frequency

        Returns:
            [str]/[set]/[None]: returns single string if only one value found
                                set of multiple values or None if nothing found
        """
        cpus = []
        ghzs = re.findall(r'\b\d[\.,]\d', self.text)

        for g in ghzs:
            converted = float(g.replace(",", "."))
            if converted <= 4. and converted >= 1.:
                cpus.append(converted)

        if len(cpus) == 1: return cpus[0]
        if len(cpus) == 0: return None
        return set(cpus)

################################################################################

class Macbook():
    def __init__(self, url:str):
        self.url = url
        self.soup = make_soup(url)
        self.title = self.soup.find_all('div', {'class':'inzeratydetnadpis'})[0].text
        self.date = re.findall(r"\[(.*)\]", self.title)[0]
        self.desc = self.soup.find_all("div", {"class": "popisdetail"})[0].text.lower()
        self.add_info = self.__get_additional_info__()
        self.attributes = self.__get_attributes__()
        self.all_info = self.__get_all_attributes__()

    def __get_additional_info__(self) -> pd.DataFrame:
        """
        Gets additional information from the bottom of the ad

        Returns:
            pd.DataFrame: pandas DataFrame with additional information
                          filtered only for number of views and price
        """
        add_info = pd.read_html(str(self.soup.find_all("table")[1]))[0][[0, 1]].set_index([0]).filter(regex='Vid|Cena', axis=0)
        add_info.columns = [0]
        return pd.DataFrame(add_info[0].apply(lambda x: int(re.sub("\D*", "", str(x))))) # extract numbers only
    
    def __get_attributes__(self) -> pd.DataFrame:
        """
        Parses number of selected Macbook attributes from the ad description

        Returns:
            pd.DataFrame: pandas DataFrame with parsed attributes
        """
        r = RegexOperator(self.url, self.desc, self.title)

        d = dict(
            date = self.date,
            model = r.pro_or_air(),
            year = r.inor(True, BASE_YEARS),
            ram = r.inor(True, ['8', '8gb', '8 gb' '16', '16gb', '16 gb', '32', '32gb', '32 gb']),
            memory = r.inor(True, [128, '128gb', '128 gb',256, '256gb', '256 gb', 512, '512gb', '512 gb', '1tb', '1 tb', '1000 gb', '1000gb']),
            touchbar = r.inor(False, ['touchbar', 'touch bar']),
            m1 = r.instr('m1') is not None,
            cpu = r.get_cpu(),
            url = self.url
        )

        return pd.DataFrame.from_dict(d, orient='index')
    
    def __get_all_attributes__(self) -> pd.DataFrame:
        """
        Merges attributes from description with additional information
        """
        return self.attributes.append(self.add_info).T
        
################################################################################

def get_env_args() -> dict:
    """
    Returns dict of arguments from OS environment
    """
    env_args = dict.fromkeys(DEFAULT_ARGS.keys())

    for k in env_args:
        env_args[k] = os.environ.get('BAZOS_' + k.upper())

    return env_args

def get_cmd_args() -> dict:
    """
    Returns dict of arguments from command line
    """
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--zip_code', type=int, nargs='?',
                        help='Zip code - e.g. 10500')
    parser.add_argument('--dist', type=int, nargs='?',
                        help='Distance in km from zip code - e.g. 50')
    parser.add_argument('--min_p', type=int, nargs='?',
                        help='Minimum price in CZK - e.g. 10000')
    parser.add_argument('--max_p', type=int, nargs='?',
                        help='Maximum price in CZK - e.g. 50000')
    parser.add_argument('--n_ads', type=int, nargs='?',
                        help='Number of ads to go through - e.g. 100')
    parser.add_argument('--mb_years', type=int, nargs='*',
                        help='Wanted years of Macbooks')
    parser.add_argument('--send_mail', action='store_true',
                        help='Whether to send an email with results')
    
    return vars(parser.parse_args())

def get_final_args(env_args:dict, cmd_args:dict) -> dict:
    """
    Returns Coalesce of command line, OS environment and default arguments

    Args:
        env_args (dict): arguments from OS environment
        cmd_args (dict): arguments from command line

    Returns:
        dict: Coalesce of command line, OS environment and default arguments
    """
    result_args = dict.fromkeys(DEFAULT_ARGS)

    for key in result_args:
        result_args[key] = cmd_args[key] or env_args[key] or DEFAULT_ARGS[key]
    
    print(f"Running with following parameters: \n {result_args}")
    print(f'{80*"-"}')
    
    return result_args

################################################################################

def send_mail(airs:pd.DataFrame, pros:pd.DataFrame) -> None:
    """
    Sends an email with result tables for Macbooks Air and Macbooks pro to 
    specified email in <smtp-creds> file which should be placed in the root
    folder of the app. First line should contain email and second app password.
    Supports only GMail.

    Args:
        airs (pd.DataFrame): DataFrame with Macbooks Air
        pros (pd.DataFrame): DataFrame with Macbooks Pro
    """
    #  convert dataframes to html
    airs = airs.to_html(na_rep='', index=False)
    pros = pros.to_html(na_rep='', index=False)

    # open HTML template and paste tables in it
    with open(CURR_DIR + '/mail_template.html', 'r') as f:
        t = f.read()
    filled = t.replace('#tables', airs + '<br/><br/>' + pros).replace("\n","")

    # load SMTP credentials
    # first line = username
    # second line = password
    with open(CURR_DIR + '/smtp_creds', 'r') as f:
        creds = f.read().splitlines()

    # send mail
    import yagmail
    try:
        yag = yagmail.SMTP(creds[0], creds[1])
        yag.send(creds[0], 'Macbooks from Bazos', filled)
        print("Email successfully sent")
    except Exception as e:
        print("Failed to send email", str(e))
        raise

def main(**kwargs) -> list[pd.DataFrame]:
    """
    Runs main task 
    - scrape Bazos for Macbooks, 
    - create & save DataFrames for Airs and Pros,
    - send email with result DataFrames

    Returns:
        list[pd.DataFrame]: list of result dataframes - all, airs, pros
    """
    zip_code = str(kwargs['zip_code'])
    dist = str(kwargs['dist'])
    min_p = str(kwargs['min_p'])
    max_p = str(kwargs['max_p'])
    n_ads = int(kwargs['n_ads'])
    send_mail_var = True if str(kwargs['send_mail']) == 'True' else False # because of the environment variables treated as strings
    mb_years = kwargs['mb_years']

    base_url = f'https://bazos.cz/search.php?hledat=macbook&rubriky=www&hlokalita={zip_code}&humkreis={dist}&cenaod={min_p}&cenado={max_p}&Submit=Hledat&kitx=ano&order=&crz='
    macbooks = pd.DataFrame()

    for i in range(0, n_ads, 20):
        url = base_url + str(i)
        print(url)
        
        soup = make_soup(url)
        ads = soup.find_all("div", {"class":"inzeraty"})

        for ad in ads:
            href = str(ad.find_all("div", {"class":"inzeratynadpis"})[0].find("a"))
            ad_url = re.findall(r'''<a href=(["'])(.*?)\1''', href)[0][1]
            mb = Macbook(ad_url)
            macbooks = macbooks.append(mb.all_info)

    macbooks = macbooks.sort_values('Cena:', ascending=True)
    macbooks.to_csv(CURR_DIR +'/data/all.csv', sep=';')

    # Macbooks Air
    airs = macbooks[~(macbooks['model'] == 'Pro') & (~macbooks['year'].isin(list(set(BASE_YEARS) - set(mb_years)))) & (macbooks['m1'])] 
    airs.to_csv(CURR_DIR +'/data/airs.csv', sep=';')
    print(f'{80*"-"}')
    print(len(airs), "Macbooks Air found")
    
    # Macbooks Pro
    pros = macbooks[~(macbooks['model'] == 'Air') & (~macbooks['year'].isin(list(set(BASE_YEARS) - set(mb_years))))]
    pros.to_csv(CURR_DIR + '/data/pros.csv', sep=';')
    print(len(pros), "Macbooks Pro found")
    print(f'{80*"-"}')

    if send_mail_var: send_mail(airs, pros)

    return [macbooks, airs, pros]

################################################################################

if __name__ == '__main__':
    print(f'{80*"-"}')
    args = get_final_args(env_args=get_env_args(), cmd_args=get_cmd_args())
    main(**args)
    print()
