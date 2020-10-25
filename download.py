import requests, re, os, zipfile, csv
import numpy as np
from io import TextIOWrapper
REGIONS = {
    "PHA": "00",
    "STC": "01",
    "JHC": "02",
    "PLK": "03",
    "KVK": "19",
    "ULK": "04",
    "LBK": "18",
    "HKK": "05",
    "PAK": "17",
    "OLK": "14",
    "MSK": "07",
    "JHM": "06",
    "ZLK": "15",
    "VYS": "16",
}

#(tuple:(skratka, nazov), konverzia/typ)
CSV_HEADERS = (
    ("IDENTIFIKAČNÍ ČÍSLO", "string"),
    ("DRUH POZEMNÍ KOMUNIKACE", "int"),
    ("ČÍSLO POZEMNÍ KOMUNIKACE", "int"),
    ("ČASOVÉ ÚDAJE O DOPRAVNÍ NEHODĚ(den, měsíc, rok)", "datetime?"),
    ("WEEKDAY", "int"),
    ("ČAS", "datetime"),
    ("DRUH NEHODY", "int"),
    ("DRUH SRÁŽKY JEDOUCÍCH VOZIDEL", "int"),
    ("DRUH PEVNÉ PŘEKÁŽKY", "int"),
    ("CHARAKTER NEHODY", "int"),
    ("ZAVINĚNÍ NEHODY", "int"),
    ("ALKOHOL U VINÍKA NEHODY PŘÍTOMEN", "int"),
    ("HLAVNÍ PŘÍČINY NEHODY", "int"),
    ("USMRCENO OSOB", "int"),
    ("těžce zraněno osob", "int"),
    ("lehce zraněno osob", "int"),
    ("CELKOVÁ HMOTNÁ ŠKODA", "float"),
    ("DRUH POVRCHU VOZOVKY", "int"),
    ("STAV POVRCHU VOZOVKY V DOBĚ NEHODY", "int"),
    ("STAV KOMUNIKACE", "int"),
    ("POVĚTRNOSTNÍ PODMÍNKY V DOBĚ NEHODY", "int"),
    ("VIDITELNOST", "int"),
    ("ROZHLEDOVÉ POMĚRY", "int"),
    ("DĚLENÍ KOMUNIKACE", "int"),
    ("SITUOVÁNÍ NEHODY NA KOMUNIKACI", "int"),
    ("ŘÍZENÍ PROVOZU V DOBĚ NEHODY", "int"),
    ("MÍSTNÍ ÚPRAVA PŘEDNOSTI V JÍZDĚ", "int"),
    ("SPECIFICKÁ MÍSTA A OBJEKTY V MÍSTĚ NEHODY", "int"),
    ("SMĚROVÉ POMĚRY", "int"),
    ("POČET ZÚČASTNĚNÝCH VOZIDEL", "int"),
    ("MÍSTO DOPRAVNÍ NEHODY", "int"),
    ("DRUH KŘIŽUJÍCÍ KOMUNIKACE", "int"),
    ("DRUH VOZIDLA", "int"),
    ("VÝROBNÍ ZNAČKA MOTOROVÉHO VOZIDLA", "int"),
    ("ROK VÝROBY VOZIDLA", "int"),
    ("CHARAKTERISTIKA VOZIDLA ", "int"),
    ("SMYK", "bool"),
    ("VOZIDLO PO NEHODĚ", "int"),
    ("ÚNIK PROVOZNÍCH, PŘEPRAVOVANÝCH HMOT", "int"),
    ("ZPŮSOB VYPROŠTĚNÍ OSOB Z VOZIDLA", "int"),
    ("SMĚR JÍZDY NEBO POSTAVENÍ VOZIDLA", "int"),
    ("ŠKODA NA VOZIDLE", "int"),
    ("KATEGORIE ŘIDIČE", "int"),
    ("STAV ŘIDIČE", "int"),
    ("VNĚJŠÍ OVLIVNĚNÍ ŘIDIČE", "int"),
    ("", "int"),
    ("", "int"),

)

class DataDownloader:
    
    """@param folder říká, kam se mají dočasná data ukládat. Tato složka nemusí na začátku existovat!
    @param cache_filename jméno souboru ve specifikované složce, které říká, kam se soubor s již zpracovanými daty z funkce ​ get_list​ bude ukládat a odkud
    se budou data brát pro další zpracování a nebylo nutné neustále stahovat data přímo z webu. Složené závorky (formátovací řetězec) bude nahrazený
    tříznakovým kódem (viz tabulka níže) příslušného kraje. Pro jednoduchost podporujte pouze formát “pickle” s kompresí gzip."""
    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pk1.gz"):
        self.url = url
        self.folder = folder
        if (not os.path.exists(self.folder)):
            os.mkdir(self.folder)
        self.cache_filename = cache_filename

    """funkce stáhne do datové složky ​ folder​ všechny soubory s daty z adresy ​ url​ ."""
    def download_data(self):
        cookies = {
            '_ranaCid': '894571194.1567851474',
            '_ga': 'GA1.2.727971800.1567851474',
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://ehw.fit.vutbr.cz/izv/',
            'Upgrade-Insecure-Requests': '1',
        }
        html = requests.get(self.url, headers=headers, cookies=cookies)
        ziplist = re.findall("data/[a-zA-Z0-9\-]*\.zip", str(html.content))
        for file_name in ziplist:
            response = requests.get(self.url+file_name, headers=headers, cookies=cookies)
            with open("{}/".format(self.folder)+file_name[5:], 'wb') as fd:
                for chunk in response.iter_content():
                    fd.write(chunk)
        

    """pokud nejsou data pro daný kraj stažená, stáhne je do datové složky ​ folder​ . Poté
    je pro daný region specifikovaný tříznakovým kódem (viz tabulka níže) ​ vždy
    vyparsuje do následujícího formátu tuple(list[str], list[np.ndarray])"""
    def parse_region_data(self, region):
        if (not os.path.lexists("{}/datagis2016.zip".format(self.folder))):
            self.download_data()
        zf = zipfile.ZipFile("{}/datagis2016.zip".format(self.folder))
        #fd = zf.open("{}.csv".format(REGIONS[region]))
        names = list()
        for tup in CSV_HEADERS:
            names.append(tup[0])
        csvfile = zf.open('{}.csv'.format(REGIONS[region]), "r")
        reader = csv.reader(TextIOWrapper(csvfile, encoding='unicode_escape'), delimiter=';', quotechar='"')
        #for row in reader:
        #    print(row)


    
    def get_list(self, regions=None):
        pass

dd = DataDownloader()
#dd.download_data()
dd.parse_region_data("KVK")