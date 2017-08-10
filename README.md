fullstack-nanodegree-vm
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

# Catalog Project 
 by Hai Vo

# Description
results = URI
Home page = / and catalog/ \n
filter items = catalog/Snowboarding/items \n
item description = catalog/Snowboarding/Snowboard \n
add item (login require) = catalog/Snowboard/edit \n
delete item (login require) = catalog/Snowboard/delete \n
api call = catalog.json \n

# How To Run
Setup the vagrant \n
go to the catalog folder \n
run `python catalog_server.py` \n

Note: if you want to setup the db again \n
remove or backup the categoryProject.db \n
in the catalog folder \n
run `python db_manager.py` \n
if you want sample data \n
run `python dbSetup.py` \n
