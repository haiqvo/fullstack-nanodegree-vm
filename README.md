fullstack-nanodegree-vm
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

# Catalog Project 

# Description
results = URI
Home page = / and catalog/
filter items = catalog/Snowboarding/items
item description = catalog/Snowboarding/Snowboard
add item (login require) = catalog/Snowboard/edit
delete item (login require) = catalog/Snowboard/delete
api call = catalog.json

# How To Run
Setup the vagrant 
go to the catalog folder
run `python catalog_server.py`

Note: if you want to setup the db again
remove or backup the categoryProject.db
in the catalog folder
run `python db_manager.py`
if you want sample data
run `python dbSetup.py`
