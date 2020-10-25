import requests, re, os

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
            with open("data/{}".format(file_name[5:]), 'wb') as fd:
                for chunk in response.iter_content():
                    fd.write(chunk)
        

    """pokud nejsou data pro daný kraj stažená, stáhne je do datové složky ​ folder​ . Poté
    je pro daný region specifikovaný tříznakovým kódem (viz tabulka níže) ​ vždy
    vyparsuje do následujícího formátu tuple(list[str], list[np.ndarray])"""
    def parse_region_data(self, region):
        pass

    
    def get_list(self, regions=None):
        pass

dd = DataDownloader()
dd.download_data()