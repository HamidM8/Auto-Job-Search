import sys
from os import path
from lxml import html, etree
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.request
import re
from urllib.parse import urljoin
import time  # instead of usiing User agent we can make pauses in clicks. here we use both
import tkinter as tk
from tkinter import StringVar  # this is for variables StringVar() to get the path in string
from tkinter import ttk     ## ttk is the Python binding to the newer "themed widgets" added in Tk version 8.5
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import *   # for defining style
from PIL import Image, ImageTk  #for images
import xlsxwriter
from urllib.request import Request, urlopen
from datetime import datetime
from time import sleep

try:                        #(this for Win10 thats why its mentioned as try - to avoid errors in Linux,Mac,etc.)
   from ctypes import windll     #this part is maximazing pixels in texts 
   windll.shcore.SetProcessDpiAwareness(1)
except:
   pass


now = datetime.now()
time_now = now.strftime("%H%M")   #syntax   now.strftime("%m/%d/%Y, %H:%M:%S")
date_today = now.strftime("%m.%d.%Y")
Format_date = str(date_today + "-" + time_now)



columns = ['Company','Job','Location', 'Link'] 
dfIndeed = pd.DataFrame(columns=columns)
dfMonster = pd.DataFrame(columns=columns)
dfPracuj = pd.DataFrame(columns=columns)
dfJobs = pd.DataFrame(columns=columns)


def SaveExcelFile():
    global dfIndeed, dfMonster, dfPracuj, dfJobs, Format_date

    columns = ['Company','Job','Location', 'Link']   
    df = pd.DataFrame(columns=columns)
 
    OutputFileName =  f'{txtKeyword.get()}'+ '_'+f'{txtCity.get()}'+f'({Format_date})'
    writer = pd.ExcelWriter(f'{OutputFileName}.xlsx')

    if CheckIndeedVar.get()==1:
        dfIndeed.to_excel(writer,'Indeed.com',index=False)
        writer.sheets['Indeed.com'].set_column('A:D',40)
    if CheckMonsterVar.get()==1:
        dfMonster.to_excel(writer,'Monster.com',index=False)
        writer.sheets['Monster.com'].set_column('A:D',40)
    if CheckPracujVar.get()==1:
        dfPracuj.to_excel(writer,'Pracuj.pl',index=False)
        writer.sheets['Pracuj.pl'].set_column('A:D',40)
    if CheckJobsVar.get()==1:
        dfJobs.to_excel(writer,'Jobs.cz',index=False)
        writer.sheets['Jobs.cz'].set_column('A:D',40)

    writer.save()
    messagebox.showinfo("Success Message","Excel file has been saved.")


class CustomText(tk.Text):

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def HighlightPattern(self, pattern, tag, start="1.0", end="end", regexp=True):
        '''Apply the given tag to all text that matches the given pattern'''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart",start)
        self.mark_set("matchEnd",end)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",count=count, regexp=regexp)
            if index == "": break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index,count.get()))
            self.tag_add(tag, "matchStart","matchEnd")


def getFolderPath():
    global folderPath
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


def clicked(*args):

    global dfIndeed, dfMonster, dfPracuj, dfJobs, engine_num_chosen 

    # creating new df 
    columns = ['Company','Job','Location', 'Link'] 
    dfIndeed = pd.DataFrame(columns=columns)
    dfMonster = pd.DataFrame(columns=columns)
    dfPracuj = pd.DataFrame(columns=columns)
    dfJobs = pd.DataFrame(columns=columns)

    #engine_num_chosen = 0

    ans = messagebox.askokcancel("Verify", "Start searching?")
    if CheckPracujVar.get()==1 and (CheckIndeedVar.get()==1 or CheckMonsterVar.get()==1 or CheckJobsVar.get()==1):
            messagebox.showinfo("Error", "The chosen Web Engines are for searching in different countries.\
                \nPlease choose only those engines that are compatible.")
            raise Exception("These Web Engines support search in different countries") 
    elif CheckJobsVar.get()==1 and (CheckIndeedVar.get()==1 or CheckMonsterVar.get()==1 or CheckPracujVar.get()==1):
            messagebox.showinfo("Error", "The chosen Web Engines are for searching in different countries.\
                \nPlease choose only those engines that are compatible.")
            raise Exception("These Web Engines support search in different countries")     
    
    if ans == 1:        
        if CheckIndeedVar.get()==1:
            StartIndeedUS()
        if CheckMonsterVar.get()==1:
            StartMonsterUS()
        if CheckPracujVar.get()==1:
            txtState.set("<<No Entry Required>>")
            StartPracuj()
        if CheckJobsVar.get()==1:
            txtState.set("<<No Entry Required>>")
            StartJobsCZ()
        SaveExcelFile()

    if CheckIndeedVar.get()==0 and CheckMonsterVar.get()==0 and CheckPracujVar.get()==0 and CheckJobsVar.get()==0: # CheckLinkedInVar.get()==1
            messagebox.showinfo("Error", "No WEB Engine has been Chosen")
            raise Exception("No WEB Engine has been Chosen")
    


