import urllib3
urllib3.disable_warnings()
import sys
import warnings
import os
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from dataclasses import dataclass
from tkinter.ttk import Style
from tkinter import Tk, Label, Button, Listbox, Entry, IntVar, END, W, E, N, S, filedialog,Frame, BOTH, Toplevel, Message, StringVar, Scrollbar
import time
import socket

"""
Author: Costin Canciu
Entrypoint: FileCollector.py
Description: Collect files from client and send them to a server using multipart form POST requests
"""

@dataclass
class UploadFile:
    fullPath: str = ''
    fileName: str = ''
    uploadStatus: str = ''

class App(Frame):
    uploadFiles=list()

    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_layout(self):
        self.master.title("Tkinter File Collector")
        self.pack(fill=BOTH, expand=True)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(5, pad=7)

    def init_labels(self):
        self.area=Listbox(self, font=('Consolas',10))
        self.area.grid(row=1, column=0, columnspan=2, rowspan=4, padx=5, sticky=E+W+S+N)

    def init_scrollbar(self):
        self.scrollbar=Scrollbar(self, orient="vertical")
        self.scrollbar.config(command=self.area.yview)
        self.scrollbar.grid(row=1, column=2, rowspan=4, padx=5, sticky=E+W+S+N)
        self.area.config(yscrollcommand=self.scrollbar.set)

    def init_button_browse(self):
        self.buttonBrowse=Button(self,text="Browse Files", command=self.load_files, width=10)
        self.buttonBrowse.grid(row=1, column=3)

    def init_button_close(self):
        self.buttonClose=Button(self, text="Close", command=self.master.quit, width=10)
        self.buttonClose.grid(row=2, column=3, pady=4)

    def init_button_help(self):
        self.buttonHelp=Button(self, text="Help", command=self.display_help, width=10)
        self.buttonHelp.grid(row=5, column=0, padx=5)

    def init_button_upload(self):
        self.buttonUpload=Button(self, text="Upload", command=self.upload_files, width=10)
        self.buttonUpload.grid(row=5, column=3)

    def init_buttons(self):
        self.init_button_browse()
        self.init_button_close()
        self.init_button_help()
        self.init_button_upload()

    def init_UI(self):
        self.init_layout()
        self.init_labels()
        self.init_scrollbar()
        self.init_buttons()

    def display_message(self,message):
        self.topLevel=Toplevel(self.master)
        self.topLevel.title("Help")
        self.stringVar=StringVar()
        self.message=Message(self.topLevel, textvariable=self.stringVar)
        self.stringVar.set(message)
        self.message.pack()
        self.button=Button(self.topLevel, text="Ok", command=self.topLevel.destroy)
        self.button.pack()

    def display_help(self):
        CONST_HELP_MESSAGE='To upload a file press the "Browse Files" button, then click the "Upload Files" button'
        self.display_message(CONST_HELP_MESSAGE)

    def display_listBox(self, indexToSelect):
        self.area.delete(0, END)
        if len(App.uploadFiles) > 0:
            self.area.insert(END, "No.  File Name                          Upload Status")
            self.area.itemconfig(0, bg="#CFCFD2")
            for i in range(len(App.uploadFiles)):
                spacesToAdd=35-len(App.uploadFiles[i].fileName)
                index=str(i+1) + '.' + ' ' * (4 - len(str(i+1))) 
                self.area.insert(END, index + App.uploadFiles[i].fileName + ' ' * spacesToAdd + App.uploadFiles[i].uploadStatus)
                self.area.itemconfig(i+1, bg="#FFFFFF" if i%2 else "#F0F0F1")
                if any(x in str(self.area.get(i+1,i+1)).upper() for x in ['UPLOADED']):
                    self.area.itemconfig(i+1, {'fg' : 'green'})
                if indexToSelect != None:
                    self.area.select_set(indexToSelect,indexToSelect)
                self.area.update()
            
    def load_files(self):
        fileNames=filedialog.askopenfilenames(filetypes = (("JSON/text files", "*.json;*.txt"),("All Files","*.*")))
        if fileNames:
            try:
                for fileName in fileNames:
                    uploadFile=UploadFile()
                    uploadFile.fullPath=fileName
                    uploadFile.uploadStatus='None'
                    uploadFile.fileName=os.path.basename(fileName)
                    App.uploadFiles.append(uploadFile)
                self.display_listBox(None)
            except Exception as ex:
                print(ex.args[0])
                print("Error on loading files.")

    def is_server_reachable(self, serverAddress):
        socket.socker(socket.AF_INET,socket.SOCK_STREAM)
        reply=os.system('ping '+ serverAddress)
        return True if reply == 0 else False

    def update_field_progress(self):
        yield 'Uploading .'
        yield 'Uploading . .'
        yield 'Uploading . . .'

    def upload_files(self):
        try:        
            for i in range(len(App.uploadFiles)):
                for status in self.update_field_progress():
                    App.uploadFiles[i].uploadStatus=status
                    time.sleep(0.5)
                    self.display_listBox(None)
                with open(App.uploadFiles[i].fullPath) as fileInput:
                    textContent=fileInput.read()
                try:
                    self.post(App.uploadFiles[i].fileName,textContent)
                    App.uploadFiles[i].uploadStatus='Uploaded'
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    App.uploadFiles[i].uploadStatus='Upload Error'
                self.display_listBox(None)
            self.display_message('Files uploaded!')
        except:
            print("Exception uploading files")
            self.display_message("Error uploading files.")

    def post(self,fileName,fileContent):
        url="http://localhost:8080/upload"
        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"fileupload\"; filename=\"{0}\"\r\nContent-Type: text/plain\r\n\r\n{1}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--".format(fileName,fileContent)
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'cache-control': "no-cache",
            'postman-token': "bf4212e6-ae70-2074-76a7-e17059a76d73"
            }
        http = urllib3.PoolManager()
        response = http.request(
            "POST", url, 
            body=payload,
            headers = headers,
            timeout=1)

def main():
    root=Tk()
    root.geometry("650x400+300+300")
    app=App()
    root.mainloop()

if __name__ == '__main__':
    main()