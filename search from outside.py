import sys
import csv
import os, errno
import time
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

class Ui(QWidget):
    
    def __init__(self):
        
        super().__init__()
        self.title = 'Linkedin Competitor Search by Company'
        self.left = 100
        self.top = 100
        self.width = 500
        self.height = 200
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        global path_csv
        self.selectCsvButton()
        self.competitorSearchStart()
        # self.NicheSearchStart()
        self.show()

    def csv_path(self):
        try:
            path_csv
        except NameError:
            return False
        else:
            return path_csv
        
    def openFileNameDialog(self):
        #open file dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select CSV FILES", "","Comma Separated Value File (CSV) (*.csv)", options=options)
        if fileName:
            global path_csv
            path_csv = fileName
            print(path_csv)
        
    def selectCsvButton(self):
        #open file dialog trigger
        button = QPushButton('choose csv file', self)
        button.setGeometry(QRect(180, 50, 110, 30)) 
        button.clicked.connect(self.openFileNameDialog)
        
    def competitorSearchStart(self):
        button = QPushButton('Start Competitor Search', self)
        button.setGeometry(QRect(320, 130, 160, 50))
        button.clicked.connect(self.startScrapeByCompany)

    def startScrapeByCompany(self):
        path = self.csv_path()
        if path == False:
            print("some fields are empty. please fill it out")
            print(type(path))
        else:
            try:
                self.csv_path = path
                self.csv_path = self.csv_path.replace('/','\\\\')
                print(type(path))
                self.file = open(self.csv_path,'a', newline='')
                self.writer = csv.writer(self.file, delimiter=',')
                self.writer.writerow((''))
                self.file.close()
                self.setWindowTitle("Linkedin Scraper is working...")
                ScrapeLinkedin(self.csv_path).ScrapeByCompany()
            except PermissionError:
                print("File Permission Denied! I can't access the file.")
                self.browser.quit()

