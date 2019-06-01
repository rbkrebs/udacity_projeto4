# Catalog App Project

This is the fourth project of Full Stack Web Developer Nanodegree Program from `Udacity`.

## About

According to `Udacity` "*The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.*"

## Configuration

Yuo must have installed on your computer:

* [Vagrant](https://github.com/udacity/fullstack-nanodegree-vm); (*You can clone ou download this project*)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads);
* [Python 2.7](https://www.python.org/downloads/);
* [Google Account](https://myaccount.google.com/);


## Run

To run this project follow the next steps forward:

1. Clone the directory or download as a zip file. If you downloaded, unpack the zip first.
2. Navigate to the directory cd repository_name or folder name.
3. Inside the repository or folder, run:

```
vagrant up
vagrant ssh
cd /vagrant
python database_setup.py
python app.py
```
4. Open a web browser and type:
```
http://localhost:5000
```
## JSON Endpoints

This endpoint will return all the categories and its items recorded on database.

```
http://localhost:/templates/catalog/JSON
```
This endpoint will return all items from a specific category recorded on database.

```
http://localhost:/templates/catalogitems/integer/JSON
```
where *integer* is the number of the category, for exemple

```
http://localhost:/templates/catalogitems/1/JSON
```

## License

This project is under [MIT License](https://opensource.org/licenses/MIT)

