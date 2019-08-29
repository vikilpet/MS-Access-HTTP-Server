import os
import configparser
import pyodbc

DEFAULT_SETTINGS = {
	'driver': r'Microsoft Access Driver (*.mdb, *.accdb)'
	, 'uid': r'admin'
	, 'pwd': r''
	, 'systemdb': r''
}

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

def run_query(db:str, sql:str, headers:bool=False, test:bool=False)->tuple:
	''' Run an SQL query and return the status and query data (or error)
		as list of lists.
		db - name of database as section in ini file.
		sql - query.
		headers - add column headers to data.
		test - use test SQL from ini file.
	'''
	sett = Settings(db, default_sett=DEFAULT_SETTINGS)
	if test: sql = sett.test_run
	try:
		con = pyodbc.connect(
			'DRIVER=' + sett.driver
			+ ';DBQ=' + sett.db
			+ ';PWD=' + sett.pwd
			+ ';UID=' + sett.uid
			+ ';SYSTEMDB=' + sett.systemdb
		)
		cur = con.cursor()
		rows = cur.execute(sql).fetchall()
		rows = [list(x) for x in rows]
		if headers:
			columns = [column[0] for column in cur.description]
			rows.insert(0, columns)
		cur.close()
		con.close()
	except Exception as e:
		return False, (
			f'Settings:\n{sett.show()}'
			+ f'\n\nODBC error:\n{repr(e)}'
		)
	return True, rows
	
def exec_query(db:str, sql:str, test:bool=False)->tuple:
	''' Execute UPDATE, INSERT, DELETE queries.
		Returns True and the number of records and False and
		error text on fail.
		db - name of database.
		sql - query.
		test - use test SQL from ini file.
	'''
	sett = Settings(db, default_sett=DEFAULT_SETTINGS)
	if test: sql = sett.test_exec
	try:
		con = pyodbc.connect(
			'DRIVER=' + sett.driver
			+ ';DBQ=' + sett.db
			+ ';PWD=' + sett.pwd
			+ ';UID=' + sett.uid
			+ ';SYSTEMDB=' + sett.systemdb
		)
		cur = con.cursor()
		number = cur.execute(sql).rowcount
		cur.commit()
		cur.close()
		con.close()
	except Exception as e:
		return False, (
			f'Settings:\n{sett.show()}'
			+ f'\n\nODBC error:\n{repr(e)}'
		)
	return True, number
	
if __name__ == '__main__':
	status, data = run_query('db test', '', headers=True, test=True)
	if status:
		print('Test query result:')
		print(*data, sep='\n')
	else:
		print(f'run_query error:\n{data}')
		exit()
	status, data = exec_query('db test', '', test=True)
	if status:
		print(f'Test number of records: {data}')
	else:
		print(f'exec_query error:\n{data}')
