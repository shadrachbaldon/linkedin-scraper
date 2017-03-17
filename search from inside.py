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
        self.title = 'Linkedin Scraper'
        self.left = 100
        self.top = 100
        self.width = 500
        self.height = 300
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        global path_csv
        self.loginForm()
        self.selectCsvButton()
        self.competitorSearchStart()
        self.NicheSearchStart()
        self.show()

    def loginForm(self):
        #label
        self.lblEmail = QLabel("Email:", self)
        self.lblEmail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lblEmail.setAlignment(Qt.AlignCenter)
        self.lblEmail.setGeometry(QRect(40, 20, 40, 50))

        #textbox
        self.txtEmail = QLineEdit(self)
        self.txtEmail.setGeometry(QRect(90, 30, 250, 30))

        #label
        self.lblPassword = QLabel("Password:", self)
        self.lblPassword.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lblPassword.setAlignment(Qt.AlignCenter)
        self.lblPassword.setGeometry(QRect(20, 70, 60, 50))

        #open file dialog trigger
        self.txtPassword = QLineEdit(self)
        self.txtPassword.setGeometry(QRect(90, 80, 250, 30))

    def csv_path(self):
        try:
            path_csv
        except NameError:
            return False
        else:
            return path_csv
        
    def displayPath(self):
        
        self.lblPath = QLabel("path_csv", self)
        self.lblPath.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lblPath.setGeometry(QRect(130, 135, 110, 50))
        print("display path called")
        
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
        button = QPushButton('choose file', self)
        button.setGeometry(QRect(20, 145, 110, 30)) 
        button.clicked.connect(self.openFileNameDialog)
        
    def competitorSearchStart(self):
        button = QPushButton('Start Competitor Search', self)
        button.setGeometry(QRect(20, 230, 160, 50))
        email = self.txtEmail.text()
        password = self.txtPassword.text()
        button.clicked.connect(self.startScrapeByCompany)

    def startScrapeByCompany(self):
        email = self.txtEmail.text().strip()
        password = self.txtPassword.text().strip()
        path = self.csv_path()
        if email == '' or password == '' or path == False:
            print("some fields are empty. please fill it out")
        else:
            try:
                self.csv_path = path
                self.csv_path = self.csv_path.replace('/','\\\\')
                self.file = open(self.csv_path,'a', newline='')
                self.writer = csv.writer(self.file, delimiter=',')
                self.writer.writerow((''))
                self.file.close()
                self.setWindowTitle("Linkedin Scraper is working...")
                ScrapeLinkedin(email,password,self.csv_path).ScrapeByCompany()
            except PermissionError:
                print("File Permission Denied! I can't access the file.")
                self.browser.quit()


    def NicheSearchStart(self):
        button = QPushButton('Start Keyword Search', self)
        button.setGeometry(QRect(200, 230, 160, 50))
        #button.clicked.connect(self.openFileNameDialog)

