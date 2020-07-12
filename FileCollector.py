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

@dataclass
class UploadFile:
    fullPath: str = ''
    fileName: str = ''
    uploadStatus: str = ''

class App(Frame):
    uploadFiles=list()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("Health Check Collector")
        self.pack(fill=BOTH, expand=True)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(5, pad=7)

        self.labelInstructions = Label(self, text="Please browse the files you want to upload.")
        self.labelInstructions.grid(sticky=W, pady=4, padx=5)

        self.area=Listbox(self, font=('Consolas',10))
        self.area.grid(row=1, column=0, columnspan=2, rowspan=4, padx=5, sticky=E+W+S+N)

        self.scrollbar=Scrollbar(self, orient="vertical")
        self.scrollbar.config(command=self.area.yview)
        self.scrollbar.grid(row=1, column=2, rowspan=4, padx=5, sticky=E+W+S+N)
        self.area.config(yscrollcommand=self.scrollbar.set)

        self.buttonBrowse=Button(self,text="Browse Files", command=self.loadFiles, width=10)
        self.buttonBrowse.grid(row=1, column=3)

        self.buttonClose=Button(self, text="Close", command=self.master.quit, width=10)
        self.buttonClose.grid(row=2, column=3, pady=4)

        self.buttonHelp=Button(self, text="Help", command=self.displayHelp, width=10)
        self.buttonHelp.grid(row=5, column=0, padx=5)

        self.buttonUpload=Button(self, text="Upload", command=self.upload_files, width=10)
        self.buttonUpload.grid(row=5, column=3)


    def displayMessage(self,message):
        self.topLevel=Toplevel(self.master)
        self.topLevel.title("Help")

        self.stringVar=StringVar()
        self.message=Message(self.topLevel, textvariable=self.stringVar)
        self.stringVar.set(message)
        self.message.pack()

        self.button=Button(self.topLevel, text="Ok", command=self.topLevel.destroy)
        self.button.pack()

    def displayHelp(self):
        CONST_HELP_MESSAGE='To upload a file press the "Browse Files" button, then click the "Upload Files" button'
        self.displayMessage(CONST_HELP_MESSAGE)

    def displayListBox(self, indexToSelect):
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
            
    def loadFiles(self):
        fileNames=filedialog.askopenfilenames(filetypes = (("JSON/text files", "*.json;*.txt"),("All Files","*.*")))
        if fileNames:
            try:
                for fileName in fileNames:
                    uploadFile=UploadFile()
                    uploadFile.fullPath=fileName
                    uploadFile.uploadStatus='None'
                    uploadFile.fileName=os.path.basename(fileName)
                    App.uploadFiles.append(uploadFile)
                self.displayListBox(None)
            except Exception as ex:
                print(ex.args[0])
                print("Error on loading files.")

    def isServerReachable(self, serverAddress):
        socket.socker(socket.AF_INET,socket.SOCK_STREAM)
        reply=os.system('ping '+ serverAddress)
        return True if reply == 0 else False

    def updateFieldProgress(self,index):
        App.uploadFiles[index].uploadStatus='Uploading .'
        time.sleep(1)
        self.displayListBox(None)
        App.uploadFiles[index].uploadStatus+=' .'
        time.sleep(1)
        self.displayListBox(None)
        App.uploadFiles[index].uploadStatus+=' .'
        time.sleep(1)
        self.displayListBox(None)

    def upload_files(self):
        try:        
            for i in range(len(App.uploadFiles)):
                self.updateFieldProgress(i)
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
                self.displayListBox(None)
            self.displayMessage('Files uploaded!')
        except:
            print("Exception uploading files")
            self.displayMessage("Error uploading files.")

    def post(self,fileName,fileContent):
        print(fileName)
        print(fileContent)
        text = ''
        if fileContent == None:
            with open(fileName) as f:
                text=f.read()
        else:
            text=fileContent
        url="http://localhost:8080/upload"
        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"fileupload\"; filename=\"{0}\"\r\nContent-Type: text/plain\r\n\r\n{1}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--".format(fileName,fileContent)
        print(payload)
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