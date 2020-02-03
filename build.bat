echo off

if "X%1" == "X" (
	echo build
	goto build
) else if "%1" == "-b" (
	echo build
	goto build
) else if "%1" == "-c" (
	echo clean
	goto clean
) else if "%1" == "-s" (
	echo setup_virtual_env
	goto setup_virtual_env
) else if "%1" == "-d" (
	echo delete_virtual_env
	goto delete_virtual_env
) else goto help

goto end

:help
	echo -b or no param : Build
	echo -c             : Clean Build
	echo -s             : Re-setup virtual enviroment
	echo -d             : Delete virtual enviroment
	goto end

:delete_virtual_env
	pipenv --rm
	goto end


:setup_virtual_env
	pipenv --rm

	pipenv install
	pipenv shell

	pip install pandas
	pip install pyqt5
	pip install tushare
	pip install bs4
	pip install pymongo
	pip install requests
	pip install openpyxl

	pip uninstall pyinstaller
	pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
	
	goto end


:build
	del main.spec
	rmdir /s /q dist
	rmdir /s /q build
	
	pyi-makespec --hidden-import pandas --icon="res/logo.ico" main.py
	Rem pyi-makespec -w --hidden-import pandas --icon="res/logo.ico" main.py

	pyinstaller main.spec

	xcopy  Data dist/main/Data /e /i /h
	xcopy  Analyzer dist/main/Analyzer /e /i /h
	xcopy  Collector dist/main/Collector /e /i /h
	
	goto end


:clean
	del main.spec
	rmdir /s /q dist
	rmdir /s /q build
	goto end

:end
	echo End...
	pause






