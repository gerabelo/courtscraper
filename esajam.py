'''
e-SAJ TJAM Scraper be geraldo.rabelo@gmail.com (Ago/2019)

\python esajam.py username password processos.txt

0606426-45.2019.8.04.0092
    0606426-45.2019 Processo
    8.04            Junta
    0092            Foro
'''

import time, argparse, urllib.parse, re

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from fake_useragent import UserAgent
from time import sleep
from pymongo import MongoClient

def lreplace(pattern, sub, string):
    return re.sub('^%s' % pattern, sub, string)

def rreplace(pattern, sub, string):
    return re.sub('%s$' % pattern, sub, string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='e-SAJ TJAM Scraper be geraldo.rabelo@gmail.com (Ago/2019)')
    parser.add_argument('user', help='Login')
    parser.add_argument('password', help='Senha')
    parser.add_argument('processos', help='Lista de processos em arquivo')
    # parser.add_argument('processo', help='Número do processo')
    # parser.add_argument('foro', help='Número do foro unificado')
    
    args = parser.parse_args()

    client = MongoClient("mongodb://localhost:27017")
    db = client['esaj']
    collection = db['processos']


    # url = "https://cna.oab.org.br/"
    # url = "https://consultasaj.tjam.jus.br/cpopg/show.do?"
    url_consulta = "https://consultasaj.tjam.jus.br/cpopg/open.do?mobile=N&gateway=true"
    url_login = "https://consultasaj.tjam.jus.br/sajcas/login?service=https%3A%2F%2Fconsultasaj.tjam.jus.br%2Fesaj%2Fj_spring_cas_security_check"
    chrome_driver = "C:\\chromedriver_win32\\chromedriver.exe"        
    options = webdriver.ChromeOptions()
    # ua = UserAgent()
    # userAgent = ua.random
    # options.add_argument(f'user-agent={userAgent}')
    # print(userAgent)
    options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36")
    driver = webdriver.Chrome(chrome_driver, chrome_options=options)  # Optional argument, if not specified will search path.
    driver.get(url_login)
    
    usernameForm = driver.find_element_by_id("usernameForm")
    usernameForm.send_keys(args.user+Keys.TAB+args.password+Keys.TAB+Keys.TAB+Keys.ENTER)

    with open(args.processos,"r") as processos_file:
        processos = processos_file.readlines()
        for processo in processos:
            try:
                atomos = processo.split('.')
                processo = atomos[0]+'.'+atomos[1]
                junta = atomos[2]+'.'+atomos[3]
                foro = atomos[4]
                driver.get(url_consulta)
                sleep(5)
                numeroDigitoAnoUnificado = driver.find_element_by_id("numeroDigitoAnoUnificado")
                numeroDigitoAnoUnificado.send_keys(processo)
                numeroDigitoAnoUnificado.send_keys(Keys.TAB+"0092")
                numeroDigitoAnoUnificado.send_keys(Keys.TAB+Keys.TAB+Keys.TAB+Keys.TAB+" ")

                dataMovimentacao = driver.find_elements_by_class_name("dataMovimentacao")
                descricaoMovimentacao = driver.find_elements_by_class_name("descricaoMovimentacao") 
                classeProcesso = driver.find_element_by_id("classeProcesso") 
                assuntoProcesso = driver.find_element_by_id("assuntoProcesso") 
                foroProcesso = driver.find_element_by_id("foroProcesso") 
                varaProcesso = driver.find_element_by_id("varaProcesso") 
                juizProcesso = driver.find_element_by_id("juizProcesso") 
                # print(dataMovimentacao[0].get_attribute("innerText"),' ',descricaoMovimentacao[0].get_attribute("innerText"))

                print(f'Processo: {processo}')
                print('Classe: ',classeProcesso.get_attribute("innerText"))
                print('Assunto: ',assuntoProcesso.get_attribute("innerText"))
                # print('Foro: ',foroProcesso.get_attribute("innerText"))
                print(f'Foro: {foro}')
                print('Vara: ',varaProcesso.get_attribute("innerText"))
                print('Juiz: ',juizProcesso.get_attribute("innerText"))

                movimentacao = [[],[]]
                for i,j in zip(dataMovimentacao,descricaoMovimentacao):
                    data = i.get_attribute("innerText").replace('\n','').replace('\t','').replace('  ',' ')
                    data = lreplace(' ','',data)
                    data = rreplace(' ','',data)
                    desc = j.get_attribute("innerText").replace('\n','').replace('\t','').replace('  ',' ')
                    desc = lreplace(' ','',desc)
                    desc = rreplace(' ','',desc)
                    print(f'{data} {desc}')
                    movimentacao[0].append(data)
                    movimentacao[1].append(desc)
                try:
                    collection.update_one(
                        {"processo":processo},
                        {'$set':
                            {
                                "processo":processo,
                                "junta":junta,
                                "classe":classeProcesso.get_attribute("innerText"),
                                "assunto":assuntoProcesso.get_attribute("innerText"),
                                "foro":foroProcesso.get_attribute("innerText"),
                                "vara":varaProcesso.get_attribute("innerText"),
                                "juiz":juizProcesso.get_attribute("innerText"),
                                "movimentacao":movimentacao
                            }
                        },{upsert:True})
                except:
                    None
            except Exception as e:
                try:
                    botao = driver.find_element_by_id("botaoConsultarProcessos")
                    if botao:
                        driver.execute_script("arguments[0].click();", botao)
                        sleep(5)
                        dataMovimentacao = driver.find_elements_by_class_name("dataMovimentacao")
                        descricaoMovimentacao = driver.find_elements_by_class_name("descricaoMovimentacao") 
                        classeProcesso = driver.find_element_by_id("classeProcesso") 
                        assuntoProcesso = driver.find_element_by_id("assuntoProcesso") 
                        foroProcesso = driver.find_element_by_id("foroProcesso") 
                        varaProcesso = driver.find_element_by_id("varaProcesso") 
                        juizProcesso = driver.find_element_by_id("juizProcesso") 
                        # print(dataMovimentacao[0].get_attribute("innerText"),' ',descricaoMovimentacao[0].get_attribute("innerText"))

                        print(f'Processo: {processo}')
                        print('Classe: ',classeProcesso.get_attribute("innerText"))
                        print('Assunto: ',assuntoProcesso.get_attribute("innerText"))
                        # print('Foro: ',foroProcesso.get_attribute("innerText"))
                        print(f'Foro: {foro}')
                        print('Vara: ',varaProcesso.get_attribute("innerText"))
                        print('Juiz: ',juizProcesso.get_attribute("innerText"))

                        movimentacao = [[],[]]
                        for i,j in zip(dataMovimentacao,descricaoMovimentacao):
                            data = i.get_attribute("innerText").replace('\n','').replace('\t','').replace('  ',' ')
                            data = lreplace(' ','',data)
                            data = rreplace(' ','',data)
                            desc = j.get_attribute("innerText").replace('\n','').replace('\t','').replace('  ',' ')
                            desc = lreplace(' ','',desc)
                            desc = rreplace(' ','',desc)
                            print(f'{data} {desc}')
                            movimentacao[0].append(data)
                            movimentacao[1].append(desc)
                        try:
                            collection.update_one(
                                {"processo":processo},
                                {'$set':
                                    {
                                        "processo":processo,
                                        "junta":junta,
                                        "classe":classeProcesso.get_attribute("innerText"),
                                        "assunto":assuntoProcesso.get_attribute("innerText"),
                                        "foro":foroProcesso.get_attribute("innerText"),
                                        "vara":varaProcesso.get_attribute("innerText"),
                                        "juiz":juizProcesso.get_attribute("innerText"),
                                        "movimentacao":movimentacao
                                    }
                                },{upsert:True})
                        except:
                            None
                except:
                    None
                # print(e)

    driver.stop_client()
    driver.close()
    # id=linkPasta #Visualizar autos
