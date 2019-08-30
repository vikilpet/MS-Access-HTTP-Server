
import os
import time
import json
import csv
import configparser
import io
import pandas
import ctypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote
from msaccess import run_query, exec_query

sett = None
DEFAULT_SETTINGS = {
	'bind_ip': '127.0.0.1'
	, 'port': 80
	, 'white_list': '127.0.0.1'
	, 'developer': False
}
HTML_TEMPLATE = r'''
	<!DOCTYPE html>
	<html>
		<head>
			<title>Query result</title>
			<meta charset="utf-8">
		</head>
		<body>{}</body>
	</html>
'''

DEF_TITLE = 'MS Access HTTP Server'
CONTENT_TYPES = {
	'html': 'text/html'
	, 'json': 'application/json'
	, 'csv': 'text/csv'
}
req_counter = 0
set_title = ctypes.windll.kernel32.SetConsoleTitleW

class Settings:
	''' Load settings from section from .ini file in module folder
	'''
	def __init__(s, section:str, ini_file:str='settings.ini'
				, encoding:str='utf-8-sig', default_sett:dict={}):
		s.section = section
		s.ini_file = os.path.join(
			os.path.abspath(os.path.dirname(__file__))
			, ini_file
		)
		config = configparser.ConfigParser()
		config.optionxform = str
		config.read(
			s.ini_file
			, encoding=encoding
		)
		for setting in config.items(section):
			if setting[1].lower() in ('true', 'yes'):
				s.__dict__[setting[0]] = True
			elif setting[1].lower() in ('false', 'no'):
				s.__dict__[setting[0]] = False
			elif setting[1].isdigit():
				s.__dict__[setting[0]] = int(setting[1])
			elif setting[1].replace('.', '', 1).isdigit():
				try:
					s.__dict__[setting[0]] = float(setting[1])
				except:
					s.__dict__[setting[0]] = setting[1]
			else:
				s.__dict__[setting[0]] = setting[1]
		for setting in default_sett.items():
			s.__dict__.setdefault(setting[0], setting[1])
	
	def show(s)->str:
		''' Show file, section and all settings (for debugging)
		'''
		r = ''
		for key, value in s.__dict__.items():
			r += f'{key}: {value}\n'
		return r

def make_html(query_data:list, headers:bool)->str:
	''' Makes HTML code from list of lists in query_data.
		headers - the first nested list contains column headers.
	'''
	if headers:
		col_names = query_data[0]
		del query_data[0]
	else:
		col_names = None
	try:
		df = pandas.DataFrame(query_data, columns=col_names)
	except Exception as e:
		print(f'DataFrame error:\n{repr(e)}')
		return f'DataFrame error:\n{repr(e)}'
	table = df.to_html(header=headers)
	return HTML_TEMPLATE.format(table)

def parse_url(url:str)->tuple:
	''' Takes URL and returns path and dict with
		URL parameters.
	'''
	parsed_url = urlparse(url.lower())
	params = {}
	for k, v in parse_qs(parsed_url.query).items():
		params[k.lower()] = v[0].lower()
	return unquote(parsed_url.path[1:]), params

def get_query_result(db:str, sql:str, cont_type:str, headers:bool=False)->str:
	'''	Executes a SQL query and returns the result in
		the required format.
	'''
	status, query_data = run_query(db=db, sql=sql, headers=headers)
	if not status:
		return f'run_query error: {query_data}'
	if cont_type == 'json':
		try:
			return json.dumps(query_data)
		except Exception as e:
			print(f'json.dumps error:\n{repr(e)}')
			return f'json.dumps error:\n{repr(e)}'
	elif cont_type == 'csv':
		try:
			output = io.StringIO()
			writer = csv.writer(output)
			writer.writerows(query_data)
			return output.getvalue()
		except Exception as e:
			print(f'csv error:\n{repr(e)}')
			return f'csv error:\n{repr(e)}'
	else:
		return make_html(query_data, headers)

def process_request(url:str)->tuple:
	''' Returns content-type:str, content:str for requested path
	'''

	db, params = parse_url(url.lower())
	mime = params.get('mime', 'html')
	if params['sql'][:6] == 'select':
		cont_type = CONTENT_TYPES.get(mime, 'html')
		content = get_query_result(
			db=db
			, sql=params['sql']
			, cont_type=mime
			, headers=(
				params.get('headers', 'false').lower()
					in ['yes', 'true']
			)
		)
	else:
		cont_type = 'text/plain'
		status, number = exec_query(db=db, sql=params['sql'])
		content = f'{status}: {number}'
	return cont_type, content

class QueryHandler(BaseHTTPRequestHandler):
	def do_GET(s):
		if 'favicon.' in s.path:
			if sett.developer: print(f'favicon request: {s.path}')
			s.wfile.write(b'<link rel="icon" href="data:,">')
			return
		if sett.white_list:
			if not s.address_string() in sett.white_list.split(','):
				print(time.asctime()
					, f'Request from unknown IP ({s.address_string()}): {s.path}')
				s.send_header('Content-type', 'text/plain; charset=utf-8')
				s.wfile.write(b'403')
				return
		s.respond(200)
			
	def handle_http(s, status_code, path):
		global req_counter
		try:
			cont_type, content = process_request(path)
			s.send_response(status_code)
			s.send_header('Content-type', cont_type + '; charset=utf-8')
			s.end_headers()
			req_counter += 1
			set_title(f'{DEF_TITLE} ({req_counter})')
			return bytes(content, 'utf-8')
		except Exception as e:
			print(f'handle_http error:\n{repr(e)}')
			return bytes(f'handle_http error:\n{repr(e)}', 'utf-8')

	def respond(s, status):
		response = s.handle_http(status, s.path)
		s.wfile.write(response)

def main():
	global sett
	sett = Settings('web server', default_sett=DEFAULT_SETTINGS)
	try:
		server_class = ThreadingHTTPServer
		httpd = server_class((sett.bind_ip, sett.port), QueryHandler)
		set_title(DEF_TITLE)
		print(time.asctime()
			, f'The server is running at {sett.bind_ip}:{sett.port}')
		if sett.developer:
			os.startfile(sett.url_exec.format(sett.bind_ip, sett.port))
			os.startfile(sett.url_run.format(sett.bind_ip, sett.port))
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('Stopped by keyboard')
	except Exception as e:
		print(f'Server error:\n{repr(e)}')
		return
	httpd.server_close()
	print(time.asctime(), f'The server is stopped.')

if __name__ == '__main__': main()