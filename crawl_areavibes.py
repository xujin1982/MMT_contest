# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 14:30:20 2016

@author: Junxiao
"""

from bs4 import BeautifulSoup
import urllib2
import re
import time
from decimal import Decimal
from re import sub

# 找到ZIP CODE的link
# 两个不同的link供测试
url = "http://www.areavibes.com/search-results/?zip=28662&ll=36.021516+-81.899121"
#url = "http://www.areavibes.com/search-results/?zip=77081&ll=29.7162+-95.483"

#%% 搜索页
#print 'wait 3 sec'
time.sleep(3)

page = urllib2.urlopen(url)
soup = BeautifulSoup(page, 'lxml')
search_result = soup.findAll(href = re.compile("ll="))
for link in search_result:
    livability_url= 'http://www.areavibes.com'+ link.get('href')


#%% Livability page
#print 'wait 2 sec'
time.sleep(2)

livability_page = urllib2.urlopen(livability_url)
livability_soup = BeautifulSoup(livability_page, 'lxml')
cost_of_living_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("cost-of-living/")).get('href')
crime_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("crime/")).get('href')
education_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("education/")).get('href')
employment_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("employment/")).get('href')
housing_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("housing/")).get('href')
weather_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("weather/")).get('href')
demographics_url = 'http://www.areavibes.com' + livability_soup.find(href = re.compile("demographics/")).get('href')

table_content = livability_soup.findAll(attrs = {'class':['score-map']})
livability = map(float, re.findall(r'\d+\.*\d*', str(table_content)))[0]

#%% Cost of living page
#print 'wait 2 sec'
time.sleep(2)
cost_of_living_page = urllib2.urlopen(cost_of_living_url)
cost_of_living_soup = BeautifulSoup(cost_of_living_page, 'lxml')
table_content = cost_of_living_soup.findAll(attrs = {'class':['table-overflow-container']})


FeatureName = ['Household', 'Owners', 'Renters', 'General Sales Tax', 'With Max Surtax', 
               'Income Tax (Low)', 'Income Tax (High)', 'Haircut', 'Beauty Salon', 
               'Toothpaste', 'Shampoo', 'Movie', 'Bowling', 'Ground Beef', 'Fried Chicken', 
               'Milk', 'Potatoes', 'Pizza', 'Beer', 'Optometrist', 'Doctor','Dentist', 
               'Ibuprofen', 'Lipitor', 'Home Price', 'Avg. Mortgage Payment', 'Apartment Rent', 
               'Gasoline', 'Tire Balancing', 'All Electricity', 'Phone']
offset_cost_of_living = [2, 2, 2, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
                         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
boolean_cost_of_living = [0] * (len(FeatureName))
values_cost_of_living = [0] * (len(FeatureName))


for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = temp_GST[j + offset_cost_of_living[k]].contents[0]                        
                        print FeatureName[k],':\t', temp_value
                        boolean_cost_of_living[k] = 1
                        try:
                            values_cost_of_living[k] = float(Decimal(sub(r'[^\d.]', '', temp_value)))
                        except:
                            boolean_cost_of_living[k] = 0
                break



#%% Crime page
#print 'wait 2 sec'
time.sleep(2)
crime_page = urllib2.urlopen(crime_url)
crime_soup = BeautifulSoup(crime_page, 'lxml')
table_content = crime_soup.findAll(attrs = {'class':['table-overflow-container']})


FeatureName = ['Murder', 'Rape', 'Robbery', 'Assault', 'Violent crime', 'Burglary', 'Theft', 
               'Vehicle theft', 'Property crime','Law enforcement employees', 'Police officers']
offset_crime = [2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1]
boolean_crime = [0] * (len(FeatureName))
values_crime = [0] * (len(FeatureName))


for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = temp_GST[j + offset_crime[k]].contents[0]                        
                        print FeatureName[k],':\t', temp_value
                        boolean_crime[k] = 1
                        try:
                            values_crime[k] = float(Decimal(sub(r'[^\d.]', '', temp_value)))  # deal with n/a
                        except:
                            boolean_crime[k] = 0
                break
            
# find data of previous year  from figure
figure_content = crime_soup.findAll(attrs = {'type':['text/javascript']})
for yy in figure_content:
    yy_str = yy.string
    try:    
        if 'yy_crime' in yy_str:
            temp_value = map(float, re.findall(r'\d+\.*\d*', str(yy_str)))
            values_crime = values_crime + temp_value[-3:]
            boolean_crime = boolean_crime + [1, 1, 1]
            print 'Violent (1 years ago):\t', values_crime[k+1]
            print 'Property  (1 years ago):\t', values_crime[k+2]
            print 'Crime  (1 years ago):\t', values_crime[k+3]
            break
    except:
        temp_value = [0]
        
if (len(boolean_crime) == 11):
    values_crime = values_crime + [0, 0, 0]
    boolean_crime = boolean_crime + [0, 0, 0]
    
    
#%% Education page

#print 'wait 2 sec'
time.sleep(2)
education_page = urllib2.urlopen(education_url)
education_soup = BeautifulSoup(education_page, 'lxml')
table_content = education_soup.findAll(attrs = {'class':['table-overflow-container']})

FeatureName = ['Average Test Scores', 'Student/Teacher ratio', 'Total public schools',
               'Total private schools', 'Total post-secondary schools', 'Completed 8th grade', 
               'Completed high school', 'Completed some college', 'Completed associate degree',
               'Completed bachelors', 'Completed masters', 'Completed professional degree', 
               'Completed doctorate']
offset_education = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
boolean_education = [0] * (len(FeatureName))
values_education = [0] * (len(FeatureName))

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = temp_GST[j + offset_education[k]].contents[0]                        
                        print FeatureName[k],':\t', temp_value
                        boolean_education[k] = 1
                        try:
                            values_education[k] = float(Decimal(sub(r'[^\d.]', '', temp_value))) # deal with n/a
                        except:
                            boolean_education[k] = 0
                break



# find data of previous year  from figure
figure_content = education_soup.findAll(attrs = {'type':['text/javascript']})
k = len(values_education)
for yy in figure_content:
    yy_str = yy.string
    try:    
        if 'highest_edu' in yy_str:
            temp_value = map(float, re.findall(r'\d+\.*\d*', str(yy_str)))
            values_education = values_education + temp_value
            boolean_education = boolean_education + [1] * 14
            print 'High school diploma (Male):\t', values_education[k+0]
            print 'Some college (Male):\t', values_education[k+1]
            print 'Associates degree (Male):\t', values_education[k+2]
            print 'Professional schooling (Male):\t', values_education[k+3]
            print 'Bachelor’s degree (Male):\t', values_education[k+4]
            print 'Master’s degree (Male):\t', values_education[k+5]
            print 'Doctorate degree (Male):\t', values_education[k+6]
            print 'High school diploma (Female):\t', values_education[k+7]
            print 'Some college (Female):\t', values_education[k+8]
            print 'Associates degree (Female):\t', values_education[k+9]
            print 'Professional schooling (Female):\t', values_education[k+10]
            print 'Bachelor’s degree (Female):\t', values_education[k+11]
            print 'Master’s degree (Female):\t', values_education[k+12]
            print 'Doctorate degree (Female):\t', values_education[k+13]
            break
    except:
        temp_value = [0]
        
if (len(boolean_education) == 13):
    values_education = values_education + [0] * 14
    boolean_education = boolean_education + [0] * 14
    
    
#%% Employment page

#print 'wait 2 sec'
time.sleep(2)
employment_page = urllib2.urlopen(employment_url)
employment_soup = BeautifulSoup(employment_page, 'lxml')
table_content = employment_soup.findAll(attrs = {'class':['table-overflow-container']})    



FeatureName = ['Income per capita', 'Median household income', 'Median income owner occupied',
               'Median income renter occupied', 'Median earnings male', 'Median earnings female', 
               'Unemployment rate', 'Poverty level']
offset_employment = [1, 1, 1, 1, 1, 1, 1, 1]
boolean_employment = [0] * (len(FeatureName))
values_employment = [0] * (len(FeatureName))

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = temp_GST[j + offset_employment[k]].contents[0]                        
                        print FeatureName[k],':\t', temp_value
                        boolean_employment[k] = 1
                        try:
                            values_employment[k] = float(Decimal(sub(r'[^\d.]', '', temp_value))) # deal with n/a
                        except:
                            boolean_employment[k] = 0
                break

FeatureName = ['Construction industry', 'Manufacturing sector', 'Financial & insurance services',
               'Wholesale & retail services', 'Public administration', 
               'Transportation, warehousing & utilities', 'Education, health & social services', 'Other']
offset_employment = [1, 1, 1, 1, 1, 1, 1, 1]

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        try:
                            temp_value = temp_GST[j + offset_employment[k]].contents[0]                        
                            print FeatureName[k],'(Male):\t', temp_value
                            boolean_employment = boolean_employment + [1]
                            values_employment = values_employment + [float(Decimal(sub(r'[^\d.]', '', temp_value)))] # deal with n/a
                        except:
                            boolean_employment = boolean_employment + [0]
                            values_employment = values_employment + [0]
                break

offset_employment = [2, 2, 2, 2, 2, 2, 2, 2]

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        try:
                            temp_value = temp_GST[j + offset_employment[k]].contents[0]                        
                            print FeatureName[k],'(Female):\t', temp_value
                            boolean_employment = boolean_employment + [1]
                            values_employment = values_employment + [float(Decimal(sub(r'[^\d.]', '', temp_value)))] # deal with n/a
                        except:
                            boolean_employment = boolean_employment + [0]
                            values_employment = values_employment + [0]
                break     


# find data of previous year  from figure
figure_content = employment_soup.findAll(attrs = {'type':['text/javascript']})
k = len(values_employment)
for yy in figure_content:
    yy_str = str(yy.string)
    try:    
        if 'work_type' in yy_str:
            yy_str = yy_str.replace('35 hours', '')
            yy_str = yy_str.replace('34 to 15', '')
            yy_str = yy_str.replace('14 to 1', '')
            temp_value = map(float, re.findall(r'\d+\.*\d*', yy_str))
            values_employment = values_employment + temp_value
            boolean_employment = boolean_employment + [1] * 12
            print 'In labor force:\t', values_employment[k+0]
            print 'Military:\t', values_employment[k+1]
            print 'Unemployed:\t', values_employment[k+2]
            print 'Unknown/Other:\t', values_employment[k+3]
            print '35 hours plus (Male):\t', values_employment[k+4]
            print '34 to 15 hours (Male):\t', values_employment[k+5]
            print '14 to 1 hours (Male):\t', values_employment[k+6]
            print 'None (Male):\t', values_employment[k+7]
            print '35 hours plus (Female):\t', values_employment[k+8]
            print '34 to 15 hours (Female):\t', values_employment[k+9]
            print '14 to 1 hours (Male):\t', values_employment[k+10]
            print 'None (Female):\t', values_employment[k+11]
            break
    except:
        temp_value = [0]
        
if (len(boolean_employment) == 24):
    values_employment = values_employment + [0] * 12
    boolean_employment = boolean_employment + [0] * 12   



k = len(values_employment)
for yy in figure_content:
    yy_str = str(yy.string)
    try:    
        if 'wage_brackets' in yy_str:
#            print yy_str
            yy_str = yy_str.replace('$0 - 10K', '')
            yy_str = yy_str.replace('$10K - 25K', '')
            yy_str = yy_str.replace('$25K - 40K', '')
            yy_str = yy_str.replace('$40K - 65K', '')
            yy_str = yy_str.replace('$65K - 100K', '')
            yy_str = yy_str.replace('$100K plus', '')
            temp_value = map(float, re.findall(r'\d+\.*\d*', yy_str))
#            print temp_value
            values_employment = values_employment + temp_value
            boolean_employment = boolean_employment + [1] * 12
            print '0 - 10k (Male):\t', values_employment[k+0]
            print '10k - 25k (Male):\t', values_employment[k+1]
            print '25k - 40k (Male):\t', values_employment[k+2]
            print '40k - 65k (Male):\t', values_employment[k+3]
            print '65k - 100k (Male):\t', values_employment[k+4]
            print '100k plus (Male):\t', values_employment[k+5]
            print '0 - 10k (Female):\t', values_employment[k+6]
            print '10k - 25k (Female):\t', values_employment[k+7]
            print '25k - 40k (Female):\t', values_employment[k+8]
            print '40k - 65k (Female):\t', values_employment[k+9]
            print '65k - 100k (Female):\t', values_employment[k+10]
            print '100k plus (Female):\t', values_employment[k+11]
            break
    except:
        temp_value = [0]
        
if (len(boolean_employment) == 36):
    values_employment = values_employment + [0] * 12
    boolean_employment = boolean_employment + [0] * 12   




#%% Housing page

#print 'wait 2 sec'
time.sleep(2)
housing_page = urllib2.urlopen(housing_url)
housing_soup = BeautifulSoup(housing_page, 'lxml')
table_content = housing_soup.findAll(attrs = {'class':['table-overflow-container']})    

FeatureName = ['Median home price', 'Median rent asked', 'Avg. people per household',
               'Owner occupied households', 'Renter occupied households']
offset_housing = [1, 1, 1, 1, 1]
boolean_housing = [0] * (len(FeatureName))
values_housing = [0] * (len(FeatureName))

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = temp_GST[j + offset_housing[k]].contents[0]
                        print FeatureName[k],':\t', temp_value
                        boolean_housing[k] = 1
                        try:
                            values_housing[k] = float(Decimal(sub(r'[^\d.]', '', temp_value))) # deal with n/a
                        except:
                            boolean_housing[k] = 0
                break

# find data of previous year  from figure
figure_content = housing_soup.findAll(attrs = {'type':['text/javascript']})
k = len(values_housing)
for yy in figure_content:
    yy_str = str(yy.string)
    try:    
        if 'vac_occ_lvls' in yy_str:
#            print yy_str
            yy_str = yy_str.replace('0-9%', '')
            yy_str = yy_str.replace('10-19%', '')
            yy_str = yy_str.replace('20-29%', '')
            yy_str = yy_str.replace('30-39%', '')
            yy_str = yy_str.replace('40-49%', '')
            yy_str = yy_str.replace('50%+', '')
            temp_value = map(float, re.findall(r'\d+\.*\d*', yy_str))
            values_housing = values_housing + temp_value
#            print temp_value
            boolean_housing = boolean_housing + [1] * 27
            print 'Occupied:\t', values_housing[k+0]
            print 'Vacant:\t', values_housing[k+1]
            print 'For rent:\t', values_housing[k+2]
            print 'For sale only:\t', values_housing[k+3]
            print 'Rented\Sold not occ:\t', values_housing[k+4]
            print 'Seasonal:\t', values_housing[k+5]
            print 'Migrant workers:\t', values_housing[k+6]
            print 'Other:\t', values_housing[k+7]
            print 'Avg. household size:\t', values_housing[k+8]
            print 'Avg. household size owner occ:\t', values_housing[k+9]
            print 'Avg. household size renter occ:\t', values_housing[k+10]
            print 'Median house-hold rooms:\t', values_housing[k+11]
            print 'Utility gas:\t', values_housing[k+12]
            print 'Electricity:\t', values_housing[k+13]
            print 'Oil or kerosene:\t', values_housing[k+14]
            print 'Solar:\t', values_housing[k+15]
            print 'Other:\t', values_housing[k+16]
            print 'None:\t', values_housing[k+17]
            print '0-9%:\t', values_housing[k+18]
            print '10-19%:\t', values_housing[k+19]
            print '20-29%:\t', values_housing[k+20]
            print '30-39%:\t', values_housing[k+21]
            print '40-49%:\t', values_housing[k+22]
            print '50%+:\t', values_housing[k+23]
            print 'N/A:\t', values_housing[k+24]
            print 'Utilities extra:\t', values_housing[k+25]
            print 'Utilities included:\t', values_housing[k+26]
            break
    except:
        temp_value = [0]
        
if (len(boolean_housing) == 5):
    values_housing = values_housing + [0] * 27
    boolean_housing = boolean_housing + [0] * 27   


#%% Housing page

#print 'wait 2 sec'
time.sleep(2)
weather_page = urllib2.urlopen(weather_url)
weather_soup = BeautifulSoup(weather_page, 'lxml')
table_content = weather_soup.findAll(attrs = {'class':['table-overflow-container']})            


FeatureName = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
               'September', 'October', 'November', 'December']
offset_weather = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ,1 ,1]
boolean_weather = [0] * (len(FeatureName))
values_weather = [0] * (len(FeatureName))

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = temp_GST[j + offset_weather[k]].contents[0]
                        print FeatureName[k],'(min):\t', temp_value
                        boolean_weather[k] = 1
                        try:
                            values_weather[k] = float(Decimal(sub(r'[^\d.]', '', temp_value))) # deal with n/a
                        except:
                            boolean_weather[k] = 0
                break

offset_weather = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2 ,2 ,2]

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        try:
                            temp_value = temp_GST[j + offset_weather[k]].contents[0]                        
                            print FeatureName[k],'(max):\t', temp_value
                            boolean_weather = boolean_weather + [1]
                            values_weather = values_weather + [float(Decimal(sub(r'[^\d.]', '', temp_value)))] # deal with n/a
                        except:
                            boolean_weather = boolean_weather + [0]
                            values_weather = values_weather + [0]
                break


offset_weather = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3 ,3 ,3]

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        try:
                            temp_value = temp_GST[j + offset_weather[k]].contents[0]                        
                            print FeatureName[k],'(avg):\t', temp_value
                            boolean_weather = boolean_weather + [1]
                            values_weather = values_weather + [float(Decimal(sub(r'[^\d.]', '', temp_value)))] # deal with n/a
                        except:
                            boolean_weather = boolean_weather + [0]
                            values_weather = values_weather + [0]
                break
            
FeatureName = ['Air quality index', 'Pollution index', 'Days measured', 'Days with good air quality',
               'Days with moderate air quality', 'Days w/ poor A.Q. for sensitive groups',
               'Days with unhealthy air quality', 'Arsenic', 'Benzene', 'Carbon Tetrachloride',
               'Lead', 'Mercury']
offset_weather = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ,1 ,1]


for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:
                    if temp_GST[j].string == FeatureName[k]:
                        try:
                            temp_value = temp_GST[j + offset_weather[k]].contents[0]                        
                            print FeatureName[k],':\t', temp_value
                            boolean_weather = boolean_weather + [1]
                            values_weather = values_weather + [float(Decimal(sub(r'[^\d.]', '', temp_value)))] # deal with n/a
                        except:
                            boolean_weather = boolean_weather + [0]
                            values_weather = values_weather + [0]
                break          


#%% Demographics page

#print 'wait 2 sec'
time.sleep(2)
demographics_page = urllib2.urlopen(demographics_url)
demographics_soup = BeautifulSoup(demographics_page, 'lxml')
table_content = demographics_soup.findAll(attrs = {'class':['table-overflow-container']})



FeatureName = ['Population', 'Population density', 'Median age', 'Male/Female ratio', 'Married ', 
               'Speak English', 'Speak Spanish', 'Caucasian', 'African American', 'Asian', 
               'American Indian', 'Native Hawaiian', 'Mixed race', 'Other race']
offset_demographics = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ,1 , 1, 1, 1]
boolean_demographics = [0] * (len(FeatureName))
values_demographics = [0] * (len(FeatureName))

for i in [n for n in range(0,len(table_content))]:
    for k in [p for p in range(0,len(FeatureName))]:
        for temp_FeatureName in table_content[i].find_all("td"):
            if temp_FeatureName.string == FeatureName[k]:
                temp_GST = table_content[i].find_all("td")
                for j in [m for m in range(0,len(temp_GST))]:  
                    try:
                        temp_GST[j].small.extract()
                    except:
                        temp_value = [0] 
                    if temp_GST[j].string == FeatureName[k]:
                        temp_value = str(temp_GST[j + offset_demographics[k]].contents[0])
                        temp_value = temp_value.replace(':1', '')
                        print FeatureName[k],':\t', temp_value
                        boolean_demographics[k] = 1
                        try:
                            values_demographics[k] = float(Decimal(sub(r'[^\d.]', '', temp_value))) # deal with n/a
                        except:
                            boolean_demographics[k] = 0
                break

table_content = demographics_soup.findAll(attrs = {'class':['block-explain']})
try:
    temp_value = map(float, re.findall(r'\d+\.*\d*', str(table_content)))
    values_demographics = values_demographics + temp_value
    boolean_demographics = boolean_demographics + [1]
    print 'Hispanic or Latino origin: ',temp_value[0],'%'
except:
    values_demographics = values_demographics + [0]
    boolean_demographics = boolean_demographics + [0]

# find data of previous year  from figure
figure_content = demographics_soup.findAll(attrs = {'type':['text/javascript']})
k = len(values_demographics)
for yy in figure_content:
    yy_str = str(yy.string)
    try:    
        if 'lang_split' in yy_str:
#            print yy_str
            yy_str = yy_str.replace('$200K plus', '')
            yy_str = yy_str.replace('$150K-$200K', '')
            yy_str = yy_str.replace('$100K-$150K', '')
            yy_str = yy_str.replace('$60K-$100K', '')
            yy_str = yy_str.replace('$40K-$60K', '')
            yy_str = yy_str.replace('$25K-$40K', '')            
            yy_str = yy_str.replace('$10K-$25K', '')
            yy_str = yy_str.replace('$10K or less', '')
            yy_str = yy_str.replace('< 5', '')
            yy_str = yy_str.replace('5-14', '')
            yy_str = yy_str.replace('15-19', '')
            yy_str = yy_str.replace('20-24', '')
            yy_str = yy_str.replace('25-34', '')
            yy_str = yy_str.replace('35-44', '')
            yy_str = yy_str.replace('45-54', '')
            yy_str = yy_str.replace('55-64', '')    
            yy_str = yy_str.replace('65-84', '') 
            yy_str = yy_str.replace('84 >', '') 
            yy_str = yy_str.replace('Younger than 6 only', '') 
            yy_str = yy_str.replace('Both younger than 6', '') 
            yy_str = yy_str.replace('between 6 and 17', '')
            yy_str = yy_str.replace('6 to 17 only', '') 
#            print yy_str
            temp_value = map(float, re.findall(r'\d+\.*\d*', yy_str))
#            print temp_value
            values_demographics = values_demographics + temp_value
            boolean_demographics = boolean_demographics + [1] * 56
            print 'Speak English:\t', values_demographics[k+0]
            print 'Speak Spanish:\t', values_demographics[k+1]
            print 'Other:\t', values_demographics[k+2]
            print 'In state of res:\t', values_demographics[k+3]
            print 'Out of state:\t', values_demographics[k+4]
            print 'Out of US:\t', values_demographics[k+5]
            print 'Foreign:\t', values_demographics[k+6]
            print '$200K plus:\t', values_demographics[k+7]
            print '$150K-$200K:\t', values_demographics[k+8]
            print '$100K-$150K:\t', values_demographics[k+9]
            print '$60K-$100K:\t', values_demographics[k+10]
            print '$40K-$60K:\t', values_demographics[k+11]
            print '$25K-$40K:\t', values_demographics[k+12]
            print '$10K-$25K:\t', values_demographics[k+13]
            print '$10K or less:\t', values_demographics[k+14]
            print 'Salary:\t', values_demographics[k+15]
            print 'Self Emp.:\t', values_demographics[k+16]
            print 'Investments:\t', values_demographics[k+17]
            print 'Social Sec.:\t', values_demographics[k+18]
            print 'Supplmental Sec.:\t', values_demographics[k+19]
            print 'Public Asst.:\t', values_demographics[k+20]
            print 'Retirment Inc.:\t', values_demographics[k+21]
            print 'Other:\t', values_demographics[k+22]
            print '<5 (Male):\t', values_demographics[k+23]
            print '5 - 14 (Male):\t', values_demographics[k+24]
            print '15 - 19 (Male):\t', values_demographics[k+25]
            print '20 - 24 (Male):\t', values_demographics[k+26]
            print '25 - 34 (Male):\t', values_demographics[k+27]
            print '35 - 44 (Male):\t', values_demographics[k+28]
            print '45 - 54 (Male):\t', values_demographics[k+29]
            print '55 - 64 (Male):\t', values_demographics[k+30]
            print '65 - 84 (Male):\t', values_demographics[k+31]
            print '> 85 (Male):\t', values_demographics[k+32]
            print '<5 (Female):\t', values_demographics[k+33]
            print '5 - 14 (Female):\t', values_demographics[k+34]
            print '15 - 19 (Female):\t', values_demographics[k+35]
            print '20 - 24 (Female):\t', values_demographics[k+36]
            print '25 - 34 (Female):\t', values_demographics[k+37]
            print '35 - 44 (Female):\t', values_demographics[k+38]
            print '45 - 54 (Female):\t', values_demographics[k+39]
            print '55 - 64 (Female):\t', values_demographics[k+40]
            print '65 - 84 (Female):\t', values_demographics[k+41]
            print '>85 (Female):\t', values_demographics[k+42]
            print 'Never (Male):\t', values_demographics[k+43]
            print 'Married (Male):\t', values_demographics[k+44]
            print 'Separated (Male):\t', values_demographics[k+45]
            print 'Divorced (Male):\t', values_demographics[k+46]
            print 'Widowed (Male):\t', values_demographics[k+47]
            print 'Never (Female):\t', values_demographics[k+48]
            print 'Married (Female):\t', values_demographics[k+49]
            print 'Separated (Female):\t', values_demographics[k+50]
            print 'Divorced (Female):\t', values_demographics[k+51]
            print 'Widowed (Female):\t', values_demographics[k+52]
            print 'Younger than 6 only:\t', values_demographics[k+53]
            print 'Both younger than 6 & between 6 and 17:\t', values_demographics[k+54]
            print '6 to 17 only:\t', values_demographics[k+55]
            break
    except:
        temp_value = [0]
        
if (len(boolean_demographics) == 15):
    values_demographics = values_demographics + [0] * 56
    boolean_demographics = boolean_demographics + [0] * 56   

boolean_total = boolean_cost_of_living + boolean_crime + boolean_demographics + boolean_education + boolean_employment + boolean_housing + boolean_weather
values_total = values_cost_of_living + values_crime + values_demographics + values_education + values_employment + values_housing + values_weather
final = boolean_total + values_total

f=open('crawl_areavibes_result.txt', 'w')
f.write(str(final))
f=open('crawl_areavibes_result.txt', 'r')