class ScrapeLinkedin():
    def __init__(self, email, password,path):
        self.usernameStr = email
        self.passwordStr = password
        self.csv_path = path
        self.csv_path = self.csv_path.replace('/','\\\\')
        print(self.csv_path)
        self.browser = webdriver.Chrome()
        self.browser.get(('https://linkedin.com'))
        self.browser.maximize_window()
        self.login()
        self.failCounter = 0
        self.requestCounter = 0
        self.saveCounter = 0

    def login(self):
        try:
            self.element = WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.ID, 'login-email'))
            )
            # fill in username
            self.username = self.browser.find_element_by_id('login-email')
            self.username.send_keys(self.usernameStr)
            #fill the password
            self.password = self.browser.find_element_by_id('login-password')
            self.password.send_keys(self.passwordStr)
            #click the sign in button
            self.loginbtn = self.browser.find_element_by_id('login-submit')
            self.loginbtn.click()
        except TimeoutException:
            print ("Can't find the login form! Trying again.")
            return self.login()

    def scroll(self):
        self.browser.execute_script("window.scrollTo(0,700);")
        print("scrolled..")

    def delay(self):
        seconds = random.randrange(15,45)
        print("delaying execution for " +str(seconds) + " seconds")
        time.sleep(seconds)

    def StopForNow(self):
        print("The bot is paused for 24 hours to avoid being blocked!")
        time.sleep(86400)
    
    def searchCompany(self,name):
        #search company function
        #parameters: name of the company
        #return value: company url
        print("searching for company..")
        self.browser.get(('https://www.linkedin.com/search/results/companies/?keywords='+name+'&origin=GLOBAL_SEARCH_HEADER'))
        try:
            self.element = WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-control-name="search_srp_result"]'))
            )
            self.result = self.browser.find_element_by_xpath('//*[@data-control-name="search_srp_result"]')
            print("search done!")
            return self.result.get_attribute('href')
        except TimeoutException:
            print ("Can't find results! Trying again.")
            return self.searchCompany(name)

    def getCompanyInfo(self):
        try:
            self.element = WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="org-top-card-module__name mb1 Sans-26px-black-85%-light"]'))
            )
            self.name = self.browser.find_element_by_xpath('//*[@class="org-top-card-module__name mb1 Sans-26px-black-85%-light"]')
            self.name = self.name.text
            self.website = self.browser.find_element_by_css_selector('.org-about-company-module__company-page-url a')
            self.website = self.website.get_attribute('href')
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
                return self.getCompanyInfo()
        except NoSuchElementException:
            self.name = self.browser.find_element_by_xpath('//*[@class="org-top-card-module__name mb1 Sans-26px-black-85%-light"]')
            self.name = self.name.text
            self.website = ''
            print("No website found!")
            print("Fail Counter:"+str(self.failCounter))
            self.failCounter = 0
            return self.name, self.website

    def getRelatedCompanies(self,companyUrl,comp,lvl):
        #gets the related companies
        #parameters: company url
        #return value: array of urls of related companies
        if self.requestCounter == 300:
            self.StopForNow()
        else:
            print("company: "+ comp)
            print("processing level "+ str(lvl) +" related companies...")
            self.results = []
            self.browser.get(companyUrl)
            self.requestCounter += 1
            print("Page Request made: "+str(self.requestCounter))
            self.delay()
            self.scroll()
            self.scroll()
    
            if lvl > 1:
                self.info = self.getCompanyInfo()
                self.comapnyInfoSave = self.saveToFile(self.info[0],self.info[0])
    
            try:
                self.element = WebDriverWait(self.browser, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li[class=org-similar-companies-module__list-item] span dl.company-info dt a"))
                )
                print ("Page is ready!")
                self.scroll()
                self.scroll()
                self.relatedCompanies = self.browser.find_elements_by_css_selector('li[class=org-similar-companies-module__list-item] span dl.company-info dt a')
                for self.url in self.relatedCompanies:
                    self.results.append(self.url.get_attribute('href'))
                print("===========================")
                print(len(self.relatedCompanies))
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

    def saveToFile(self,name,website):
        #convert name to list
        self.temp = []
        self.temp.append(name)
        #convert name to set for comparison on the file
        print(self.temp)
        name = set(self.temp)        self.masterList = self.GetColumnsFromCSV(5)
        self.masterList = set(self.masterList)
        self.toSave = name - self.masterList
        if len(self.toSave) > 0:
            try:
                name = list(name)
                self.file = open(self.csv_path,'a', newline='', encoding='utf-8')
                print("OOOOOOOOOOOOOOO")
                self.writer = csv.writer(self.file, delimiter=',')
                if (self.name == '') and (self.website == ''):
                    pass
                else:
                    self.clean = self.website.rstrip()
                    print(self.clean)
                    self.writer.writerow(('','','','','',self.name,'',self.clean,''))
                self.file.close()
                self.saveCounter += 1
                print("Saved Info total: "+str(self.saveCounter))

            except PermissionError:
                print("File Permission Denied! I can't access the file.")
        else:
            print("No need to save this is already on the file")

    def saveLog(self,msg):
        self.file = open('log.txt','a')
        self.file.write(msg)
        self.file.write('\n')
        self.file.close()

    def ScrapeByCompany(self):     

        self.companies = self.GetColumnsFromCSV(5)

        for self.company in self.companies:

            self.lvl1Search,self.lvl2Search, self.lvl3Search, self.lvl4Search, self.lvl5Search, self.lvl6Search = [],[],[],[],[],[]
            self.lvl1Search = self.getRelatedCompanies(self.searchCompany(self.company),self.company,1)
            self.log = self.company+" Level 1 total:"+str(len(self.lvl1Search))
            self.saveLog(self.log)

            print("COMPANY PROCESSING: " + self.company)
            print("=========================================")
            print("==============STARTING LVL 1=============")
            print("=========================================")
            
            for self.lvl1_item in self.lvl1Search:
                self.lvl2Search = self.lvl2Search + self.getRelatedCompanies(self.lvl1_item,self.company,2)
            self.lvl2Search = set(self.lvl2Search)#removes duplicate links
            self.lvl2Search = list(self.lvl2Search)#converts to list for concatenation
            self.log = self.company+" Level 2 total:"+str(len(self.lvl2Search))
            self.saveLog(self.log)
            print("=========================================")
            print("==============LVL 1 ENDS HERE============")
            print("==============STARTING LVL 2=============")

            
            for self.lvl2_item in self.lvl2Search:
                self.lvl3Search = self.lvl3Search + self.getRelatedCompanies(self.lvl2_item,self.company,3)
            self.lvl3Search = set(self.lvl3Search)#removes duplicate links
            self.lvl3Search = list(self.lvl3Search)#converts to list for concatenation
            self.log = self.company+" Level 3 total:"+str(len(self.lvl3Search))
            self.saveLog(self.log)

            print("=========================================")
            print("==============LVL 2 ENDS HERE============")
            print("==============STARTING LVL 3=============")

            
            for self.lvl3_item in self.lvl3Search:
                self.lvl4Search = self.lvl4Search + self.getRelatedCompanies(self.lvl3_item,self.company,4)
            self.lvl4Search = list(self.lvl4Search)#converts to list for concatenation
            self.lvl4Search = set(self.lvl4Search)#removes duplicate links
            self.log = self.company+" Level 4 total:"+str(len(self.lvl4Search))
            self.saveLog(self.log)
        
            print("=========================================")
            print("==============LVL 3 ENDS HERE============")
            print("==============STARTING LVL 4=============")

            
            
            for self.lvl4_item in self.lvl4Search:
                self.lvl5Search = self.lvl5Search + self.getRelatedCompanies(self.lvl4_item,self.company,5)
            self.lvl5Search = set(self.lvl5Search)#removes duplicate links
            self.lvl5Search = list(self.lvl5Search)#converts to list for concatenation
            self.log = self.company+" Level 5 total:"+str(len(self.lvl5Search))
            self.saveLog(self.log)
        
            print("=========================================")
            print("==============LVL 4 ENDS HERE============")
            

            if len(self.lvl5Search) < 500:
                print("=========================================")
                print("===========LVL 5 is less than 500========")
                print("==============STARTING LVL 6=============")
                for self.lvl5_item in self.lvl5Search:
                    self.lvl6Search = self.lvl6Search + self.getRelatedCompanies(self.lvl5_item,self.company,6)
                self.lvl6Search = set(self.lvl6Search)#removes duplicate links
                self.lvl6Search = list(self.lvl6Search)#converts to list for concatenation
                self.log = self.company+" Level 5 total:"+str(len(self.lvl6Search))
                self.saveLog(self.log)
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