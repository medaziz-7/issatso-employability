from asyncio.windows_events import NULL
from operator import contains
from flask import Flask, render_template, request, url_for ,redirect
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np 
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
import warnings
warnings. filterwarnings('ignore')



app = Flask(__name__)
@app.route('/')
def home():
    return render_template('first_page.html')
@app.route('/', methods = ['GET', 'POST'])
def go_scrape():
    if request.method == 'POST':
        all_pass = request.form.get("pass_word")
        if all_pass == 'issat_so_employability':
            return  redirect("/scrape", code=302)
        else:
            return  redirect("/", code=302)
            
@app.route('/scrape')
def scrape():
    return render_template('home.html')
@app.route('/scrape', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST' :
       f = request.files['file']
       f.save(secure_filename(f.filename))
       df = pd.read_excel(f.filename)
       df['Linkedin_account'] = NULL
       df['Job_title'] = NULL
       df['Company'] = NULL
       df['Location'] = NULL
       #logging in my linked account 
       user_info = request.form.get("username")
       pass_info = request.form.get("password")
       driver = webdriver.Chrome('C:/chromedriver.exe')
       url = "https://www.linkedin.com/login"
       driver.get(url)
       #sending username
       user = driver.find_element_by_id('username')
       user.send_keys(user_info)
       sleep(3)
       #sending password
       password = driver.find_element_by_id('password')
       password.send_keys(pass_info)
       sleep(4)
       #click on login button
       button = driver.find_element_by_xpath('//*[@id="organic-div"]/form/div[3]/button')
       button.click()
       sleep(3)
       ##############
       for ind in df.index:
           try:
               nom = df['Nom'][ind]
               prenom = df['Prénom'][ind]
               #locating the search field
               search_field = driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/input')
               sleep(2)
               search_field.clear()
               #searching for people
               search_field.send_keys(prenom.lower() + ' ' + nom.lower())
               sleep(1)
               search_field.send_keys(Keys.RETURN)
               #checking the people box to look for people
               element_1 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-pill')))
               button_p = driver.find_element_by_xpath('//button[text() = "People"]')
               button_p.click()
               #clicking all filter button 
               sleep(1)
               element_2 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-reusables__filters-bar"]/div/div/button')))
               button_a = driver.find_element_by_xpath('//*[@id="search-reusables__filters-bar"]/div/div/button')
               button_a.click()
               sleep(1)
               #Identify the WebElement which will appear after scrolling down
               #elem = driver.find_element_by_xpath("//legend[contains(text(), 'School filter')]")
               # now execute query which actually will scroll until that element is not appeared on page.
               #driver.execute_script("arguments[0].scrollIntoView(true)",elem)
               #clicking on issat sousse for school
               driver.execute_script("let elem = document.querySelector('.artdeco-modal__content');elem.scrollTo(0, elem.scrollHeight / 2);")
               button_issat = driver.find_element_by_xpath('//label[@for="advanced-filter-schoolFilter-18420875"]')
               button_issat.click()
               element_4 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'reusable-search-filters-buttons')))
               #searching 
               button_search = driver.find_element_by_class_name('reusable-search-filters-buttons')
               button_search.click()
               #waiting for the profile to load up
               element_5 = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "app-aware-link")))
               sleep(3)
               driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
               sleep(1)
               #scraping the profile#########################################
               page = BeautifulSoup(driver.page_source, 'html.parser')
               profiles = page.find_all('a', class_ = 'app-aware-link')
               for profile in profiles:
                   if 'miniProfile' in profile.get('href') and nom.lower().split(' ')[0] in str(profile.get('href')): 
                       df['Linkedin_account'][ind] = profile.get('href').split('?')[0]
                       break
               element_6 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "flex-shrink-zero")))
               reset_button = driver.find_element_by_class_name("flex-shrink-zero")
               driver.execute_script("arguments[0].click();", reset_button)
               
           except NoSuchElementException:
               try:
                   exit_button = driver.find_element_by_class_name('artdeco-modal__dismiss')
                   exit_button.click()
                   #waiting for the profiles to load up
                   element_ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "app-aware-link")))
                   #scraping the profiles urls 
                   page = BeautifulSoup(driver.page_source, 'html.parser')
                   profiles = page.find_all('a', class_ = 'app-aware-link')
                   profiles_list = []
                   for profile in profiles:
                       if 'miniProfile' in profile.get('href') and nom.lower().split(' ')[0] in profile.get('href'): 
                           profiles_list.append(profile.get('href'))
                   profiles_list = list(dict.fromkeys(profiles_list))
                   break_flag = False
                   for url_ in profiles_list:
                       driver.get(url_)
                       sleep(3)
                       driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                       sleep(1)
                       html = driver.page_source 
                       page_2 = BeautifulSoup(html,'html.parser')
                       sections = page_2.find_all('section', class_ = 'artdeco-card ember-view break-words pb3 mt4')
                       for section in sections:
                           if 'id="education"' in str(section) and ('ISSAT'or 'Issat'or 'issat' or 'Higher Institute of Applied Sciences and Technology of Sousse') in str(section):
                               df['Linkedin_account'][ind] = url_.split('?')[0]
                               print(url_.split('?')[0])
                               break_flag = True
                               break  
                           
                           
                       if break_flag == True:
                           break
                       else:
                           df['Linkedin_account'][ind] = 'no linkedin account'
               except:
                   df['Linkedin_account'][ind] = 'no linkedin account'

           except ElementNotInteractableException:
               print('put the browser on full screen mode')
           except Exception as e:
               df['Linkedin_account'][ind] = 'no linkedin account'
               print('print pop up repeat an error occured')
       for ind in df.index :
          try:
            Job_title = NULL
            Company = NULL
            Location = NULL
            driver.get(df['Linkedin_account'][ind])
            page = BeautifulSoup(driver.page_source, 'html.parser')
            info_div = page.find('div', class_ = 'mt2 relative')
            job_title = info_div.find('div', class_ = 'text-body-medium break-words')
            Job_title_bf = job_title.text.strip()
            if ('chez') in Job_title_bf:
                Job_title = Job_title_bf.split('chez')[0]
            elif( 'à' ) in Job_title_bf:
                Job_title = Job_title_bf.split('à')[0]
            elif('at') in Job_title_bf:
                Job_title = Job_title_bf.split('at')[0] 
            else:
                Job_title = Job_title_bf
            df['Job_title'][ind] = Job_title
            location = info_div.find('span', class_ = "text-body-small inline t-black--light break-words")
            Location = location.text.strip()
            df['Location'][ind] = Location
            sections = page.find_all('section', class_ = 'artdeco-card')
            for section in sections:
                if 'id="experience"' in str(section):
                    exp_section = section
                    break
            current_job_info = exp_section.find('div', class_ = 'display-flex flex-column full-width align-self-center')
            spans = current_job_info.find_all('span', class_="visually-hidden")
            if 'mr1 hoverable-link-text t-bold' in str(current_job_info):
                Company= spans[0].text.split('·')[0].strip()
            else:
                Company= spans[1].text.split('·')[0].strip()
                
            df['Company'][ind] = Company
          except:
              df['Job_title'][ind] = 'not working currently' if df['Job_title'][ind] == NULL else Job_title
              df['Company'][ind] = 'not working currently' if df['Company'][ind] == NULL else Company
              df['Location'][ind] = 'not working currently' if df['Location'][ind] == NULL else Location

           
   return render_template('final.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
   

@app.route('/statistics')
def statistics_page():
    return render_template('statistics.html')

@app.route('/donnee')
def first():
    return render_template("modify.html")

@app.route('/donnee', methods = ['GET', 'POST'])
def gerer_donner():
    if request.method == 'POST':
        with open("year_17_18_2.csv", encoding="utf8") as file:
            return render_template("modify.html", csv=file)




if __name__ == "__main__":
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=5000)
    app.run(debug = True)