class ScrapeLinkedin():
    def __init__(self, path):
        self.csv_path = path
        self.csv_path = self.csv_path.replace('/','\\\\')
        print(self.csv_path)
        self.browser = webdriver.Chrome()
        self.browser.maximize_window()
        self.failCounter = 0
        self.requestCounter = 0

    def scroll(self):
        self.browser.execute_script("window.scrollTo(0,700);")
        print("scrolled..")

    def delay(self):
        seconds = random.randrange(25,60)
        print("delaying execution for " +str(seconds) + " seconds")
        time.sleep(seconds)

    def saveLog(self,msg):
        self.file = open('searchFromOutsideLog.txt','a', encoding='utf-8')
        self.file.write(msg)
        self.file.write('\n')
        self.file.close()
    
    def searchCompany(self,name):
        #search company function
        #parameters: name of the company
        #return value: company url

        print("searching for company..")
        self.searchString = "site:linkedin.com/company "+ name
        self.browser.get('https://www.google.com')
        self.element = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.NAME, 'q'))
        )
        self.query = self.browser.find_element_by_name('q')
        self.query.send_keys(self.searchString)
        self.query.send_keys(u'\ue007')

        try:
            self.element = WebDriverWait(self.browser, 30).until(
                # EC.presence_of_element_located((By.CSS_SELECTOR, 'cite._Rm'))
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h3.r > a'))
            )
            # self.result = self.browser.find_element_by_css_selector('cite._Rm')
            self.result = self.browser.find_element_by_css_selector('h3.r > a')
            self.result = self.result.get_attribute("href")
            print("search done!")
            print(self.result)

            return self.result

            # self.browser.close()
        except TimeoutException:
            print ("Can't find results! Trying again.")
            return self.searchCompany(name)

    def getRelatedCompanies(self,companyUrl,comp,lvl):
        #gets the related companies
        #parameters: company url
        #return value: array of urls of related companies

        print("company: "+ comp)
        print("processing level "+ str(lvl) +" related companies...")
        
        self.results = []
        self.browser.get(companyUrl)
        self.requestCounter += 1
        print("Number of page requested: "+str(self.requestCounter))

        if self.requestCounter == 54:
            self.requestCounter = 0
            self.bigDelay()
        else:
            self.delay()

        self.scroll()
        self.scroll()
        self.scroll()
        self.scroll()

        try:
            self.element = WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.also-viewed.module > ul > li > a"))
            )
            print ("Page is ready!")
            self.scroll()
            self.scroll()
            self.relatedCompanies = self.browser.find_elements_by_css_selector('div.also-viewed.module > ul > li > a')
            for self.url in self.relatedCompanies:
                # self.results.append(self.url.get_attribute('href').replace("?trk=extra_biz_viewers_viewed",""))
                self.results.append(self.url.get_attribute('href'))
                print(self.url.get_attribute('href').replace("?trk=extra_biz_viewers_viewed",""))
            print("===========================")
            print("total: " + str(len(self.relatedCompanies)))
            print("===========================")
            self.failCounter = 0
            print("Fail Counter:"+str(self.failCounter))
            return self.results
        except TimeoutException:
            
            if self.failCounter == 5:
                print("Information could not be found. This is the time to let go.")
                print("Fail Counter:"+str(self.failCounter))
                self.failCounter = 0
                return self.results
            else:
                self.failCounter += 1
                print ("Can't find the information I need! Trying again.")
                print("Fail Counter:"+str(self.failCounter))
                return self.getRelatedCompanies(companyUrl,comp,lvl)


    def getCompanyInfo(self,companyUrl):

        
        self.browser.get(companyUrl)
        self.requestCounter += 1
        print("Number of page requested: "+str(self.requestCounter))
        if self.requestCounter == 54:
            self.requestCounter = 0
            self.bigDelay()
        else:
            self.delay()

        try:
            self.element = WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.header > div.left-entity > div > h1 > span'))
            )
            self.name = self.browser.find_element_by_css_selector('div.header > div.left-entity > div > h1 > span')
            self.name = self.name.text
            self.website = self.browser.find_element_by_css_selector('.basic-info-about > ul > li.website > p > a')
            self.website = self.website.text
            print("("+self.website+")")
            print("Fail Counter:"+str(self.failCounter))
            self.failCounter = 0
            return self.name, self.website
        except TimeoutException:
            if self.failCounter == 5:
                print("Information could not be found. This is the time to let go.")
                print("Fail Counter:"+str(self.failCounter))
                self.failCounter = 0
                self.name=''
                self.website=''
                return self.name, self.website
            else:
                self.failCounter += 1
                print ("Can't find the information I need! Trying again.")
                print("Fail Counter:"+str(self.failCounter))
                return self.getCompanyInfo(companyUrl)
        except NoSuchElementException:
            self.name = self.browser.find_element_by_css_selector('div.header > div.left-entity > div > h1 > span')
            self.name = self.name.text
            self.website = ''
            print("No website found!")
            print("Fail Counter:"+str(self.failCounter))
            self.failCounter = 0
            return self.name, self.website

    def GetColumnsFromCSV(self,column):
        self.container = []
        self.file = open(self.csv_path,'r')
        self.reader = csv.reader(self.file)
        self.reader = list(filter(None, self.reader))
        self.rowCounter = 0
        for self.row in self.reader:
            if self.rowCounter > 0:
                self.container.append(self.row[column])
            self.rowCounter +=1
        self.file.close()
        self.container = list(filter(None, self.container))
        return self.container

    def ScrapeByCompany(self):

        self.companies = self.GetColumnsFromCSV(5)
        for self.company in self.companies:

            self.lvl1Search,self.lvl2Search, self.lvl3Search, self.lvl4Search, self.lvl5Search, self.lvl6Search = [],[],[],[],[],[]
            self.lvl1Search = self.getRelatedCompanies(self.searchCompany(self.company),self.company,1)
            print("COMPANY PROCESSING: " + self.company)
            print("=========================================")
            print("==============STARTING LVL 1=============")
            print("=========================================")
            
            for self.lvl1_item in self.lvl1Search:
                self.lvl2Search = self.lvl2Search + self.getRelatedCompanies(self.lvl1_item,self.company,2)
            
            print("=========================================")
            print("==============LVL 1 ENDS HERE============")
            print("==============STARTING LVL 2=============")

            self.lvl2Search = set(self.lvl2Search)#removes duplicate links
            self.lvl2Search = list(self.lvl2Search)#converts to list for concatenation
            for self.lvl2_item in self.lvl2Search:
                self.lvl3Search = self.lvl3Search + self.getRelatedCompanies(self.lvl2_item,self.company,3)
        
            print("=========================================")
            print("==============LVL 2 ENDS HERE============")
            print("==============STARTING LVL 3=============")

            self.lvl3Search = set(self.lvl3Search)#removes duplicate links
            self.lvl3Search = list(self.lvl3Search)#converts to list for concatenation
            for self.lvl3_item in self.lvl3Search:
                self.lvl4Search = self.lvl4Search + self.getRelatedCompanies(self.lvl3_item,self.company,4)
        
            print("=========================================")
            print("==============LVL 3 ENDS HERE============")
            print("==============STARTING LVL 4=============")

            self.lvl4Search = set(self.lvl4Search)#removes duplicate links
            self.lvl4Search = list(self.lvl4Search)#converts to list for concatenation
            for self.lvl4_item in self.lvl4Search:
                self.lvl5Search = self.lvl5Search + self.getRelatedCompanies(self.lvl4_item,self.company,5)
        
            print("=========================================")
            print("==============LVL 4 ENDS HERE============")
            self.lvl5Search = set(self.lvl5Search)#removes duplicate links
            self.lvl5Search = list(self.lvl5Search)#converts to list for concatenation

            if len(self.lvl5Search) < 500:
                print("=========================================")
                print("===========LVL 5 is less than 500========")
                print("==============STARTING LVL 6=============")
                for self.lvl5_item in self.lvl5Search:
                    self.lvl6Search = self.lvl6Search + self.getRelatedCompanies(self.lvl5_item,self.company,6)
                self.lvl6Search = set(self.lvl6Search)#removes duplicate links
                self.lvl6Search = list(self.lvl6Search)#converts to list for concatenation
                print("=========================================")
                print("==============LVL 6 ENDS HERE============")

            print("LEVEL 1 Search: " + str(len(self.lvl1Search)))
            print("LEVEL 2 Search: " + str(len(self.lvl2Search)))
            print("LEVEL 3 Search: " + str(len(self.lvl3Search)))
            print("LEVEL 4 Search: " + str(len(self.lvl4Search)))
            print("LEVEL 5 Search: " + str(len(self.lvl5Search)))
            print("LEVEL 6 Search: " + str(len(self.lvl6Search)))
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Ui()
    sys.exit(app.exec_())
