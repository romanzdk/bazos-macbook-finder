import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

################################################################################

inputs = dict(
    zip_code = '10400',
    dist = '50',
    min_p = '15000',
    max_p = '25000',
    n_ads = 100,
    send_email = False
)

################################################################################

def make_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')

################################################################################

class RegexOperator():
    def __init__(self, url, text, title):
        self.url = url
        self.text = text
        self.title = title

    def instr(self, to_search:str) -> str:
        if re.search(fr'\b{to_search}\b', self.url) is not None: return True
        if re.search(fr'\b{to_search}\b', self.title) is not None: return True
        if re.search(fr'\b{to_search}\b', self.text) is not None: return False

        return None

    def pro_or_air(self) -> str:
        is_pro = self.instr('macbook pro')
        is_air = self.instr('air')
        
        if (not is_air is None): 
            return 'Air'
        else:
            return 'Pro'
        
        return 'Pro or Air'

    def inor(self, only_numbers=True, *args):
        l = []
        for arg in args:
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
        add_info = pd.read_html(str(self.soup.find_all("table")[1]))[0][[0, 1]].set_index([0]).filter(regex='Vid|Cena', axis=0)
        add_info.columns = [0]
        return pd.DataFrame(add_info[0].apply(lambda x: int(re.sub("\D*", "", str(x))))) # extract numbers only
    
    def __get_attributes__(self) -> pd.DataFrame:
        r = RegexOperator(self.url, self.desc, self.title)

        d = dict(
            date = self.date,
            model = r.pro_or_air(),
            year = r.inor(True, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020),
            ram = r.inor(True, '8', '8gb', '8 gb' '16', '16gb', '16 gb', '32', '32gb', '32 gb'),
            memory = r.inor(True, 128, '128gb', '128 gb',256, '256gb', '256 gb', 512, '512gb', '512 gb', '1tb', '1 tb', '1000 gb', '1000gb'),
            touchbar = r.inor(False, 'touchbar', 'touch bar'),
            m1 = r.instr('m1') is not None,
            cpu = r.get_cpu(),
            url = self.url
        )

        return pd.DataFrame.from_dict(d, orient='index')
    
    def __get_all_attributes__(self) -> pd.DataFrame:
        return self.attributes.append(self.add_info).T
        
################################################################################

def get_args() -> dict:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--zip_code', type=str, nargs='?',
                        help='Zip code - e.g. 10500')
    parser.add_argument('--dist', type=str, nargs='?',
                        help='Distance in km from zip code - e.g. 50')
    parser.add_argument('--min_p', type=str, nargs='?',
                        help='Minimum price in CZK - e.g. 10000')
    parser.add_argument('--max_p', type=str, nargs='?',
                        help='Maximum price in CZK - e.g. 50000')
    parser.add_argument('--n_ads', type=int, nargs='?',
                        help='Number of ads to go through - e.g. 100')
    parser.add_argument('--send_email', action='store_true',
                        help='Whether to send an email with results')

    arg_dict = vars(parser.parse_args())

    for key in arg_dict:
        if arg_dict[key] is None:
            arg_dict[key] = inputs[key]

    return arg_dict

def main(**kwargs) -> list[pd.DataFrame]:
    zip_code = kwargs['zip_code']
    dist = kwargs['dist']
    min_p = kwargs['min_p']
    max_p = kwargs['max_p']
    n_ads = kwargs['n_ads']

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
    macbooks.to_csv('data/all.csv', sep=';')

    airs = macbooks[~(macbooks['model'] == 'Pro') & (~macbooks['year'].isin(['2012', '2012', '2013', '2014', '2015', '2016', '2017', '2018'])) & (macbooks['m1'])] 
    airs.to_csv('data/airs.csv', sep=';')
    print(f'{80*"-"}')
    print("Macbook Air")
    print(airs)
    
    pros = macbooks[~(macbooks['model'] == 'Air') & (~macbooks['year'].isin(['2012', '2012', '2013', '2014', '2015', '2016', '2017', '2018'])) & (~macbooks['memory'].isin(['128']))]
    pros.to_csv('data/pros.csv', sep=';')
    print(f'{80*"-"}')
    print("Macbook Pro")
    print(pros)

    return [airs, pros]

def send_mail(airs:pd.DataFrame, pros:pd.DataFrame) -> None:
    #  convert dataframes to html
    airs = airs.to_html(na_rep='', index=False)
    pros = pros.to_html(na_rep='', index=False)

    # open HTML template and paste tables in it
    with open('mail_template.html', 'r') as f:
        t = f.read()
    filled = t.replace('#tables', airs + '<br/><br/>' + pros).replace("\n","")

    # load SMTP credentials
    # first line = username
    # second line = password
    with open('smtp_creds', 'r') as f:
        creds = f.read().splitlines()

    # send mail
    import yagmail
    try:
        yag = yagmail.SMTP(creds[0], creds[1])
        yag.send(creds[0], 'Macbooks from Bazos', filled)
    except Exception as e:
        print("Failed to send email", str(e))
        raise

################################################################################

if __name__ == '__main__':
    args = get_args()
    r = main(**args)
    if args['send_email']: send_mail(r[0], r[1])