import requests, re, os, zipfile, csv, pickle, gzip
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
    ("ČAS", "S"),
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

files = ("datagis2016.zip", "datagis-rok-2017.zip", "datagis-rok-2018.zip", "datagis-rok-2019.zip", "datagis-09-2020.zip")

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
        self.data_attr = {}
        reg_keys = REGIONS.keys()
        for region in reg_keys:
            self.data_attr[region] = None

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
        for file in files:
            if (not os.path.lexists(os.path.join(self.folder, file))):
                self.download_data()
            zf = zipfile.ZipFile(os.path.join(self.folder, file))
            csvfile = zf.open('{}.csv'.format(REGIONS[region]), "r")
            reader = csv.reader(TextIOWrapper(csvfile, encoding='unicode_escape'), delimiter=';', quotechar='"')

            #parse csv strings
            for row in reader:
                i = 0
                string_list = list(row)
                for obj in string_list:
                    if (obj == "" or obj == "XX" or obj == "D:" or obj == "E:" or obj == "F:" or obj == "G:"):
                        obj = "-1"
                    if (CSV_HEADERS[i][1] == 'f'):
                        obj = str(obj).replace(',', '.')
                    tmp_list[i].append(obj.encode("UTF-8"))
                    i += 1
                tmp_list[i].append(region)

            #close open files
            csvfile.close()
            zipfile.ZipFile.close(zf)

        #convert to numpy array
        i = 0
        for particle in tmp_list: 
            data.append(np.array(particle, dtype=CSV_HEADERS[i][1]))
            i += 1

        #final tuple
        result = (names, data)
        return result
    
    """Vrací zpracovaná data pro vybrané kraje (regiony). Argument ​ regions ​ specifikuje
    seznam (list) požadovaných krajů jejich třípísmennými kódy. Pokud seznam není
    uveden (je použito None), zpracují se všechny kraje včetně Prahy."""
    def get_list(self, regions=None):
        if (regions == None):
            regions = REGIONS.keys()

        #init
        names = list()
        data = list()
        i = 0
        for tup in CSV_HEADERS:
            names.append(tup[0])
            data.append(np.empty(0, dtype=CSV_HEADERS[i][1]))
            i += 1
        result = (names, data)
        iter_list = None

        for region in regions:
            #already loaded in attribute
            if (self.data_attr[region] != None):  
                iter_list = self.data_attr[region][1]
            #load from cache
            elif (os.path.exists(os.path.join(self.folder, self.cache_filename.format(region)))): 
                fd = gzip.open(os.path.join(self.folder, self.cache_filename.format(region)), "r")
                iter_list = pickle.load(fd)
                self.data_attr[region] = iter_list
            #parse from csv file
            else: 
                iter_list = self.parse_region_data(region)
                fd = gzip.open(os.path.join(self.folder, self.cache_filename.format(region)), "w")
                pickle.dump(iter_list, fd)
                fd.close()
                self.data_attr[region] = iter_list

            i = 0
            for arr in iter_list[1]:
                data[i] = np.concatenate((data[i], arr))
                i += 1
        print("FINISHED!")
        return result

            
        
#EXAMPLE
if (__name__ == "__main__"):
    dd = DataDownloader()
    res = dd.get_list(("STC", "HKK", "JHM"))
    print(", ".join(res[0]))
    print("number of accidents= {}".format(res[1][1].size))
    print("Regions= Stredocesky, Kralovehradecky, Jihomoravsky")