# Satellite Image Mapper
## Build and Run Using Docker
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
long: Longitude of desured location (-180 to 180)
file: local filepath of png image containing overlay
```
cURL Example:
```
curl -X GET http://localhost:3000/satmap/api/v1.0/generate   
-H 'Content-Type: multipart/form-data'   
-H 'content-type: multipart/form-data; 
boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'   
-F lat=45.516884   
-F long=-73.578823   
-F file=@{PATH_TO_FILE}/plume.png -o response.png
```
