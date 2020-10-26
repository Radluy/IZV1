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

#(tuple:(nazov, konverzia/typ))
CSV_HEADERS = (
    ("IDENTIFIKAČNÍ ČÍSLO", "S"),
    ("DRUH POZEMNÍ KOMUNIKACE", "i"),
    ("ČÍSLO POZEMNÍ KOMUNIKACE", "i"),
    ("ČASOVÉ ÚDAJE O DOPRAVNÍ NEHODĚ(den, měsíc, rok)", "M"),
    ("WEEKDAY", "i"),
    ("ČAS", "M"),
    ("DRUH NEHODY", "i"),
    ("DRUH SRÁŽKY JEDOUCÍCH VOZIDEL", "i"),
    ("DRUH PEVNÉ PŘEKÁŽKY", "i"),
    ("CHARAKTER NEHODY", "i"),
    ("ZAVINĚNÍ NEHODY", "i"),
    ("ALKOHOL U VINÍKA NEHODY PŘÍTOMEN", "i"),
    ("HLAVNÍ PŘÍČINY NEHODY", "i"),
    ("USMRCENO OSOB", "i"),
    ("těžce zraněno osob", "i"),
    ("lehce zraněno osob", "i"),
    ("CELKOVÁ HMOTNÁ ŠKODA", "f"),
    ("DRUH POVRCHU VOZOVKY", "i"),
    ("STAV POVRCHU VOZOVKY V DOBĚ NEHODY", "i"),
    ("STAV KOMUNIKACE", "i"),
    ("POVĚTRNOSTNÍ PODMÍNKY V DOBĚ NEHODY", "i"),
    ("VIDITELNOST", "i"),
    ("ROZHLEDOVÉ POMĚRY", "i"),
    ("DĚLENÍ KOMUNIKACE", "i"),
    ("SITUOVÁNÍ NEHODY NA KOMUNIKACI", "i"),
    ("ŘÍZENÍ PROVOZU V DOBĚ NEHODY", "i"),
    ("MÍSTNÍ ÚPRAVA PŘEDNOSTI V JÍZDĚ", "i"),
    ("SPECIFICKÁ MÍSTA A OBJEKTY V MÍSTĚ NEHODY", "i"),
    ("SMĚROVÉ POMĚRY", "i"),
    ("POČET ZÚČASTNĚNÝCH VOZIDEL", "i"),
    ("MÍSTO DOPRAVNÍ NEHODY", "i"),
    ("DRUH KŘIŽUJÍCÍ KOMUNIKACE", "i"),
    ("DRUH VOZIDLA", "i"),
    ("VÝROBNÍ ZNAČKA MOTOROVÉHO VOZIDLA", "i"),
    ("ROK VÝROBY VOZIDLA", "i"),
    ("CHARAKTERISTIKA VOZIDLA ", "i"),
    ("SMYK", "i"),
    ("VOZIDLO PO NEHODĚ", "i"),
    ("ÚNIK PROVOZNÍCH, PŘEPRAVOVANÝCH HMOT", "i"),
    ("ZPŮSOB VYPROŠTĚNÍ OSOB Z VOZIDLA", "i"),
    ("SMĚR JÍZDY NEBO POSTAVENÍ VOZIDLA", "i"),
    ("ŠKODA NA VOZIDLE", "i"),
    ("KATEGORIE ŘIDIČE", "i"),
    ("STAV ŘIDIČE", "i"),
    ("VNĚJŠÍ OVLIVNĚNÍ ŘIDIČE", "i"),
    ("a", "S"),
    ("b", "S"),
    ("d", "S"),#float ciarka to bodka
    ("e", "S"),#float ciarka to bodka
    ("f", "S"),
    ("g", "S"),
    ("h", "S"),
    ("i", "S"),
    ("j", "S"),
    ("k", "S"),
    ("l", "S"),
    ("n", "S"),
    ("o", "S"),
    ("p", "S"),
    ("q", "S"),
    ("r", "S"),
    ("s", "S"),
    ("t", "S"),
    ("LOKALITA NEHODY", "i"),
    ("REGION", "S")

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
        #initialize data structures
        names = list()
        data = list()
        tmp_list = list()
        for tup in CSV_HEADERS:
            names.append(tup[0])
            tmp_list.append(list())

        #open csv file for reading
        if (not os.path.lexists("{}/datagis2016.zip".format(self.folder))):
            self.download_data()
        zf = zipfile.ZipFile("{}/datagis2016.zip".format(self.folder))
        csvfile = zf.open('{}.csv'.format(REGIONS[region]), "r")
        reader = csv.reader(TextIOWrapper(csvfile, encoding='unicode_escape'), delimiter=';', quotechar='"')

        #parse csv strings
        for row in reader:
            i = 0
            string_list = list(row)
            for obj in string_list:
                if (obj == "" or obj == "XX"):
                    obj = "-1"
                tmp_list[i].append(obj.encode("UTF-8"))
                i += 1

        #close open files
        csvfile.close()
        zipfile.ZipFile.close(zf)

        #convert to numpy array
        i = 0
        for particle in tmp_list: 
            data.append(np.array(particle, dtype=CSV_HEADERS[i][1]))
            i += 1
        print("finished!")
        result = (names, data)
        return result




    
    def get_list(self, regions=None):
        pass

dd = DataDownloader()
#dd.download_data()
dd.parse_region_data("KVK")