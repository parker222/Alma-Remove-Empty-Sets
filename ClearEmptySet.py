from tkinter import *
from tkinter import messagebox
import requests
import configparser
import xmltodict
import pprint
import pathlib as Path

# configurations ##############################################################
config = configparser.ConfigParser()
config.read('config.ini')

apikey = config['misc']['apikey']

# main program ################################################################
def main(*args):
    #main loop tree
	#open file
    origin_file = gui.get_file()
    origin_count = 0
    full_line = ""
    output_line = ""
    set_name = ""
    set_id = ""
    set_count = ""
    origin_name = (f'{origin_file}.txt')
    del_file_name = (f'{origin_file}_sets_deleted.txt')
    not_del_file_name = (f'{origin_file}_not_deleted.txt')
    not_found_file_name = (f'{origin_file}_sets_not_found.txt')
    not_empty_file_name = (f'{origin_file}_sets_with_members.txt')
    
    
    try:
        cl = open(f"{origin_name}","r")
        for line in cl:
			#add to count
            origin_count += 1
			#capture barcode
            full_line = line.strip('\r\n')
            set_name = full_line
            
			#get item record
            alma = getXML(f"https://api-na.hosted.exlibrisgroup.com/almaws/v1/conf/sets?set_type=ITEMIZED&q=name~{set_name}&limit=1&offset=0&set_origin=UI&apikey={apikey}")
			# check for errors
            errors_exist = check_errors(alma)
			# create line
            if errors_exist[0] == True:
            	error = errors_exist[1]
            	f = open(f"{not_found_file_name}","a")
            	f.write(f"{set_name}     {error}\n")
            	f.close
            else:
				#parse item record
            	field_test = "None"
            	item_xml = alma.text
            	alma_dict = xmltodict.parse(alma.text, dict_constructor=dict)
            	got_set = alma_dict['sets']['@total_record_count']
            	if str(got_set) != "0":
                    #set_id = alma_dict['member_link']['id']
                    set_id = alma_dict['sets']['set']['id']
                    get_count = getXML(f"https://api-na.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{set_id}/members?limit=1&offset=0&apikey={apikey}")
                    item_xml = get_count.text
                    count_set_dict = xmltodict.parse(get_count.text, dict_constructor=dict)
                    #set_count_hold = count_set_dict['members']
                    set_count = count_set_dict['members']['@total_record_count']
                    if str(set_count) == "0":
                        #delete_set_xml = \
#f"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
#<set>
#<id>{set_id}</id>
#</set>
#"""
                        delete_set = requests.delete(f"https://api-na.hosted.exlibrisgroup.com/almaws/v1/conf/sets/{set_id}?apikey={apikey}")
                        #print(delete_set)
                        del_errors = check_errors(delete_set)
                        #print(delete_set.text)
                        if del_errors[0] == True:
                            #print(del_errors)
                            f = open(f"{not_del_file_name}","a")
                            f.write(f"{set_name}    {del_errors[1]}\n")
                            f.close
                        else:
                            f = open(f"{del_file_name}","a")
                            f.write(f"{set_name}\n")
                            f.close
                    else:
                        f = open(f"{not_empty_file_name}","a")
                        f.write(f"{set_name}    {set_count} Members\n")
                        f.close
            	else:
                    f = open(f"{not_found_file_name}","a")
                    f.write(f"{set_name}\n")
                    f.close                    
        cl.close()       
    except FileNotFoundError:
        msg = (f"{origin_name} NOT FOUND")
        gui.msgbox(msg)
		
    gui.update_file_display(origin_name, origin_count)
            
# functions ###################################################################
def postXML(url, xml):
    headers = {'Content-Type': 'application/xml', 'charset':'UTF-8'}
    r = requests.post(url, data=xml.encode('utf-8'), headers=headers)
    return r

def getXML(url):
    headers = {'Content-Type': 'application/xml', 'charset':'UTF-8'}
    x = requests.get(url, headers=headers)
    return x
    
def check_errors(r):
    if (r.status_code != 200) and (r.status_code != 204):
        errors = xmltodict.parse(r.text)
        error = errors['web_service_result']['errorList']['error']['errorMessage']
        return True, error
    else: 
        return False, "OK"
            
# gui #########################################################################
class gui:
    def __init__(self, master):
        self.master = master
        master.title("Shelf List")
        master.resizable(0, 0)
        master.minsize(width=600, height=100)
        
        self.status_title = Label(height=1, text="Name Your Text File", font="Consolas 12 italic")
        self.status_title.pack(fill="both", side="top")

        self.status_added = Label(height=1, text="READY", font="Consolas 12 bold", fg="green")
        self.status_added.pack(fill="both", side="top")

        self.file_entry_field = Entry(font="Consolas 16")
        self.file_entry_field.focus()
        self.file_entry_field.bind('<Key-Return>', main)
        self.file_entry_field.pack(fill="both", side="top")
        
        self.compare_button = Button(text="Delete Zero Member Sets", font="Arial 16", command=main)
        self.compare_button.pack(fill="both", side="top")
		
        self.file_origin = Label(height=1, text="", font="Consolas 12 italic")
        self.file_origin.pack(fill="both", side="top")
        
    def msgbox(self, msg):
        messagebox.showerror("Attention", msg)
        
    def get_file(self):
        compare_file = self.file_entry_field.get()
        return compare_file 
        
    def get_lib(self):
        for circ in options_step_two:
            if circ == self.selected_desk.get():
                circ_library = options_step_two[self.selected_desk.get()]
        return circ_library
        
    def clear_file(self):
        self.file_entry_field.delete(0, END)
            
    def update_file_display(self, origin_name, origin_count):
        self.file_origin.config(text=f"File Read: {origin_name} - {origin_count} Sets")

		
               
root = Tk()
gui = gui(root)
root.mainloop()