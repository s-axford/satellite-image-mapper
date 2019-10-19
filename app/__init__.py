import os
import requests
import googlemaps
from PIL import Image
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

# file extensions that are allowed by the file form fields
ALLOWED_EXTENSIONS = set(['png'])

# directory setup for easy referencing
cur_path = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(cur_path, 'static/images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# default route
@app.route('/')
def index():
    return render_template('index.html')

# default route post handler for form data
@app.route('/', methods=['POST'])
def handle_data():
    # get lat long
    print(request)
    latitude = request.form['lat']
    longitude = request.form['long']

    # center defines the center of the map
    center = latitude + "," + longitude

    # get uploaded file
    # check if the post request has files
    if 'file' not in request.files:
        print('No file portion of request')
        return render_template('index.html')
    file = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        print('Must Select File')
        return render_template('index.html', error='Must Select File')

    # ensures file is a png of proper format
    if not file or not allowed_file(file.filename):
        print('File not valid')
        return render_template('index.html', error='File Not Valid')
    else:
        filename = secure_filename(file.filename)
        print(file)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # get url to image of lat long specified location from google maps api
    map_image = requests.get(gmaps_url + "center=" + center + "&zoom=" +
                             str(zoom) + "&size=514x257&key=" +
                             api_key + "&sensor=false" + "&maptype=satellite")

    # save map file to images folder
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], "map.png"), 'wb')
    f.write(map_image.content)
    f.close()

    # open both files as Image objects
    background = Image.open(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            "map.png"))
    overlay = Image.open(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename))

    # maintain alpha channels
    background = background.convert("RGBA")
    overlay = overlay.convert("RGBA")

    # generate informative name for new file
    new_img_filename = os.path.splitext(
        filename)[0] + '-' + latitude + "-" + longitude + ".png"

    # overlay uploaded image on top of gmaps image
    new_img = Image.alpha_composite(background, overlay)
    new_img.save(os.path.join(app.config['UPLOAD_FOLDER'], new_img_filename))

    return render_template(
        'index.html',
        lat=latitude,
        long=longitude,
        image_created='true',
        filename=(
            'images/' +
            new_img_filename))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