def CheckFolderPath():
    if (folderPath.get() == ""):
        messagebox.showinfo("Error:","Please choose folder for output file")
        raise Exception("No folder was chosen")        
    else:
        os.chdir(os.path.abspath(folderPath.get())) # format 'c:\\Users\\hamid\\ ... 


def CheckEntryParameters():
    global job, city, state_code_indeed, state_code_monster

    if str(txtKeyword.get())=="":
        messagebox.showinfo("Warning", "Please enter job/keyword")
        raise Exception("Position or keywords was not entered")
    else: 
        job = str(txtKeyword.get())
        job = job.lower()

    
    if str(txtCity.get())== ("" or " " or "  " or "   "):
        messagebox.showinfo("Warning", "Please enter City")
        raise Exception("City was not entered")
    else: 
        city = str(txtCity.get())

    state = str(txtState.get())
    city = city.lower()
    
    if CheckIndeedVar.get()==1 or CheckMonsterVar.get()==1:
        # State must be valid two letter code - for US only
        st = state.strip()
        if len(st) == 0:
            state_code_indeed = ""
            state_code_monster = ""
        elif len(st) !=2:
            messagebox.showinfo("Error", "State must be two letters or must be empty")
            raise Exception("State must be two letters or must be empty")
        else:
            st = st.upper()
            state_code_indeed = "%2C+"+st   
            state_code_monster ="__2C-"+st


