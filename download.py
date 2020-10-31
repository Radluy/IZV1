import requests, re, os, zipfile, csv, pickle, gzip
import numpy as np
from io import TextIOWrapper
#region abbrevations and their corresponding numbers
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

#list(tuple:(column name, numpy datatype of values))
CSV_HEADERS = (
    ("IDENTIFIKAČNÍ ČÍSLO", "S"),
    ("DRUH POZEMNÍ KOMUNIKACE", "i2"),
    ("ČÍSLO POZEMNÍ KOMUNIKACE", "i4"),
    ("ČASOVÉ ÚDAJE O DOPRAVNÍ NEHODĚ(den, měsíc, rok)", "M"),
    ("WEEKDAY", "i2"),
    ("ČAS", "S"),
    ("DRUH NEHODY", "i2"),
    ("DRUH SRÁŽKY JEDOUCÍCH VOZIDEL", "i2"),
    ("DRUH PEVNÉ PŘEKÁŽKY", "i2"),
    ("CHARAKTER NEHODY", "i4"),
    ("ZAVINĚNÍ NEHODY", "i2"),
    ("ALKOHOL U VINÍKA NEHODY PŘÍTOMEN", "i2"),
    ("HLAVNÍ PŘÍČINY NEHODY", "i4"),
    ("USMRCENO OSOB", "i2"),
    ("těžce zraněno osob", "i2"),
    ("lehce zraněno osob", "i2"),
    ("CELKOVÁ HMOTNÁ ŠKODA", "f"),
    ("DRUH POVRCHU VOZOVKY", "i2"),
    ("STAV POVRCHU VOZOVKY V DOBĚ NEHODY", "i2"),
    ("STAV KOMUNIKACE", "i2"),
    ("POVĚTRNOSTNÍ PODMÍNKY V DOBĚ NEHODY", "i2"),
    ("VIDITELNOST", "i2"),
    ("ROZHLEDOVÉ POMĚRY", "i2"),
    ("DĚLENÍ KOMUNIKACE", "i4"),
    ("SITUOVÁNÍ NEHODY NA KOMUNIKACI", "i4"),
    ("ŘÍZENÍ PROVOZU V DOBĚ NEHODY", "i2"),
    ("MÍSTNÍ ÚPRAVA PŘEDNOSTI V JÍZDĚ", "i2"),
    ("SPECIFICKÁ MÍSTA A OBJEKTY V MÍSTĚ NEHODY", "i4"),
    ("SMĚROVÉ POMĚRY", "i4"),
    ("POČET ZÚČASTNĚNÝCH VOZIDEL", "i2"),
    ("MÍSTO DOPRAVNÍ NEHODY", "i4"),
    ("DRUH KŘIŽUJÍCÍ KOMUNIKACE", "i4"),
    ("DRUH VOZIDLA", "i"),
    ("VÝROBNÍ ZNAČKA MOTOROVÉHO VOZIDLA", "i"),
    ("ROK VÝROBY VOZIDLA", "i"),
    ("CHARAKTERISTIKA VOZIDLA ", "i4"),
    ("SMYK", "i4"),
    ("VOZIDLO PO NEHODĚ", "i4"),
    ("ÚNIK PROVOZNÍCH, PŘEPRAVOVANÝCH HMOT", "i4"),
    ("ZPŮSOB VYPROŠTĚNÍ OSOB Z VOZIDLA", "i2"),
    ("SMĚR JÍZDY NEBO POSTAVENÍ VOZIDLA", "i2"),
    ("ŠKODA NA VOZIDLE", "i"),
    ("KATEGORIE ŘIDIČE", "i2"),
    ("STAV ŘIDIČE", "i2"),
    ("VNĚJŠÍ OVLIVNĚNÍ ŘIDIČE", "i2"),
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

#file names 
files = ("datagis2016.zip", "datagis-rok-2017.zip", "datagis-rok-2018.zip", "datagis-rok-2019.zip", "datagis-09-2020.zip")

#class responsible for downloading and parsing accidents data
class DataDownloader:
    """Initializes class instance
    @param url url of website containing datafiles
    @param folder folder where data files and cache files will be stored
    @param cache_filename name format for cache files"""
    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pk1.gz"):
        self.url = url
        self.folder = folder
        if (not os.path.exists(self.folder)):
            os.mkdir(self.folder)
        self.cache_filename = cache_filename
        self.data_attr = {} #attribute that stores all data if they were processed already, dict{region: data}
        reg_keys = REGIONS.keys()
        for region in reg_keys:
            self.data_attr[region] = None

    """Finds and downloads all zip files found on specified url"""
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
        
    """Parses csv file of one region into final data structure: tuple(list[column names], list[numpy arr of values])
    @param region region abbrevation according to global REGIONS dict
    @return returns final data structure tuple(list[column names], list[numpy arr of values])"""
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
    
    """Parses csv files for each region specified in list passed to function and merges data into one data structure
    @param regions list of regions abbrevations, if None is specified all regions are processed
    @return return tuple(list[column names], list[numpy arr of values]) containing all regions queried"""
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

        #process region by region
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

            #concatenate into final numpy arrays
            i = 0
            for arr in iter_list[1]:
                data[i] = np.concatenate((data[i], arr))
                i += 1

        return result

            
        
#EXAMPLE
if (__name__ == "__main__"):
    dd = DataDownloader()
    res = dd.get_list(("STC", "HKK", "JHM"))
    print(", ".join(res[0]))
    print("number of accidents= {}".format(res[1][1].size))
    print("Regions= Stredocesky, Kralovehradecky, Jihomoravsky")