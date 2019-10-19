"""
.. module:: satmap
   :synopsis: All endpoints of the SatMap API are defined here
.. moduleauthor:: Spencer Axford
"""
import os
import requests
import googlemaps
from PIL import Image
from flask import Flask, render_template, request, redirect, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# file extensions that are allowed by the file form fields
ALLOWED_EXTENSIONS = set(['png'])

# directory setup for easy referencing
cur_path = os.path.dirname(__file__)
IMAGES_FOLDER = os.path.join(cur_path, 'static/images')
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

# google maps API key
api_key = 'AIzaSyAwFrztsxrcARTjOhchUXuCunYiC3e2WJ4'

# url variable store url
gmaps_url = "https://maps.googleapis.com/maps/api/staticmap?"

# zoom defines the zoom level of the map
# roughly 10km x 5km in Montreal Latitude
# TODO provide better calculation for zoom level
zoom = 13


def allowed_file(filename):
    # checks if uploaded file is of allowed extension type
    # filename: string representing filename
    # returns boolean
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def generate_overlay_image(latitude, longitude, file):
    # fetchs static satellite image at specified latitude and longitude
    # overlays given werkzeug file object on satellite image
    # saves new file to static/images and returns filename
    # latitude: number (between -90 and 90) latitude for center of image
    # longitude: number (between -180 and 180) longitude for center of image
    # file: werkzeug file object (image/png) that will be overlayed on google maps image
    # returns filename of new image stored in static/images, or throws
    # exception

    # center defines the center of the map
    center = "{},{}".format(latitude, longitude)

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        print('Must Select File')
        raise FileNotFoundError('Must Select File')

    # ensures file is a png of proper format
    if not file or not allowed_file(file.filename):
        print('File not valid')
        raise TypeError('File Not Valid')
    else:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['IMAGES_FOLDER'], filename))

    # get url to image of lat long specified location from google maps api
    map_image = requests.get(gmaps_url + "center=" + center + "&zoom=" +
                             str(zoom) + "&size=514x257&key=" +
                             api_key + "&sensor=false" + "&maptype=satellite")

    # save map file to images folder
    f = open(os.path.join(app.config['IMAGES_FOLDER'], "map.png"), 'wb')
    f.write(map_image.content)
    f.close()

    # open both files as Image objects
    background = Image.open(
        os.path.join(
            app.config['IMAGES_FOLDER'],
            "map.png"))
    overlay = Image.open(
        os.path.join(
            app.config['IMAGES_FOLDER'],
            filename))

    # maintain alpha channels
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    # overlay uploaded image on top of gmaps image
    new_img = Image.alpha_composite(background, overlay)

    # generate informative name for new file
    new_img_filename = os.path.splitext(
        filename)[0] + '-' + latitude + "-" + longitude + ".png"

    # save new file for witth generated file name
    new_img.save(os.path.join(app.config['IMAGES_FOLDER'], new_img_filename))

    return new_img_filename


@app.route('/')
def index():
    # default route with GHGSat Montreal office cordinates as defaults
    return render_template('index.html', lat="45.5168", long="-73.5788")


@app.route('/', methods=['POST'])
def handle_data():
    # default route POST handler for form data

    # get lat long
    latitude = request.form['lat']
    longitude = request.form['long']

    # get uploaded file
    # check if the post request has files
    if 'file' not in request.files:
        print('No file portion of request')
        return render_template('index.html', lat=latitude, long=longitude)
    file = request.files['file']
    print(file)

    # try to get filename of overlayed imaged
    try:
        new_img_filename = generate_overlay_image(latitude, longitude, file)
    # user did not input a file
    except FileNotFoundError as error:
        print(error)
        return render_template('index.html', error='Must Select File', lat=latitude, long=longitude)
    # user inputted a file that does not conform to API
    except TypeError as error:
        print(error)
        return render_template('index.html', error='File Not Valid', lat=latitude, long=longitude)

    return render_template(
        'index.html',
        lat=latitude,
        long=longitude,
        image_created='true',
        filename=(
            'images/' +
            new_img_filename))


@app.route('/satmap/api/v1.0/generate', methods=['GET'])
def generate_image():
    # SatMap API which collects a longitude, latitude and png image
    # returns new image of request image overlayed with google maps static
    # image at given cordinates
    """
        **Generate Satellite Image File**

        This function allows users to upload and image with latitude and longitude information

        :return: uploaded image overlayed a static google maps api image taken at specified cordinates

        - Example::

            curl -X GET http://localhost:{specified_port}/satmap/api/v1.0/generate

            -H 'Content-Type: multipart/form-data'

            -H 'content-type: multipart/form-data;

            boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'

            -F lat=45.516884

            -F long=-73.578823

            -F file=@{PATH_TO_IMAGES_FOLDER}/plume.png -o response.png

        - Expected Success Response::

            HTTP Status Code: 200

            body: image/png
    """
    # get lat long
    latitude = request.form['lat']
    longitude = request.form['long']

    # get uploaded file
    # check if the post request has files
    if 'file' not in request.files:
        print('No file portion of request')
        return jsonify({'error': 'No file portion of request'})
    file = request.files['file']

    # try to get filename of overlayed imaged
    try:
        new_img_filename = generate_overlay_image(latitude, longitude, file)
    # user did not input a file
    except FileNotFoundError as error:
        print(error)
        return jsonify({'error': 'Must Send File'})
    # user inputted a file that does not conform to API
    except TypeError as error:
        print(error)
        return jsonify({'error': 'File Not Valid'})

    return send_file(
        os.path.join(
            app.config['IMAGES_FOLDER'],
            new_img_filename),
        mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
