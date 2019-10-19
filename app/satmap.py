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

# checks if uploaded file is of allowed extension type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def generate_overlay_image(latitude, longitude, file):
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

# default route
@app.route('/')
def index():
    return render_template('index.html')

# default route post handler for form data
@app.route('/', methods=['POST'])
def handle_data():
    # get lat long
    latitude = request.form['lat']
    longitude = request.form['long']

    # get uploaded file
    # check if the post request has files
    if 'file' not in request.files:
        print('No file portion of request')
        return render_template('index.html')
    file = request.files['file']
    print(file)

    # try to get filename of overlayed imaged
    try:
        new_img_filename = generate_overlay_image(latitude, longitude, file)
    # user did not input a file
    except FileNotFoundError as error:
        print(error)
        return render_template('index.html', error='Must Select File')
    # user inputted a file that does not conform to API
    except TypeError as error:
        print(error)
        return render_template('index.html', error='File Not Valid')

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
