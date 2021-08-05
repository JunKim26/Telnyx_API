# Title : Telnyx Lookup
# Author: Jun Kim
# Date: 07/16/2021
# Description: In this program, tkinter will be used to prompt a user to choose a csv file that contains phone numbers with the column name "Phone". 
# The script will then run a loop that will send an API request to Telnyx to gather information about the phone numbers and write a CSV file with that information.

from typing import Counter
import pandas as pd                                                                         # used to create dataframes
import os                                                                                   # used to create relative path to write file
from datetime import date                                                                   # used to get the current date
from datetime import datetime                                                               # used to get date and time
import tkinter as tk                                                                        # used as a user friendly tool for the program
from tkinter.filedialog import askopenfilename                                              # used to open csv file
from tkinter import StringVar                                                           
from tkinter import *
import requests                                                                             # used for API requests
import json                                                                                 # used to work with JSON
from pandas import json_normalize                                                           # used to normalize JSON data
import time                                                                                 # used to pause between API requests to not 


if __name__ == '__main__':

# =======================================================================================================================================================
#                                                           Script lines for Tkinter GUI
# =======================================================================================================================================================

    window = tk.Tk()                                                                        # creates a tkinter object
    window.geometry('200x200')                                                              # set size of tkinter window

    label = tk.Label(text='Telnyx Lookup')                                                  # sets the text to be dipslayed by tkinter
    label.pack()

    def csv_opener():
        """ this function is used for the button to open the csv file """
        global csv_name
        global csv_file
        global csv_df
        csv_name = askopenfilename()                                                        # show an "Open" dialog box and return the path to the selected file
        csv_file = open(csv_name, 'r')		                        
        csv_data = pd.read_csv(csv_file)                                                    
        csv_df = pd.DataFrame(csv_data)                                                     # creates a pandas dataframe using the input csv file

        end_button = Button(window, text = 'Create', command =window.destroy).pack()        # button to close tkinter window
                                                                    
    csv_button = Button(window, text = 'Open CSV File', command = csv_opener).pack()

    window.mainloop()                                                                       # tells Python to run the Tkinter event loop

# =======================================================================================================================================================
#                                                         Function to create Output CSV file
# =======================================================================================================================================================


    def output_creator():

        dt = datetime.now().strftime('%Y.%m.%d-%I%M%S%p')                                   # year_month_day-hours_minutes_seconds_AM/PM ; used in Title                            
        dt_string = str(dt)                                                                 # string of date and time
                    
        last_path = os.path.basename(os.path.normpath(csv_file.name))                       # grabs the title of the csv file             

        file_name = dt_string +" Count_"+str(counter)+" "+last_path                         # sets the file name 

        script_dir = os.path.dirname(__file__)                                              # absolute directory the script is in
        rel_path = 'Output'
        abs_file_path = os.path.join(script_dir, rel_path)                                  # this joins the absolute path of current script with wanted relative path

        drop_list = []

        csv_df_copy = csv_df.copy(deep=True)

        for i in range(len(csv_df_copy.index)):                                             # drop every phone numbers that were not used
            if i > counter-1:
                drop_list.append(i)

        csv_df_copy = csv_df_copy.drop(drop_list)                                           # drops the indexes of phone numbers that were not used

        for i in range(len(list_of_lists)):                                                 # this populates the actual json data into each column
            csv_df_copy[column_keys[i]] = list_of_lists[i]                                                            

        csv_df_copy = csv_df_copy.applymap(str)

        with open(abs_file_path+'/'+file_name, 'w',newline='') as new_file:	                # creates csv to write in

            csv_df_copy.to_csv(new_file, index=False)                                       # writes the dataframe into the new file without the indices
            csv_file.close()

# =======================================================================================================================================================
#                                                 Section to send API request and collect JSON data
# =======================================================================================================================================================

    column_keys = []                                                                        # this list will be used to contain the column_keys from the JSON file
    list_of_lists = []                                                                      # this list will contain lists that each represent a column    

    first = True                                                                            # this flag is used to create the column_keys on the first iteration

    counter = 0                                                                             # this counter counts the number of API requests made
    error_counter = 0                                                                       # if this reaches 10 with any one phone number, write the CSV file and end script

    for number in csv_df['Phone']:
        number=str(number)
        input_number=""                                                                     # this is the number that is sent to the API request

        for character in number:                                                            # this for loop takes out any non-numeric character from the phone numbes 
            if character.isnumeric():
                input_number = input_number+character                                       

        input_number="1"+input_number                                                       # adds the country code of "1" (United States)

        while True:                                                                         # The purpose of this while loop is to give each API request 10 tries before ending the script

            if error_counter == 10:                                     
                break

            try:                                                                            # sends API request using the standardized phone number
                res = requests.get('https://api.telnyx.com/anonymous/v2/number_lookup/'+input_number)  
                normalized_data = pd.json_normalize(res.json())   

            except:
                error_counter += 1                                                          # if API request does not go through, add 1 to the error counter and wait 65 seconds.
                print("Trying Again...")
                time.sleep(65)
                continue                 

            break

        if error_counter == 10:                                                             # break out of the for-loop if a phone number in all the phone number has failed
            break
        
        if first == True:                                                                   # this is done to set the column_keys and populate list_of_lists on first iteration

            for column_name in normalized_data:

                column_keys.append(column_name)
                column_list = []
                list_of_lists.append(column_list)
                first = False                                                               

        for i in range(len(column_keys)):                                                   # this stores the normalized JSON data into a list of lists.
            
            try:
                new_data = ''.join(str(e) for e in (normalized_data[column_keys[i]].values))

            except: 
                new_data = "N/A"

            list_of_lists[i].append(new_data)
        
        error_counter = 0

        counter += 1                                                                        # add 1 to the counter tha counts the number of phone numbers finished

        if counter%10 == 0:                                                                 # API limit is 10 per minute, so wait 63 seconds after every 10 numbers
            print(str(counter) + ' Finished')
            time.sleep(63)         

        if counter%100 == 0:                                                                 # after every X number of entries, create an output CSV file
            print('Creating CSV File...')  
            output_creator()
    

    output_creator()                                                                        # creates Final output csv after processing through all rows
