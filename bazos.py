import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

################################################################################

ZIP_CODE = '10400'
DISTANCE = '50'
MIN_PRICE = '15000'
MAX_PRICE = '25000'

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

def main(zip=ZIP_CODE, dist=DISTANCE, min_p=MIN_PRICE, max_p=MAX_PRICE, ads=100):
    base_url = f'https://bazos.cz/search.php?hledat=macbook&rubriky=www&hlokalita={ZIP_CODE}&humkreis={DISTANCE}&cenaod={MIN_PRICE}&cenado={MAX_PRICE}&Submit=Hledat&kitx=ano&order=&crz='
    macbooks = pd.DataFrame()

    for i in range(0, ads, 20):
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

################################################################################

if __name__ == '__main__':
    main()