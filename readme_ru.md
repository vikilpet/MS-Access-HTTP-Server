﻿<p align="center">
	<img src="https://i2.imageban.ru/out/2019/08/28/3bfe6d67ba91d57e27dfb3a5bb7072e5.png">
</p>

Получение данных из Microsoft Access базы в с помощью HTTP запроса. Формат выходных данных: JSON, CSV, HTML. Также можно выполнять запросы на добавление, изменение, обновление данных.
<!--more-->
Исходный код: [https://github.com/vikilpet/MS-Access-HTTP-Server](https://github.com/vikilpet/MS-Access-HTTP-Server)

Пример JSON-выдачи:
<p align="center">
	<img src="https://i3.imageban.ru/out/2019/08/28/697acf81efae57c4c0633e182b8bc183.png">
</p>

Добавление записи:
<p align="center">
	<img src="https://i3.imageban.ru/out/2019/08/28/e59b7252a23e991e4b1f9592fa5b6663.png">
</p>

## Использование
Запускаете http_query.py, вбиваете в браузер URL:
```
http://127.0.0.1:80/db_test?mime=html&headers=true&sql=SELECT TOP 3 * FROM Suppliers
```
Параметры:
- *mime* - формат выдачи (html, json или csv).
- *headers* - заголовки столбцов.
- *sql* - собственно запрос. Когда будете формировать запросы в вашем приложении, не забудьте [преобразовать в URL-совместимый формат](https://en.wikipedia.org/wiki/Percent-encoding)

## Установка
**Требования**: Windows 7 и выше, Python 3.7
Скачивайте проект, устанавливаете зависимости: *pip install -r requirements.txt*
Правите настройки в settings.ini

Секция **web server** - настройки для HTTP-сервера.
- *bind_ip* - локальный IP адрес, к которому привязывается сервер. По умолчанию это 127.0.0.1, т.е. сервер будет отвечать только на запросы, поступившие с этого же компьютера.
- *white_list* - список IP адресов через запятую, с которых разрешены подключения.

Затем нужно добавить базы данных. Каждая база данных (mdb или accdb файл) это отдельная секция с уникальным названием. Настройки:
- *db* - полный путь к файлу.
- *driver* - название ODBC драйвера.
- *uid* - пользователь.
- *pwd* - пароль, если требуется.
- *systemdb* - .mdw файл, если требуется.

Опционально можно добавить тестовые запросы, которые будут выполняться при запуске msaccess.py:
- *test_run* - SQL запрос на выборку (SELECT).
- *text_exec* - SQL запрос на добавление/изменение/удаление (INSERT/UPDATE/DELETE).
