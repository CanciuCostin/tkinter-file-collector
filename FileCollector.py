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
class ScannedServer:
    hostName: str = ''
    txtTimestampFile: str = ''
    txtLastScanFile: str = ''
    jsonLastScanFile: str = ''
    txtLastScanFileStatus: str = ''
    jsonLastScanFileStatus: str = ''
    osName: str = ''
    UUID: str = ''
    uploadStatus: str = ''

class App(Frame):
    allFilesShortPath=list()
    scannedServers=list()
    filePaths=dict()

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

        self.labelInstructions = Label(self, text="Please upload last_scan.json and last_scan.txt files.")
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

        self.buttonUpload=Button(self, text="Upload", command=self.uploadFiles, width=10)
        self.buttonUpload.grid(row=5, column=3)

    def displayMessage(self,message):
        self.topLevel=TopLevel(self.master)
        self.topLevel.title("Help")

        self.stringVar=StringVar()
        self.message=Message(self.topLevel, textVariable=self.stringVar)
        self.stringVar.set(message)
        self.message.pack()

        self.button=Button(self.topLevel, text="Ok", command=self.topLevel.destroy)
        self.button.pack()

    def displayHelp(self):
        CONST_HELP_MESSAGE='    Please upload for each server the .txt and .json files.\n\n\
        To upload a file press the "Browse Files" button, then click the "Upload Files" button\n\n\
        If you want to run the script without the GUI, run it in the same directory with the files you want to upload.'
        self.displayMessage(CONST_HELP_MESSAGE)

    def displayCorruptedFiles(self,fileNames):
        message='The following files are either corrupted or they are not HC output files:\n\n'+'\n'.join(fileNames)
        self.displayMessage(message)

    def displayListBox(self, indexToSelect):
        self.area.delete(0, END)

        if len(App.scannedServers) > 0:
            self.area.insert(END, "No.   File Name                                                                                               OS Name           Upload Status")
            self.area.itemconfig(0, bg="#CFCFD2")

            for i in range(len(App.scannedServers)):
                App.scannedServers[i].txtLastScanFile=App.scannedServers[i].txtLastScanFile if App.scannedServers[i].txtLastScanFile != '' else '         !!!!!!!!!!       MISSING TEXT File      !!!!!!!!!!        '
                App.scannedServers[i].jsonLastScanFile=App.scannedServers[i].jsonLastScanFile if App.scannedServers[i].jsonLastScanFile != '' else '         !!!!!!!!!!       MISSING JSON           !!!!!!!!!!          '

                spacesToAdd=105-len(App.scannedServers[i].txtLastScanFile)
                index=str(i+1) + '.' + ' ' * (4 - len(str(i+1))) 
                self.area.insert(END, index + App.scannedServers[i].txtLastScanFile + ' ' * spacesToAdd + App.scannedServers[i].osName.upper() + '          ' + App.scannedServers[i].txtLastScanFileStatus)
                slef.area.itemconfig(2*i+1, bg="#FFFFFF")
                if any(x in str(self.area.get(2*i+1,2*i+1)).upper() for x in ['MISSING','UNKNOWN']):
                    self.area.itemconfig(2*i+1, {'fg' : 'red'})
                if any(x in str(self.area.get(2*i+1,2*i+1)).upper() for x in ['UPLOADED']):
                    self.area.itemconfig(2*i+1, {'fg' : 'green'})

                spacesToAdd=105-len(App.scannedServers[i].jsonLastScanFile)
                index=str(i+2) + '.' + ' ' * (4 - len(str(i+2))) 
                self.area.insert(END, index + App.scannedServers[i].jsonLastScanFile + ' ' * spacesToAdd + App.scannedServers[i].osName.upper() + '          ' + App.scannedServers[i].jsonLastScanFileStatus)
                slef.area.itemconfig(2*i+2, bg="#F0F0F1")
                if any(x in str(self.area.get(2*i+2,2*i+2)).upper() for x in ['MISSING','UNKNOWN']):
                    self.area.itemconfig(2*i+2, {'fg' : 'red'})
                if any(x in str(self.area.get(2*i+2,2*i+2)).upper() for x in ['UPLOADED']):
                    self.area.itemconfig(2*i+2, {'fg' : 'green'})

                if indexToSelect != None:
                    sef.area.select_set(indexToSelect,indexToSelect)

                self.area.update()
            
    def loadFiles(self):
        bigFixFiles=self.getFilesRecursive("C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\BufferDir\\sha1")
        if len(bigFixFiles) > 0:
            fileNames=bigFixFiles
        else:
            fileNames=filedialog.askopenfilenames(filtetypes = (("JSON/text files", "*.json;*.txt"),("All Files","*.*")))
        if fileNames:
            try:
                for fileName in fileNames:
                    relativeFileName=os.path.basename(fileName).replace('%3A',':').replace('(healthcheck)_0_','')
                    App.filePaths[relativeFileName]=fileName
                    App.allFilesShortPath.append(relativeFileName)
                    fileNameFields=relativeFileName.split('__')
                    if len(fileNameFields) == 3:
                        hostName=fileNameFields[0]
                        UUID=fileNameFields[1]
                        prefix=fileNameFields[2]
                    else:
                        continue
                    scannedServer=next((x for x in App.scannedServers if x.hostName == hostName),None)
                    if scannedServer == None:
                        scannedServer=ScannedServer()
                        scannedServer.hostName=hostName
                        scannedServer.UUID=UUID
                        App.scannedServers.append(scannedServer)
                    if prefix == 'last_scan.json':
                        scannedServer.jsonLastScanFile=relativeFileName
                    elif prefix == 'last_scan.txt':
                        try:
                            scannedServer.osName=self.getOs(fileName)
                        except:
                            print(fileName)
                            continue
                        scannedServer.txtLastScanFile=relativeFileName.replace('%3A',':').replace('(healthcheck)_0_','')
                        scannedServer.txtTimestampFile=scannedServer.hostName + '__' + scannedServer.UUID + self.getTimestampFromFile(fileName) + '.txt'
                self.displayListBox(None)
            except Exception as ex:
                print(ex.args[0])
                print("Error on loading file ")

    def isServerReachable(self, serverAddress):
        socket.socker(socket.AF_INET,socket.SOCK_STREAM)
        rep=os.system('ping '+ serverAddress)
        return True if rep == 0 else False

    def updateFieldProgress(self,field):
        field='Uploading .'
        self.displayListBox(None)
        field+=' .'
        self.displayListBox(None)
        field+=' .'
        self.displayListBox(None)

    def uploadFiles(self):
        if os.path.exists("C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\BufferDir\\sha1"):
            if not os.path.exists("C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\BufferDir\\sha1\\UploadedHCs"):
                os.mkdir("C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\BufferDir\\sha1\\UploadedHCs")
        App.scannedServers=list(filter(lambda x: all(fileName != '' for fileName in [x.txtLastScanFile, x.jsonLastScanFile]),App.scannedServers))

        try:
            for i in range(len(App.scannedServers)):
                if not any(('MISSING' in x or 'Unknown' in x or '' == x) for x in [App.scannedServers[i].jsonLastScanFile,App.scannedServers[i].txtLastScanFile,App.scannedServers[i].txtTimestampFile,App.scannedServers[i].osName]):
                    self.updateFieldProgress(App.scannedServers[i].txtLastScanFileStatus)
                    with open(App.filePaths[App.scannedServers[i].txtLastScanFile]) as f:
                        textContent=f.read()
                        try:
                            self.post(App.scannedServers[i].osName.strip().lower(),App.scannedServers[i].txtTimestampFile,textContent)
                            self.post(App.scannedServers[i].osName.strip().lower(),App.scannedServers[i].txtLastScanFile,textContent)
                            App.scannedServers[i].txtLastScanFileStatus='Uploaded'
                            if os.path.exists("C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\BufferDir\\sha1"):
                                os.rename(App.filePaths[App.scannedServers[i].txtLastScanFile],"C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\" + App.scannedServers[i].txtLastScanFile)
                        except:
                            raise Exception
                        self.displayListBox(None)
                    self.updateFieldProgress(App.scannedServers[i].jsonLastScanFileStatus)
                    with open(App.filePaths[App.scannedServers[i].jsonLastScanFile]) as f:
                        jsonContent=f.read()
                        try:
                            self.post(App.scannedServers[i].osName.strip().lower(),App.scannedServers[i].jsonLastScanFile,jsonContent)
                            self.post(App.scannedServers[i].osName.strip().lower(),App.scannedServers[i].jsonLastScanFile,jsonContent)
                            App.scannedServers[i].jsonLastScanFileStatus='Uploaded'
                            if os.path.exists("C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\BufferDir\\sha1"):
                                os.rename(App.filePaths[App.scannedServers[i].jsonLastScanFile],"C:\\Program Files (x86)\\BigFix Enterprise\\BES Server\\UploadManagerData\\" + App.scannedServers[i].jsonLastScanFile)
                        except:
                            print(App.scannedServers[i].jsonLastScanFile)
                            App.scannedServers[i].jsonLastScanFileStatus = 'Cannot upload'
                        self.displayListBox(None)
                else:
                    self.update(App.scannedServers[i].txtLastScanFileStatus)
                    App.scannedServers[i].txtLastScanFileStatus='Unknown OS' if 'Unknown' in App.scannedServers[i].osName else 'Missing file'
                    self.displayListBox(None)

                    self.update(App.scannedServers[i].jsonLastScanFileStatus)
                    App.scannedServers[i].jsonLastScanFileStatus='Unknown OS' if 'Unknown' in App.scannedServers[i].osName else 'Missing file'
                    self.displayListBox(2*i+1)

            self.displayListBox(None)
            self.displayMessage('File uploaded!')
        except:
            print("Exception uploading file")
            self.displayMessage("Your machine cannot reach the centralized server\nPlease run this on a machine which can ping either sbydmzyz187030.sby.dst.ibm.com or secpkgs.edst.ibm.com")

    def post(self,osName,fileName,fileContent):
        try:
            text = ''
            if fileContent == None:
                with open(fileName) as f:
                    text=f.read()
            else:
                text=fileContent
            url2="https//sbydmzyz187030.sby.dst.ibm.com/HCManager/{0}Upload".format(osName)
            url3="https//secpkgs.edst.ibm.com/HCManager/{0}Upload".format(osName)
            payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"{0}\"; filename=\"{1}\"\r\nContent-Type: text/plain\r\n\r\n{2}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--".format(osName,fileName,fileContent)
            headers = {
                'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                'cache-control': "no-cache",
                'postman-token': "bf4212e6-ae70-2074-76a7-e17059a76d73"
                }
            http = urllib3.PoolManager()
            try:
                r = http.request(
                    "POST", url2, 
                    body=payload,
                    headers = {
                    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                    'cache-control': "no-cache",
                    'postman-token': "bf4212e6-ae70-2074-76a7-e17059a76d73"
                    },
                    timeout=1)
                print('uploaded: '+url2)
                return 0
            except:
                r = http.request(
                    "POST", url3, 
                    body=payload,
                    headers = {
                    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
                    'cache-control': "no-cache",
                    'postman-token': "bf4212e6-ae70-2074-76a7-e17059a76d73"
                    },
                    timeout=1)
                print('uploaded: '+url3)
                return 0
        except:
            raise Exception

    def getOs(self,fileName):
        try:
            operatingSystem=['Windows','AIX     ','Linux  ','Ubuntu','CentOS','Debian']
            with open(fileName) as fileInput:
                lines=fileInput.readlines()
            for line in lines:
                if any(os in line for os in ['OS Name','OS_Name']):
                    for os in operatingSystem:
                        if os.strip().lower() in line.lower():
                            return os if not any(x in os for x in ['Ubuntu','CentOS','Debian']) else 'Linux  '
            return 'Unknown'
        except:
            print("An error has been encountered. Please report this issue.")

    def getTimestampFromFile(self, fileName):
        try:
            timestamp=''
            with open(fileName) as fileInput:
                lines=fileInput.readlines()
                for line in lines:
                    if "Scan Date(local)" in line:
                        timestamp=line.partition(":")[2].strip()[:16].replace(" ","_").replace("_","").replace(":","")
                        return timestamp
                return 'Unknown'
        except Exception as ex:
            print("An error has been encountered. Please report this issue")

    def getFilesRecursive(self,rootdir):
        if os.path.isdir(rootdir) and not os.path.islink(rootdir):
            fileList = []
            try:
                rit=os.scandir(rootdir)
                for entry in rit:
                    if not entry.name.startswith('.') and not os.path.islink(entry.path) and 'last_scan' in entry.path:
                        fileList.append(entr.path)
                        fileList += self.getFilesRecursive(entry.path)
                fileList.sort()
                return fileList
            except Exception as ex:
                return fileList
        else:
            return []
        
def main():
    root=Tk()
    root.geometry("650x400+300+300")
    app=App()
    root.mainloop()

if __name__ == '__main__':
    main()