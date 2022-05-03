# Title : Telnyx Lookup
# Author: Jun Kim
# Date: 07/16/2021
# Description: In this program, tkinter will be used to prompt a user to choose a csv file that contains phone numbers with the column name "Phone". 
# The script will then run a loop that will send an API request to Telnyx to gather information about the phone numbers and write a CSV file with that information.
# An output file is created every 1000 number of times. Line 157 is where the value is set.

import pandas as pd                                                                         
import os                                                                                   
import requests                                                                             
import json                                                                                 
import time                                                                                
import tkinter as tk                                                                       
from tkinter import *
from tkinter.filedialog import askopenfilename                                              
from pandas import json_normalize                                                        
from datetime import datetime                                                             
from typing import Counter


def main():

    window = tk.Tk()                                                                        
    window.geometry('200x200')                                                             

    label = tk.Label(text='Telnyx Lookup')                                                  
    label.pack()

    def csv_opener():
        """ this function is used for the button to open the csv file """
        global csv_name
        global csv_file
        global csv_df
        
        # show an "Open" dialog box and return the path to the selected file
        csv_name = askopenfilename()                                                        
        csv_file = open(csv_name, 'r')		                        
        csv_data = pd.read_csv(csv_file)                                                    
        csv_df = pd.DataFrame(csv_data)                                                     
            
        # button to close tkinter window
        end_button = Button(window, text = 'Create', command =window.destroy).pack()       
                                                                    
    csv_button = Button(window, text = 'Open CSV File', command = csv_opener).pack()

    window.mainloop()                                                                      


    def output_creator():
        """Function to create Output CSV file"""
        
        # year_month_day-hours_minutes_seconds_AM/PM ; used in Title 
        dt = datetime.now().strftime('%Y.%m.%d-%I%M%S%p')                                                              
        dt_string = str(dt)                                                                 
        
        # grabs the title of the csv file       
        last_path = os.path.basename(os.path.normpath(csv_file.name))                               

        file_name = dt_string +" Count_"+str(counter)+" "+last_path                        

        script_dir = os.path.dirname(__file__)                                             
        rel_path = 'Output'
        
        # this joins the absolute path of current script with wanted relative path
        abs_file_path = os.path.join(script_dir, rel_path)                                  

        drop_list = []

        csv_df_copy = csv_df.copy(deep=True)
        
        # drop every phone numbers that were not used
        for i in range(len(csv_df_copy.index)):                                             
            if i > counter-1:
                drop_list.append(i)
        
        # drops the indexes of phone numbers that were not used
        csv_df_copy = csv_df_copy.drop(drop_list)                                           

        for i in range(len(list_of_lists)):                                                 
            csv_df_copy[column_keys[i]] = list_of_lists[i]                                                            

        csv_df_copy = csv_df_copy.applymap(str)
        
        # writes the dataframe into the new file without the indices
        with open(abs_file_path+'/'+file_name, 'w',newline='') as new_file:	                

            csv_df_copy.to_csv(new_file, index=False)                                       
            csv_file.close()


    column_keys = []                                                                       
    list_of_lists = []                                                                   
    
    # this flag is used to create the column_keys on the first iteration
    first = True                                                                            
    
    # this counter counts the number of API requests made
    counter = 0              
    
    # if this reaches 10 with any one phone number, write the CSV file and end script
    error_counter = 0                                                                   

    for number in csv_df['Phone']:
        number=str(number)
        input_number=""                                                                   
        
        # this for loop takes out any non-numeric character from the phone numbers
        for character in number:                                                            
            if character.isnumeric():
                input_number = input_number+character                                       

        input_number="1"+input_number                                                      
        
         # The purpose of this while loop is to give each API request 10 tries before ending the script
        while True:                                                                         

            if error_counter == 10:                                     
                break

            try:                                                                            
                res = requests.get('https://api.telnyx.com/anonymous/v2/number_lookup/'+input_number)  
                normalized_data = pd.json_normalize(res.json())   

            except:
                error_counter += 1                                                          
                print("Trying Again...")
                time.sleep(65)
                continue                 

            break
        
        # break out of the for-loop if a phone number in all the phone number has failed
        if error_counter == 10:                                                             
            break
        
        # this is done to set the column_keys and populate list_of_lists on first iteration
        if first == True:                                                                  

            for column_name in normalized_data:

                column_keys.append(column_name)
                column_list = []
                list_of_lists.append(column_list)
                first = False                                                               
        
         # this stores the normalized JSON data into a list of lists.
        for i in range(len(column_keys)):                                                   
            
            try:
                new_data = ''.join(str(e) for e in (normalized_data[column_keys[i]].values))

            except: 
                new_data = "N/A"

            list_of_lists[i].append(new_data)
        
        error_counter = 0

        counter += 1                                                                       
        
        # API limit is 10 per minute, so wait 63 seconds after every 10 numbers
        if counter%10 == 0:                                                                 
            print(str(counter) + ' Finished')
            time.sleep(63)         
        
        # after every X number of entries, create an output CSV file
        if counter%100 == 0:                                                                
            print('Creating CSV File...')  
            output_creator()
    

    output_creator()                                                                        

if __name__ == '__main__':
    main()
