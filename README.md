# Tkinter File Collector
GUI based file uploader using tkinter

[![NPM Version][npm-image]][npm-url]
[![Build Status][travis-image]][travis-url]
[![Downloads Stats][npm-downloads]][npm-url]

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
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
