fullstack-nanodegree-vm
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

# Catalog Project 
 by Hai Vo

# Description
results = URI
Home page = / and catalog/ <br />
filter items = catalog/Snowboarding/items <br />
item description = catalog/Snowboarding/Snowboard <br />
add item (login require) = catalog/Snowboard/edit <br />
delete item (login require) = catalog/Snowboard/delete <br />
api call = catalog.json <br />

# How To Run
Setup the vagrant <br />
go to the catalog folder <br />
run `python catalog_server.py` <br />

Note: if you want to setup the db again <br />
remove or backup the categoryProject.db <br />
in the catalog folder <br />
run `python db_manager.py` <br />
if you want sample data <br />
run `python dbSetup.py` <br />
