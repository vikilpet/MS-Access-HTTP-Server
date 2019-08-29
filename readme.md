# MS Access HTTP Server (Python)
Obtaining data from a Microsoft Access database using an HTTP request. Output format: JSON, CSV, HTML. You can also make requests to add, modify and update data.

HTML output example:
<p align="center">
	<img src="https://i1.imageban.ru/out/2019/08/29/6da561ba51885de8006ed6ef7f0959f3.png">
</p>

JSON:
<p align="center">
	<img src="https://i3.imageban.ru/out/2019/08/29/0a54638c32cc49fd3c20ef6b99d549d3.png">
</p>

Adding a record:
<p align="center">
	<img src="https://i2.imageban.ru/out/2019/08/29/e908c75a75bc822a0ab11bf4e980bb69.png">
</p>

## Usage
Run http_query.py, type URL in browser:
```
http://127.0.0.1:80/db_test?mime=html&headers=true&sql=SELECT TOP 3 * FROM Suppliers
```
Parameters:
- *mime* - output format (html, json or csv).
- *headers* - column headers.
- *sql* - actual query. When you generate queries in your application, don't forget [to encode in URL-friendly format](https://en.wikipedia.org/wiki/Percent-encoding)

## Setup
**Requirements**: Windows 7 and above, Python 3.7
Download project, install requirements: *pip install -r requirements.txt*
Change settings in settings.ini

Section **web server** - settings for the HTTP server.
- *bind_ip* - local IP address to which the server is bound. By default it is 127.0.0.1 so server will only respond to requests received from the same computer.
- *white_list* - list of IP adresses separated by commas from which connections are allowed.

Then you need to add the databases. Each database (mdb or accdb file) is a separate section with a unique name. Settings:
- *db* - full path to file.
- *driver* - ODBC driver name.
- *uid* - user.
- *pwd* - password if required.
- *systemdb* - .mdw file if required.

Optionally you can add test queries to be executed at startup of msaccess.py:
- *test_run* - SQL query for selection (SELECT).
- *text_exec* - SQL query for add/modify/delete (INSERT/UPDATE/DELETE).