def StartIndeedUS():
    global job, city, state_code_indeed , dfIndeed
    Progress_Bar_Percent = StringVar()
    Progress_Bar_Percent.set("Progress 0 %")
    CheckFolderPath()
    CheckEntryParameters()

    job = '+'.join(job.split(" "))
    city = '+'.join(city.split(" "))

    IndeedPages = [0]  #at the end of function return back the values
    Add_Ind_Pages = []   #at the end of function return back the values
    #IndeedPages = [0, 10, 20, 30, 40, 50, 60, 70]  #format for this website
    if (Page_Values.get()==1):
        Add_Ind_Pages = []
    if (Page_Values.get()==2):
        Add_Ind_Pages = [10]
    elif (Page_Values.get()==3):
        Add_Ind_Pages = [10, 20]
    elif (Page_Values.get()==4):
        Add_Ind_Pages = [10, 20, 30]   
    elif (Page_Values.get()==5):
        Add_Ind_Pages = [10, 20, 30, 40]
    elif (Page_Values.get()==6):
        Add_Ind_Pages = [10, 20, 30, 40, 50]
    elif (Page_Values.get()==7):
        Add_Ind_Pages = [10, 20, 30, 40, 50, 60]
    elif (Page_Values.get()==8):
        Add_Ind_Pages = [10, 20, 30, 40, 50, 60, 70]
    else:
        Add_Ind_Pages = []
    
    IndeedPages += Add_Ind_Pages

    columns = ['Company','Job','Location', 'Link']   
    dfIndeed = pd.DataFrame(columns=columns) #for columns 
    companiesName, jobsTitle, locationName, jobsLink = [], [], [], []    
    URL = str(f"https://www.indeed.com/jobs?q={job}&l={city}{state_code_indeed}&start=")
    home = 'https://www.indeed.com/viewjob?'
    
    ### Progress Bar 
    x = gui.winfo_x()
    y = gui.winfo_y()
    popup_bar=tk.Toplevel()    
    popup_bar.geometry("+%d+%d" % (x + 420, y + 300))     
    tk.Label(popup_bar, text="Searching in Indeed.com ... ").grid(row=0, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")     
    progress=0
    progress_var = tk.DoubleVar()
    
    progress_bar = ttk.Progressbar(popup_bar, variable = progress_var, style="green.Horizontal.TProgressbar", maximum=100)
    progress_bar.grid(row=21, column=0, columnspan= 150,rowspan=20, sticky ="NWE")  
    tk.Label(popup_bar, textvariable=Progress_Bar_Percent).grid(row=41, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")

    
    ## setting fixed grid size for bar
    col_count, row_count = popup_bar.grid_size()
    for col in range(col_count):
        popup_bar.grid_columnconfigure(col, minsize=1)
    
    for row in range(row_count):
        popup_bar.grid_rowconfigure(row, minsize=1)   
   
    
    
    popup_bar.pack_slaves()

    ## bar var calc
    progress_step = float(100.0/len(IndeedPages))



    for IndeedPage in IndeedPages:
        popup_bar.update()  # bar

        URL1 = str(URL)+str(IndeedPage)
        print(URL1)
        req = Request(URL1, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        
        web_url = urlopen(req).read()
        soup = BeautifulSoup(web_url, 'html.parser')
        print(URL1)

        results = soup.find_all('div', attrs={'data-tn-component': 'organicJob'})
    
        for x in results:   
            columns1 = ['Company','Job','Location', 'Link']   
            df1 = pd.DataFrame(columns=columns1) #for columns we will pass columns variable  
            company = x.find('span', attrs={"class":"company"}).text.strip()
            companiesName.append(company)
            job = x.find('a', attrs={'data-tn-element': "jobTitle"}).text.strip()
            jobsTitle.append(job)     
            try:
                location = x.find('span', attrs={"class":"location"}).text.strip()
                locationName.append(location)
            except AttributeError as e:
                messagebox.showinfo("Error:","Wrong City was entered for this Web Engine.")
                return
            job_link = urljoin(home, x.find('a').get('href'))
            jobsLink.append(job_link)
            df1 = df1.append({'Company': company,'Job': job, 'Location': location, 'Link': job_link}, ignore_index=True)
            dfIndeed = pd.concat([dfIndeed, df1]).drop_duplicates('Link').reset_index(drop=True)
            print(URL1)
            print(df1)

        
        progress +=progress_step
        progress_var.set(progress)
        print(progress)  # valid
        Progress_Bar_Percent.set("Progress " + str("%.0f" % progress)+" %")
        popup_bar.update()  # bar
        time.sleep(0.1)
    
        print(IndeedPage)
        time.sleep (5) # 5 seconds
    popup_bar.destroy()
    print("Search in Indeed.com engine is done. Click on OK to proceed further.")


def StartMonsterUS():
    global job, city, state_code_monster, dfMonster 

    Progress_Bar_Percent = StringVar()
    Progress_Bar_Percent.set("Progress 0 %")

    CheckFolderPath()
    CheckEntryParameters()


    job = '-'.join(job.split(" "))
    city = '-'.join(city.split(" "))

    #Working on Pages
    MonsterPages = [0]  #at the end of function return back the values
    Add_Monster_Pages = []   #at the end of function return back the values
    #MonsterPages = [0, 2, 3, 4, 5, 6, 7, 8]  # format
    if (Page_Values.get()==1):
        Add_Monster_Pages = []
    if (Page_Values.get()==2):
        Add_Monster_Pages = [2]
    elif (Page_Values.get()==3):
        Add_Monster_Pages = [2, 3]
    elif (Page_Values.get()==4):
        Add_Monster_Pages = [2, 3, 4]   
    elif (Page_Values.get()==5):
        Add_Monster_Pages = [2, 3, 4, 5]
    elif (Page_Values.get()==6):
        Add_Monster_Pages = [2, 3, 4, 5, 6]
    elif (Page_Values.get()==7):
        Add_Monster_Pages = [2, 3, 4, 5, 6, 7]
    elif (Page_Values.get()==8):
        Add_Monster_Pages = [2, 3, 4, 5, 6, 7, 8]
    else:
        Add_Monster_Pages = []

    
    MonsterPages += Add_Monster_Pages
   
    columns = ['Company','Job','Location', 'Link']   
    dfMonster = pd.DataFrame(columns=columns) #for columns 
    companiesName, jobsTitle, locationName, jobsLink = [], [], [], []    
    URL = str(f"https://www.monster.com/jobs/search/?q={job}&where={city}{state_code_monster}&stpage=1&page=")

    home = ''

    ### Progress Bar 
    x = gui.winfo_x()
    y = gui.winfo_y()
    popup_bar=tk.Toplevel()    
    popup_bar.geometry("+%d+%d" % (x + 420, y + 300))     
    tk.Label(popup_bar, text="Searching in Monster.com ... ").grid(row=0, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")     

    progress=0
    progress_var = tk.DoubleVar()

    progress_bar = ttk.Progressbar(popup_bar, variable = progress_var, style="green.Horizontal.TProgressbar", maximum=100)
    progress_bar.grid(row=21, column=0, columnspan= 150,rowspan=20, sticky ="NWE")  
    tk.Label(popup_bar, textvariable=Progress_Bar_Percent).grid(row=41, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")  

    ## setting grid size for bar
    col_count, row_count = popup_bar.grid_size()
    for col in range(col_count):
        popup_bar.grid_columnconfigure(col, minsize=1)
    
    for row in range(row_count):
        popup_bar.grid_rowconfigure(row, minsize=1)   
    popup_bar.pack_slaves()


    progress_step = float(100.0/len(MonsterPages))



    for MonsterPage in MonsterPages:

        popup_bar.update()  # bar


        URL1 = str(URL)+str(MonsterPage)
        print(URL1)
        req = Request(URL1, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        
        web_url = urlopen(req).read()
        soup = BeautifulSoup(web_url, 'html.parser')
        print(URL1)
        results = soup.find_all('div', attrs={'class': 'flex-row'})
    
        for x in results:   
            columns1 = ['Company','Job','Location', 'Link']   
            df1 = pd.DataFrame(columns=columns1) #for columns 
            try:
                company = x.find('div', attrs={"class":"company"}).text.strip()
                companiesName.append(company)
            except AttributeError as e:
                messagebox.showinfo("Error:","Wrong City was entered for this Web Engine.")
                return
            job = x.find('h2', attrs={'class': "title"}).text.strip()
            jobsTitle.append(job)
            location = x.find('div', attrs={"class":"location"}).text.strip()
            locationName.append(location)
            job_link = urljoin(home, x.find('a').get('href'))
            jobsLink.append(job_link)
            df1 = df1.append({'Company': company,'Job': job, 'Location': location, 'Link': job_link}, ignore_index=True)
            dfMonster = pd.concat([dfMonster, df1]).drop_duplicates('Link').reset_index(drop=True)
            print(URL1)
            print(df1)
       
        progress +=progress_step
        progress_var.set(progress)
        print(progress)  # valid
        Progress_Bar_Percent.set("Progress " + str("%.0f" % progress)+" %")
        popup_bar.update()  # bar
        time.sleep(0.1)
        

        print(MonsterPage)
        time.sleep (5) # 5 seconds 
    
    popup_bar.destroy()
    print("Search in Monster.com engine is done. Click on OK to proceed further.")


def StartPracuj():

    global job, city, dfPracuj

    #State_Rem_Space = txtState.get()+"777"
    #State_Rem_Space.replace(" ", "")
    #State_Rem_Space.strip()
    #Space_removed=State_Rem_Space    
    #if len((txtState.get())) != 0:
    #    messagebox.showinfo("Error", "Search Engine for Poland doesnt support State Codes.\
    #        \nPlease make sure that there is.")
    #    raise Exception("Search Engine for Poland doesnt support State Codes.")

    Progress_Bar_Percent = StringVar()
    Progress_Bar_Percent.set("Progress 0 %")

    CheckFolderPath()
    CheckEntryParameters()
    
    job = '%20'.join(job.split(" "))
    city = '%20'.join(city.split(" "))
 
    PracujPages = [0]  
    Add_Pracuj_Pages = []   
    #PracujPages = [0, 2, 3, 4, 5, 6, 7, 8] # format
    if (Page_Values.get()==1):
        Add_Pracuj_Pages = []
    if (Page_Values.get()==2):
        Add_Pracuj_Pages = [2]
    elif (Page_Values.get()==3):
        Add_Pracuj_Pages = [2, 3]
    elif (Page_Values.get()==4):
        Add_Pracuj_Pages = [2, 3, 4]   
    elif (Page_Values.get()==5):
        Add_Pracuj_Pages = [2, 3, 4, 5]
    elif (Page_Values.get()==6):
        Add_Pracuj_Pages = [2, 3, 4, 5, 6]
    elif (Page_Values.get()==7):
        Add_Pracuj_Pages = [2, 3, 4, 5, 6, 7]
    elif (Page_Values.get()==8):
        Add_Pracuj_Pages = [2, 3, 4, 5, 6, 7, 8]
    else:
        Add_Pracuj_Pages = []
  
    PracujPages += Add_Pracuj_Pages
     
    columns = ['Company','Job','Location', 'Link']   
    companiesName, jobsTitle, locationName, jobsLink = [], [], [], []    
    URL = str(f"https://www.pracuj.pl/praca/{job};kw/{city};wp?rd=30&pn=")
    #https://www.pracuj.pl/praca/customer%20service;kw/krakow;wp?rd=30&pn=2

    home = ''

    ### Progress Bar 
    x = gui.winfo_x()
    y = gui.winfo_y()
    popup_bar=tk.Toplevel()    
    popup_bar.geometry("+%d+%d" % (x + 420, y + 300))     
    tk.Label(popup_bar, text="Searching in Pracuj.pl ... ").grid(row=0, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")     
    progress=0
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(popup_bar, variable = progress_var, style="green.Horizontal.TProgressbar", maximum=100)
    progress_bar.grid(row=21, column=0, columnspan= 150,rowspan=20, sticky ="NWE")  
    tk.Label(popup_bar, textvariable=Progress_Bar_Percent).grid(row=41, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")

    ##settting grid size for bar
    col_count, row_count = popup_bar.grid_size()
    for col in range(col_count):
        popup_bar.grid_columnconfigure(col, minsize=1)
    
    for row in range(row_count):
        popup_bar.grid_rowconfigure(row, minsize=1)   
    popup_bar.pack_slaves()

    progress_step = float(100.0/len(PracujPages))



    for PracujPage in PracujPages:

        popup_bar.update()  # bar


        URL1 = str(URL)+str(PracujPage)
        print(URL1)
        req = Request(URL1, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        
        web_url = urlopen(req).read()
        soup = BeautifulSoup(web_url, 'html.parser')
        print(URL1)
        results = soup.find_all('div', attrs={'class': 'offer'})
    
        for x in results:   
            columns1 = ['Company','Job','Location', 'Link']   
            df1 = pd.DataFrame(columns=columns1) #for columns 
            company = x.find('span', attrs={"class":"offer-company__wrapper"}).text.strip()
            companiesName.append(company)
            job = x.find('h3', attrs={'class': "offer-details__title"}).text.strip()
            jobsTitle.append(job)
            location = x.find('li', attrs={"class":"offer-labels__item offer-labels__item--location"}).text.strip()
            locationName.append(location)
            job_link = urljoin(home, x.find('a').get('href'))
            jobsLink.append(job_link)
            df1 = df1.append({'Company': company,'Job': job, 'Location': location, 'Link': job_link}, ignore_index=True)
            dfPracuj = pd.concat([dfPracuj, df1]).drop_duplicates('Link').reset_index(drop=True)
            print(URL1)
            print(df1)

        progress +=progress_step
        progress_var.set(progress)
        print(progress)  # valid
        Progress_Bar_Percent.set("Progress " + str("%.0f" % progress)+" %")
        popup_bar.update()  # bar
        time.sleep(0.1)
    
        print(PracujPage)
        time.sleep (5) # 5 seconds 

    popup_bar.destroy()
    print("Search in Pracuj.pl engine is done. Click on OK to proceed further.")


def StartJobsCZ():
    global job, city, dfJobs

    #if str(txtState.get()) !="":
    #    messagebox.showinfo("Error", "Search Engine for Czech Republic doesnt support State Codes.\
    #        \nPlease remove the state code.")
    #    raise Exception("Search Engine for Czech Republic doesnt support State Codes.")

    Progress_Bar_Percent = StringVar()
    Progress_Bar_Percent.set("Progress 0 %")

    CheckFolderPath()
    CheckEntryParameters()


       
    job = '%20'.join(job.split(" "))
    city = '-'.join(city.split(" "))
    
    #Working on Pages
    JobsCZPages = [1]  
    Add_JobsCZ_Pages = []   
    if (Page_Values.get()==1):
        Add_JobsCZ_Pages = []
    if (Page_Values.get()==2):
        Add_JobsCZ_Pages = [2]
    elif (Page_Values.get()==3):
        Add_JobsCZ_Pages = [2, 3]
    elif (Page_Values.get()==4):
        Add_JobsCZ_Pages = [2, 3, 4]   
    elif (Page_Values.get()==5):
        Add_JobsCZ_Pages = [2, 3, 4, 5]
    elif (Page_Values.get()==6):
        Add_JobsCZ_Pages = [2, 3, 4, 5, 6]
    elif (Page_Values.get()==7):
        Add_JobsCZ_Pages = [2, 3, 4, 5, 6, 7]
    elif (Page_Values.get()==8):
        Add_JobsCZ_Pages = [2, 3, 4, 5, 6, 7, 8]
    else:
        Add_JobsCZ_Pages = []
    
    
    JobsCZPages += Add_JobsCZ_Pages

    columns = ['Company','Job','Location', 'Link']   
    dfJobs = pd.DataFrame(columns=columns) #for columns  
    companiesName, jobsTitle, locationName, jobsLink = [], [], [], [] 
    URL = str(f"https://www.jobs.cz/prace/{city}/?q%5B%5D={job}&page=")

    home = ''


    ### Progress Bar 
    x = gui.winfo_x()
    y = gui.winfo_y()
    popup_bar=tk.Toplevel()    
    popup_bar.geometry("+%d+%d" % (x + 420, y + 300))     
    tk.Label(popup_bar, text="Searching in Jobs.cz ... ").grid(row=0, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE")     
    progress=0
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(popup_bar, variable = progress_var, style="green.Horizontal.TProgressbar", maximum=100)
    progress_bar.grid(row=21, column=0, columnspan= 150,rowspan=20, sticky ="NWE")  
    tk.Label(popup_bar, textvariable=Progress_Bar_Percent).grid(row=41, column=0, columnspan= 150,rowspan=20, ipadx=5, ipady=5, sticky ="NWE") 

    
    col_count, row_count = popup_bar.grid_size()
    for col in range(col_count):
        popup_bar.grid_columnconfigure(col, minsize=1)
    
    for row in range(row_count):
        popup_bar.grid_rowconfigure(row, minsize=1)   
    popup_bar.pack_slaves()

    progress_step = float(100.0/len(JobsCZPages))


    i=0   # for differintiate exceeding number of pages from wrong entered city

    for JobsCZPage in JobsCZPages:

        i+=1
        popup_bar.update()  # bar

        URL1 = str(URL)+str(JobsCZPage)
        print(URL1)
        req = Request(URL1, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
        print(f"Jobs.cz page in progress {i}")

        try: 
            web_url = urlopen(req).read()
            print(web_url)
            print(URL1)
        except Exception as e:
            if i==1:
                popup_bar.destroy()
                messagebox.showinfo("Error", "Please make sure that you enter correct city (in Czech lang) and job title.")
                raise Exception("Please make sure that you enter correct city (in Czech lang) and job title.")
            else:
                progress_var.set(100)
                Progress_Bar_Percent.set("Progress 100 %")
                popup_bar.update() 
                time.sleep(1)
                popup_bar.destroy()
                print("There is no such number of pages for entered parameters!") 
                break

        soup = BeautifulSoup(web_url, 'html.parser')
        print(URL1)
        results = soup.find_all('div', attrs={'class': 'grid__item e-17--desk'})
    
        for x in results:   
            columns1 = ['Company','Job','Location',  'Link']   
            df1 = pd.DataFrame(columns=columns1) #for columns   
            company = x.find('div', attrs={"class":"search-list__main-info__company"}).text.strip()
            companiesName.append(company)
            job = x.find('a', attrs={'class': "search-list__main-info__title__link"}).text.strip()
            jobsTitle.append(job)
            location_long = x.find('div', attrs={"class":"search-list__main-info__address"}).text.strip()
            location = str(location_long)
            location = ' '.join(location.split('Adresa\n                                            '))
            locationName.append(location)
            job_link = urljoin(home, x.find('a').get('href'))
            jobsLink.append(job_link)
            df1 = df1.append({'Company': company,'Job': job, 'Location': location, 'Link': job_link}, ignore_index=True)
            dfJobs = pd.concat([dfJobs, df1]).drop_duplicates('Link').reset_index(drop=True)
            print(URL1)
            print(df1)

        progress +=progress_step
        progress_var.set(progress)
        print(progress)  # valid
        Progress_Bar_Percent.set("Progress " + str("%.0f" % progress)+" %")
        popup_bar.update()  # bar
        time.sleep(0.1)
            
        print(JobsCZPage)
        time.sleep (5) # 5 seconds break 

    popup_bar.destroy()
    print("Search in Jobs.cz engine is done. Click on OK to proceed further.")



def aboutF():
    x = gui.winfo_x()
    y = gui.winfo_y()
    menu_hel = tk.Toplevel()   #Attribute Toplevel for help menu  
    menu_hel.geometry("+%d+%d" % (x + 190, y + 220))  
    menu_hel.geometry("700x500")
    menu_hel.resizable(False, False)

    menu_hel.title("Info")
    about = "Application: Job Auto Search | Scrapping data of job postings from reputable job search portals. \
You can search in several websites in once (the chosen Web Engines should support the entered location entry) \
and get results in output excel file. \
\n \
\nDisclaimer: For the time when this App was created there were no restrictions for scrapping data in the given websites. \
However, please be informed that situation might change and it might become against of some of the websites' User Agreement. \
Anyway, please be informed that this project is only intended for educational purposes. \
\n \
\nPython code for this app, as well as the application itself  can be accessed on https://github.com/HamidM8."


    t=CustomText(menu_hel, wrap="word", width=80, height=13, borderwidth=0)
    t.tag_configure("red", foreground="red")
    t.pack(sid="top",fill="both",expand=True)
    t.insert("1.0", about)
    t.HighlightPattern("^.*? - ", "blue")
    tk.Button(menu_hel, text='CLOSE', command=menu_hel.destroy, bg='gray', fg='black').pack(sid="bottom")


def QuitApp_OpenFolder():
    if (folderPath.get()==""):
        messagebox.showinfo("Error:","No folder has been chosen! ")  
        return
    else:    
        try: 
            os.startfile(os.path.abspath(folderPath.get())) 
            gui.destroy()
        except NameError as e:
            messagebox.showinfo("Error:","No folder has been chosen! ")
            return


def Quit_Button():
    ans = messagebox.askokcancel("Confirm close", "Are you sure you want to quit? ")
    if ans == 1: 
        gui.destroy()
    else:
        pass


gui = tk.Tk()


txtKeyword = tk.StringVar(gui, value = 'SAP')
txtCity = tk.StringVar(gui, value = 'Buffalo')
txtState = tk.StringVar(gui, value = 'NY')
folderPath = StringVar()
CheckIndeedVar = tk.IntVar()
CheckMonsterVar = tk.IntVar()
CheckPracujVar = tk.IntVar()
CheckJobsVar = tk.IntVar()
#Progress_Bar_Percent = StringVar()


Web_Pages = [0,1,2,3,4,5,6,7,8]
Page_Values = tk.IntVar(value=Web_Pages)
Page_Values.set(Web_Pages[1])



gui.geometry("1200x800")
gui.title("Auto Job Search by Hamid.M")
gui.minsize(1200, 800)
#gui.resizable(False, False)
gui.columnconfigure((0,999), weight=1)
gui.rowconfigure((0,599), weight=1)

### Styles
s = ttk.Style()
s.theme_use("clam")
s.configure('BL.TFrame', background='khaki4', fg="black")
s.configure('DarkGray.TFrame', background='ivory3', fg="white")
s.configure('Line.TSeparator', background='black')
s.configure('MY.TCheckbutton', background='khaki4', foreground="Gray15", font='Calibri 11 bold')

s.configure('CustomButton.TButton',background='gray',
        foreground='black',
        #highlightthickness='20',
        font=('Calibri', 11))  #font=('Helvetica', 11, 'bold'))
s.map("CustomButton.TButton", foreground=[("pressed", "black"), ("active", "black")],
background=[ ("pressed","!disabled","dim gray"),("active", "azure3")],
font=[("pressed",("Calibri", 11, 'bold'))])


s.configure('CustomButton2.TButton',background='gray',
        foreground='black',
        #highlightthickness='20',
        font=('Calibri', 8), width=5, height=2)  #font=('Helvetica', 11, 'bold'))
s.map("CustomButton2.TButton", foreground=[("pressed", "black"), ("active", "black")],
background=[ ("pressed","!disabled","dim gray"),("active", "azure3")],
font=[("pressed",("Calibri", 8))])

s.configure("green.Horizontal.TProgressbar", foreground='green2', background='green2')


### Frames
left_frame=ttk.Frame(gui, style='BL.TFrame', width=300,height=600).grid(row=0,rowspan=601,columnspan=300,column=0, sticky="NSWE")
up_right_frame=ttk.Frame(gui, style='DarkGray.TFrame', width=700,height=600).grid(row=0,rowspan=601, columnspan=701, column=300, sticky="NSWE")
ttk.Separator(gui, orient="horizontal", style='Line.TSeparator').grid(row=410, column=300, columnspan=700, sticky="NSWE")


#######     -     left_Frame  0;0 / 599;299
##Image logo
#"C:\\Users\\hamid\\AppData\\Local\\Programs\\Python\\Python38\\Scripts\\Mahho_Scripts\\Proj_AUTO_JOB_SEARCH\\Assets\\logo_AJS.PNG"
try:
    bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
    print(bundle_dir)
    path_to_logo = path.join(bundle_dir, "assets", "logo_AJS.PNG")
    print(path_to_logo)
    image=Image.open(path_to_logo).resize((240,180))
    photo = ImageTk.PhotoImage(image)
    photo_label = ttk.Label(left_frame, image=photo, background="khaki4").grid(row=20, column=30, rowspan=180,columnspan=240, padx=0, pady=0, sticky="NSWE")
except Exception:
    pass


##RadioButtons- WEB Engines
tk.Label(up_right_frame,text="WEB Engines*:",bg='khaki4', fg='Gray15', font='Calibri 11 bold').grid(row=300, column=40, columnspan = 200, sticky="NW")
C1 = Checkbutton(left_frame, style ='MY.TCheckbutton', text = "Indeed.com (US)", variable = CheckIndeedVar, \
                 onvalue = 1, offvalue = 0).grid(row=310, column=40,columnspan = 200, sticky="NSWE")
C1 = Checkbutton(left_frame, style ='MY.TCheckbutton', text = "Monster.com (US)", variable = CheckMonsterVar, \
                 onvalue = 1, offvalue = 0).grid(row=320, column=40,columnspan = 200, sticky="NSWE")
C1 = Checkbutton(left_frame, style ='MY.TCheckbutton', text = "Pracuj.pl (PL)", variable = CheckPracujVar, \
                 onvalue = 1, offvalue = 0).grid(row=330, column=40,columnspan = 200, sticky="NSWE")
C1 = Checkbutton(left_frame, style ='MY.TCheckbutton', text = "Jobs.cz (CZ)", variable = CheckJobsVar, \
                 onvalue = 1, offvalue = 0).grid(row=340, column=40,columnspan = 200, sticky="NSWE")


########      -      up_right frame 
Help_button = ttk.Button(up_right_frame, text="Info", command=aboutF, style = "CustomButton2.TButton").grid(row=10,column=600,columnspan=30,rowspan=30, sticky="NE")
tk.Label(up_right_frame,text="",bg='ivory3', fg='black',font='calibri 11').grid(row=10,column=631, columnspan=20, rowspan=30, sticky="NE")
tk.Label(up_right_frame,text="Enter Job Position or Keyword*:",bg='ivory3', fg='black',font='calibri 11').grid(row=145,column=320, columnspan=100, rowspan=58, sticky="W")
tk.Label(up_right_frame,text="Enter City*:",bg='ivory3', fg='black',font='Calibri 11 ').grid(row=175,column=320, columnspan=100, rowspan=58, sticky="W")
tk.Label(up_right_frame,text="Enter Correct State Code (US only):",bg='ivory3', fg='black',font='Calibri 11 ').grid(row=205,column=320, columnspan=100, rowspan=58, sticky="W")
tk.Label(up_right_frame,text="",bg='ivory3', fg='black',font='Calibri 11 ').grid(row=235,column=320, columnspan=100, rowspan=58, sticky="W")
tk.Label(up_right_frame,text="Number of Web Pages:",bg='ivory3', fg='black',font='Calibri 11 ').grid(row=245,column=320, columnspan=58, rowspan=60, sticky="W")

Keyword_Entry = Entry(up_right_frame, textvariable=txtKeyword)
Keyword_Entry.grid(row=145,column=420, columnspan=200, rowspan=58, sticky="WE")
City_Entry = Entry(up_right_frame,textvariable=txtCity)
City_Entry.grid(row=175,column=420, columnspan=200, rowspan=58, sticky="WE")
State_Entry = Entry(up_right_frame,textvariable=txtState)
State_Entry.grid(row=205,column=420, columnspan=200, rowspan=58, sticky="WE")
tk.Label(up_right_frame,text="",bg='ivory3', fg='black',font='Calibri 11 ').grid(row=235,column=420, columnspan=300, rowspan=58, sticky="W")
w = OptionMenu(up_right_frame, Page_Values,*Web_Pages, )
w.grid(row=245,column=420, columnspan=200, rowspan=58, sticky="W")


Folder_EXCEL = tk.Label(up_right_frame,text="Output File Path*: ", bg="ivory3", fg="black", font='Calibri 11').grid(row=350,column=320, columnspan=200, sticky="W")
Browse_Folder_Button = ttk.Button(up_right_frame, text=" Browse Folder ",command=getFolderPath, style = "CustomButton.TButton").grid(row=350,column=380,columnspan=200, sticky="W")
tk.Label(up_right_frame,textvariable=folderPath,bg='ivory3', fg='RoyalBlue4', font='Times 10').grid(row=360,column=320, columnspan=200, sticky="W")



########       -       up_right frame start
Start_Button = ttk.Button(up_right_frame, text="Search", style = "CustomButton.TButton", command=clicked).grid(row=420,column=420,columnspan=50,rowspan=30, sticky="NSWE")
Quit_Open_Button =ttk.Button(up_right_frame, text="Quit & Open Folder", style = "CustomButton.TButton", command=QuitApp_OpenFolder).grid(row=420,column=480,columnspan=50,rowspan=30, sticky="NSWE")
Quit_Button =ttk.Button(up_right_frame, text="Quit", style = "CustomButton.TButton",command=Quit_Button).grid(row=420,column=540,columnspan=50,rowspan=30, sticky="NSWE")


### setting col and row size to 1 pixel
col_count, row_count = gui.grid_size()
for col in range(col_count):
    gui.grid_columnconfigure(col, minsize=1)

for row in range(row_count):
    gui.grid_rowconfigure(row, minsize=1)


### binded
Keyword_Entry.bind("<Return>", clicked)
Keyword_Entry.bind("<KP_Enter>", clicked)  # 2nd enter new numbers
City_Entry.bind("<Return>", clicked)
City_Entry.bind("<KP_Enter>", clicked)  # 2nd enter new numbers
State_Entry.bind("<Return>", clicked)
State_Entry.bind("<KP_Enter>", clicked)
w.bind("<Return>", clicked)
w.bind("<KP_Enter>", clicked)

gui.mainloop()


#testing
# pack and distribute
# if for worksheets