# # Steps to recreate environment

1 ) Create venv
-		python -m venv env

2 ) Activate venv
- Windows
	- 		.\env\Scripts\activate
- Linux
	- 		source env/bin/activate

3 ) Install dependencies
-		 pip install -r requirements.txt



# # Create executable ( optional )
1 ) pyinstaller command 
-		pyinstaller --onefile --paths=.\env\Lib\site-packages --hidden-import=yaml --hidden-import=tqdm --hidden-import=alive_progress --hidden-import=pyodbc .\main.py

2 ) pyinstall command : linux
		pyinstaller --onefile --paths=./env/lib/python3.9/site-packages --hidden-import=yaml --hidden-import=tqdm --hidden-import=alive_progress --hidden-import=pyodbc ./main.py
