# Importa as opções do Firefox
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
import json
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# utilizando webdriver no linux
"""
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
service = ChromeService(executable_path=ChromeDriverManager().install())
f = webdriver.Chrome(service=service)
"""

# url da página inicial da academia das apostas
academia = "https://www.academiadasapostasbrasil.com"
# abrindo o Navegador e Request
service = Service(executable_path=ChromeDriverManager().install())
f = webdriver.Chrome(service=service)
f.get(academia)
wdw = WebDriverWait(f, 30, poll_frequency=1)

def dia_inicial(numero_de_clicks): 
    """
    faz o click para selecionar em qual dia quero iniciar
    """
    next_btn = f.find_element(By.XPATH, '//div[@class= "widget-double-container-left mb-content"]//span[contains(@class, "date-increment")]')
    for i in range(int(numero_de_clicks)):
        next_btn.click()     

qt_analises_page = 1 # variavel contador q ajuda o soup criar o dict (deve estar fora da def mesmo)
def prox_urls(): 
    """
    Faz o click para listar os próximos jogos && tem um contador
    """
 
    global qt_analises_page
    next_btn = f.find_element(By.XPATH, '//div[@class= "widget-double-container-left mb-content"]//span[contains(@class, "date-increment")]')
    
    qt_analises_page += 1
    next_btn.click()            
    
def wait_expansao():
    """
    vai retornar TRUE até expandir tudo, ou seja enquanto houver jogos ocultos continua TRUE
    """
    try:
        btn_exp = f.find_element(By.XPATH, '//td[contains(@class, "footer")]')
    except:
        sleep(1)
        print('WARN: btn de expandir não existe mais')
        btn_exp = False
    
    return (True if bool(btn_exp) else False)
    
def click_expansao(): 
    """
     função responsável pela expansão de todos os jogos
    """
    try:
        sleep(1)
        if wait_expansao():
            btn_exp = f.find_element(By.XPATH, '//td[contains(@class, "footer")]')
            btn_exp.click()
            wdw.until_not(wait_expansao, "erro na def soup")     
    except:
        sleep(1)
        print('WARN: verificando se ainda tem btn_expandir para refazer o click')
        if wait_expansao():
            click_expansao()

urls = {} # vai guardar as urls

# lista de campeonatos que trabalho
campeonatos = [
        # Ligas
        'alemanha/bundesliga', 'alemanha/2-liga', 'dfb-pokal', 'alemanha/super-cup',
        'brasileirao-serie-a', 'copa-do-brasil/', 'brasil/serie-b', 
        'la-liga', 'liga-adelante', 
        'serie-a-tim', 'coppa-italia',
        'inglaterra/super-copa', 'inglaterra/premier-league', 
        'franca/ligue-1', 
        '/eredivisie', 'eerste-divisie',
        'primeira-liga', 
        'suica/super-liga', # suiça
        'tippeligaen',
        'major-league-soccer',
        'super-liga-turca',
        # Continentais
        'copa-libertadores-da-america', 'copa-bridgestone-sul-americana',
        'liga-dos-campeoes-da-uefa', 'europa-conference-league', 'liga-europa',
    # submundo q eu gosto
        'superliga-argentina', 'copa-argentina', # 'austria/bundesliga', 
        'belgica/1e-klasse'
]

def soup():
    """
        cria objeto BS4;
        cria JSONs para cada dia, Ex: [ {hoje:[url, url]}, {17/07/20: [url, url]} ]
    """
    try:
        # tabela de jogos
        table_games = f.find_element(
            By.XPATH, 
            '//div[@class="widget-double livescores large"]').get_attribute(
                'outerHTML'
                )
        soup = BeautifulSoup(table_games, 'html.parser') # criando soup
        date = soup.find('label').attrs['data-displaydate'] # data
        href = soup.find_all('td', class_='score') # todas partidas
        urls[f'dia{qt_analises_page}'] = []
        # preciso pegar a referencia da data p
        for link in href:
            link = link.find('a').attrs['href']
            for c in campeonatos:
                if c in link:
                    urls[f'dia{qt_analises_page}'].append(link)
        print(f'DIA: {date} - Jogos adicionados: {len(urls[f"dia{qt_analises_page}"])}')
    except:
        print('soup error')

def gerar_json():
    with open('urls.json', 'w', encoding='utf-8') as jp:
        # criando arquivo JSON
        # json só faz dump ou load 
        # (o primeiro converte o obj em str, enquanto o load faz o oposto)
        jayzon = json.dumps(urls, indent=4)
        jp.write(jayzon)
    print('JSON gerado!')

# processoo de execução...
d = input('qual dia começar, digite o valor numérico: \n 0 - hoje \n 1 - amanha \n 2 - dps de amanhã \n n - n dia \n\n digite: ')
dia_inicial(d)
x = input('quantos dias analisar (considerando o dia atual): ')
x = int(x)
try:
    for i in range(x): # vai analisar quantos dias o usuario quiser
        print(f'iniciando {i+1}')
        if i > 0:
            prox_urls()
        wait_expansao()
        click_expansao()
        soup()
    print(f'Qt de dias analisados: {qt_analises_page}')
    gerar_json()
    f.quit()
except:
    print('FATAL ERROR!!!!')