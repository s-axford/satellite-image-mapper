# Satellite Image Mapper
## Build and Run using Docker
Build the image:
```
docker build -t satmap:latest .
```
The image can now be run as a container:
```
docker run -d -p ${desired host port}:3000 satmap
```
The web interface will be available at localhost:${desired host port}
## API Usage
Generated satellite image files can be obtained via the satmap API using a multipart/form-data GET request

Form data should include:
```
lat: Latitude of desired location (-90 to 90)
long: Longitude of desired location (-180 to 180)
file: local filepath of png image containing overlay
```
cURL Example:
```
curl -X GET http://localhost:${desired host port}/satmap/api/v1.0/generate   
-H 'Content-Type: multipart/form-data'   
-H 'content-type: multipart/form-data; 
boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'   
-F lat=45.5168
-F long=-73.5788
-F file=@{PATH_TO_IMAGES_FOLDER}/plume.png -o response.png
```
## Unit Tests
Unit tests can be run on the API to confirm functionality

To run all unit tests, run the following command in the app/ directory:
```
python3 -m unittest discover
```
To evaluate satmap test coverage, install coverage package, run the unit tests, and generate a report in the app/ directory:
```
pip3 install coverage
coverage run test_satmap.py
coverage report test_satmap.py
```

## Generating Sphinx Documentation
First install Sphinx for your operating system, instructions can be found in the [Sphinx documentation](http://www.sphinx-doc.org/en/master/usage/installation.html "Sphinx Installation")

Once Sphinx is installed the documentation can be generated using the Makefile in the doc/ directory

To generate the documentation as an html page enter the doc/ directory and run:
```
make html
```
Other documentations form factors can be generated similarly:
```
make {text || latex || xml || ..etc}
```
For more information on possible Sphinx documentation types refer to the [Sphinx build documentation](http://www.sphinx-doc.org/en/master/man/sphinx-build.html "sphinx-build")
