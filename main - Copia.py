import time
from datetime import datetime
from selenium import webdriver
import pymysql
from selenium.webdriver.firefox.options import Options


class Corona:

    def __init__(self):
        option = Options()
        option.headless = True
        driver = webdriver.Firefox(options=option)

        self.crawler(driver)
        self.connect()
        value = self.select("SELECT * FROM `data` WHERE `data_hora`= '%s'" % self.data_hora)

        if len(value) == 0:
            sql = "INSERT INTO data (mortes, novos_casos, recuperados, data_hora) VALUES (%s, %s, %s, %s)"
            values = (self.n_mortes, self.n_casos_novos, self.n_recuperados, self.data_hora)
            print("entrou")
            self.insert(sql, values)

    def crawler(self, driver):
        self.driver = driver
        try:
            self.url = "https://covid.saude.gov.br/"
            self.driver.get(self.url)
            time.sleep(5)

            mortes = self.driver.find_element_by_xpath("//div[@class='lb-total tp-geral width-auto fnt-size']").text
            casos_novos = self.driver.find_element_by_xpath(
                "//div[@class='ct-info display-flex justify-start']//div[@class='lb-total tp-geral width-auto']").text
            recuperados = self.driver.find_element_by_xpath(
                "//div[@class='card-total tp-geral tp-totais bg-primary']").text
            self.data_hora = self.driver.find_element_by_xpath("//div[@class='lb-grey']//span").text

            self.n_mortes = mortes[0:mortes.index("\n")].replace(".", "")
            self.n_casos_novos = casos_novos[0:casos_novos.index("\n")].replace(".", "")
            self.n_recuperados = recuperados[recuperados.index("\n") + 1: len(recuperados)].replace(".", "")

            data_hora = datetime.strptime(self.data_hora, "%d/%m/%Y %H:%M")
            self.data_hora = data_hora.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            print("Erro no crawler %s" % (e))
        self.driver.quit()

    def connect(self):
        try:
            self.conn = pymysql.connect(host='localhost', user='root', passwd='', database='corona')
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("Erro de conexão: %s" % (e))

    def insert(self, sql, values):
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
        except Exception as e:
            print("Erro na inserção: %s" % (e))

    def select(self, sql):
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("Erro na seleção: %s" % (e))
            return None


g = Corona()
values = g.select("SELECT * FROM data")
for v in values:
    print("número de mortes: "+str(v[0]))
    print("número de casos novos: "+str(v[1]))
    print("número de recuperados: "+str(v[2]))
    date_str = v[3].strftime("%d-%m-%Y")
    hora_str = v[3].strftime("%H:%M:%S")
    print("data de envio: "+date_str+" as "+hora_str)
    print("-------------------------------------------------")
