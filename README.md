# Upload and download CSV data to a database

## About this application
With this web application, you can upload a CSV file to a SQL database and download the data back to a CSV file. The application is written in Python and built on the Flask web framework. The web pages are styled with Bootstrap CSS. The database interface uses the SQLAlchemy package and can use any database implementation that SQLAlchemy supports. 

The application is ready to deploy to the Amazon Web Services Relational Database Service: 
1. In config.py, fill in the AWS RDS database information and uncomment the designated code. 
1. Execute db_create.py to initialize the database.

The application creates a new table in the database for each uniquely named CSV file. This allows analysts to access and manipulate the dataset in its own table via SQL should they so wish. The only limits to the number of rows and number of columns are those of the database implementation. Some constraints of the automatic table creation:
1. The table name is the filename, without the .csv extension.
1. The table name and column names are reformatted to conform to SQL requirements.
1. The column names must be valid (e.g., there can't be duplicate column names).
1. The first column of data is automatically designated the primary key for the table, with the assumption that it is something like an identifier.
1. If another CSV file with the same name is uploaded, the application will attempt to INSERT any unique rows to the corresponding table. If not all rows are unique, it will report "partial success." 

There are two pages: 
* Upload: Where you can upload CSV files. This is also the home page.
* Download: Where you can download a dataset from the displayed list of all the datasets in the database.
