# Upload and download CSV data to a database

## About this application
With this web application, you can upload a CSV file to a SQL database and download the data back to a CSV file. The application is written in Python and built on the Flask web framework. The web pages are styled with Bootstrap CSS. The database interface uses the SQLAlchemy package and can use any database implementation that SQLAlchemy supports. Currently the application is set up to use a sqlite database in the local file system.

Note: the application is ready to deploy to the Amazon Web Services (AWS) Relational Database Service (RDS): 
1. In `config.py`, fill in the AWS RDS database information, uncomment the designated code, and comment or remove the old database code. 
1. Execute `db_create.py` to initialize the database.

This application creates a new table in the database for each uniquely named CSV file. This allows analysts to access and manipulate the dataset in its own table via SQL should they so wish. The database consists of a lookup table which keeps track of the dataset tables, a built-in SQLAlchemy table, and the individual dataset tables. The only limits to the number of rows and number of columns are those of the database implementation. 

Details about the automatic table creation mechanism:
1. The table name is the filename, without the .csv extension.
1. The table name and column names are reformatted to conform to SQL requirements.
1. The column names must be valid for a table (e.g., there can't be duplicate column names).
1. The first column of data is automatically designated the primary key for the table, with the assumption that it is something like an identifier.
1. If another CSV file with the same name is uploaded, the application will attempt to INSERT any unique rows to the corresponding table. If not all rows are unique, it will report "partial success." 
1. All columns are VARCHAR columns by default. This can be changed with an ALTER TABLE command, if desired.
1. To prevent SQL injection attacks, INSERTs use parameter binding. A side effect of this is that if the data in a cell looks like an injection attack (e.g., has quotes), the SQLAlchemy engine will automatically escape the data, adding extra quotes. To avoid the extra escaping, this behavior can be changed if you totally trust all the data.

There are two pages: 
* Upload: Where you can upload CSV files. This is also the home page.
* Download: Where you can download a dataset from the displayed list of all the datasets in the database.

## How to run this application locally
1. Download or clone this repository.
1. In the repository directory, to make sure the requirements are met, run: `pip install -r requirements.txt` Alternatively, if you don't want to change the versions you have in your Python installation, you can create your own environment (e.g., with virtualenv), or just go through requirements.txt and make sure each package is installed: `pip install SQLAlchemy` `pip install Flask` `pip install Flask-SQLAlchemy` `pip install pymysql`
1. Run `python application.py` to start the Flask web server.
1. Point your browser to `http://localhost:5555`

## About the modules
`config.py` Configuration information for the database and Flask web server.

`views.py` Routes for the web server.

`models.py` Model for the table index (the table that keeps track of the dataset tables) for SQLAlchemy.

`dblib.py` The interface with the database. This is the only module that interacts directly with the database.

`uploader.py` Uploading functions. Pre-processes (a little) the data and saves data to the database via dblib.

`downloader.py` Downloading functions. Retrieves a dataset from the database via dblib and converts it to a CSV file.

