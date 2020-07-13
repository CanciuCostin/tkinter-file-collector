# Tkinter File Collector
GUI based file uploader using tkinter

[![Python][python-shield]][python-url]


Collect files from client and send them to a server using multipart form POST requests.

![](demo.gif)

## Build

```
pyinstaller --onefile FileCollector.py
```

## Usage example

1. Ensure your server is up and listening for requests. You can use a dummy nodejs server:
```
node DummyServer.js
```
2. Run the python application
Source:
```
python FileCollector.py
```
or
Executable:
```
.\dist\FileCollector.exe
```

## Prerequisites

```
pip install urllib3
```

<!-- Markdown link & img dfn's -->
[python-shield]: https://img.shields.io/badge/python-3.8.3-green
