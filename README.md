# face-recognition-web-system
A simple face recognition web system made using OpenCV and Flask
### Prerequisites
This web system was made in ubuntu 20.04 using python 3.7.3, anaconda, flask and openCV (with his dependencies)
### Installing
Using pip to install anaconda, flask and OpenCV with his dependencies.

Dependencies:

```
pip install cmake
pip install numpy scipy matplotlib scikit-learn jupyter
pip install -U numpy scipy scikit-learn
pip install cmake
pip install dlib
pip install imutils

```
OpenCV:

```
pip install opencv-python
```

Flask and extra modules:

```
pip install Flask
pip install flask-mysqldb
pip install mysql-connector-python
pip install pyexcel
```

## Running the system

```
export FLASK_APP=main.py
flask run --host=0.0.0.0
```
Then go to the url: 
http://yourlocalip:5000/pythonlogin/

## Deployment
This system was only tested in Ubuntu 20.04. In windows can cause errors.
Give the project the right permissions.
The SQL Script is in the proyect. Don't forget to change database information in Flask scripts.

## Built With

* [python](https://www.python.org/) - Python site
* [flask](https://flask.palletsprojects.com/en/1.1.x/) - Flask site
* [opencv](https://opencv.org/) - OpenCV site

## Acknowledgments
Base in a chatbot made by [Allan Perez](https://gitlab.com/AHPC1993/chatbot_con_reconocimientofacial)


