import os
from os import path
import glob
import json
import csv
import requests
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .models import Image
from tad_uploader import db

from werkzeug.exceptions import abort

from tad_uploader.auth import login_required

bp = Blueprint('uploader', __name__)


@bp.route('/')
def index():
    return render_template('uploader/index.html')


@bp.route('/image_uploader', methods=['GET', 'POST'])
@login_required
def image_uploader():
    image_names = os.listdir('tad_uploader/static/uploads/images')
    image_infos = []
    if image_names:
        for image in image_names:
            image_id = image.split(" - ")[0]
            image_info = Image.query.filter_by(contributor_id=image_id).first()
            print(image_info)
            image_info.path = "uploads/images/" + image
            db.session.commit()
            image_infos.append(image_info)
    if request.method == 'POST':
        f = request.files.get('file')
        if f.filename.split(" - ")[0].isdigit():
            f.save(os.path.join('tad_uploader/static/uploads/images', f.filename))
        else:

            return 'error', 500
    return render_template('uploader/image_upload.html', image_names=image_names, image_infos=image_infos)


@bp.route('/delete_latest_image', methods=['GET', 'POST'])
@login_required
def delete_latest_image():
    if os.listdir('static/uploads/images/'):
        list_of_files = glob.glob(
            'tad_uploader/static/uploads/images/*')  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        os.remove(latest_file)
    return redirect(url_for('uploader.image_uploader'))


@bp.route('/delete_all', methods=['GET', 'POST'])
@login_required
def delete_all():
    list_of_csvs = glob.glob('tad_uploader/static/uploads/csv/*')
    if os.listdir('tad_uploader/static/uploads/csv'):
        for f in list_of_csvs:
            os.remove(f)
    else:
        print("Directory is empty")
    list_of_images = glob.glob('tad_uploader/static/uploads/images/*')
    if os.listdir('tad_uploader/static/uploads/images'):
        for f in list_of_images:
            os.remove(f)
    else:
        print("Directory is empty")
    db.session.query(Image).delete()
    db.session.commit()
    print("The database has been cleared")
    return redirect(url_for('uploader.csv_uploader'))


@bp.route('/get/static/<path:img_to_delete>', methods=['GET', 'POST'])
@login_required
def delete_image(img_to_delete):
    # delete file from database
    '''
    # outcommented cause makes no sense in this context. Deleting the db entry would cause problems in image_uploader
    query by contributer_id since the image info would be deleted. To fix this we would have to call the csv_uploader
    after each delete -> would not make sense. Better approach is to just delete the image from the folder -> check before
    sending to ArchivesSpace if the image has the info AND is in the folder and delete everything from db after an upload.

    image_id = img_to_delete.split(" - ")[0].rsplit('/', 1)[-1]
    Image.query.filter_by(contributor_id=image_id).delete()
    db.session.commit()
    '''
    os.remove('tad_uploader/static/' + img_to_delete)
    return redirect(url_for('uploader.image_uploader'))


@bp.route('/csv_uploader', methods=['GET', 'POST'])
@login_required
def csv_uploader():
    images = []
    csvs = os.listdir('tad_uploader/static/uploads/csv')
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join('tad_uploader/static/uploads/csv', f.filename))
        with open('tad_uploader/static/uploads/csv/' + f.filename, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if "Contributor ID" in row and "Title of Photo" in row and "Rights Statement" in row:
                    new_image = Image(contributor_id=int(row['Contributor ID']), title=row['Title of Photo'],
                                      rights=row['Rights Statement'])
                    db.session.add(new_image)
                    db.session.commit()
                    images.append({'Contributor ID': row['Contributor ID'],
                                   'Title': row['Title of Photo'],
                                   'Rights Statement': row['Rights Statement']})
                else:
                    list_of_files = glob.glob(
                        'tad_uploader/static/uploads/csv/*')  # * means all if need specific format then *.csv
                    latest_file = max(list_of_files, key=os.path.getctime)
                    os.remove(latest_file)
                    return 'The CSV does not have one or more of the required rows: Contributor ID, ' \
                           'Title of Photo, Rights Statement', 400
        # read csv and save it to model python csv reader with for loop -> create a new instance of model
    return render_template('uploader/csv_upload.html', csvs=csvs, images=images)


@bp.route('/delete_csv', methods=['GET', 'POST'])
@login_required
def delete_latest_csv():
    if os.listdir('tad_uploader/static/uploads/csv/'):
        list_of_files = glob.glob('tad_uploader/static/uploads/csv/*')  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        os.remove(latest_file)
    else:
        print("You haven't uploaded anything")
    return redirect(url_for('uploader.csv_uploader'))


@bp.route('/get/csv/<csv_to_delete>', methods=['GET', 'POST'])
@login_required
def delete_csv(csv_to_delete):
    with open('tad_uploader/static/uploads/csv/' + csv_to_delete, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Image.query.filter_by(contributor_id=int(row['Contributor ID'])).delete()
            db.session.commit()
    os.remove('tad_uploader/static/uploads/csv/' + csv_to_delete)
    return redirect(url_for('uploader.csv_uploader'))


@bp.route('/all_images')
def get_images():
    images = Image.query.all()
    # Image.query.get_or_404(id)
    # .get_or_404
    return render_template('view_images.html', images=images)


''''
@app.route('/identifier/<path:identifier>')
def view_identifier(identifier):
    obj = Identifier.query.get_or_404(identifier)
'''''

# starting with the upload

# DSPACE Credentials

api_base_url = "http://test.digitalpreservation.is.ed.ac.uk/"
endpoint_path = "/rest/login"
endpoint = "{}{}".format(api_base_url, endpoint_path)
ds_collection = "b8ef34ee-1b49-460b-8fe4-00a39d9a737d"
ds_user = "slange@exseed.ed.ac.uk"
ds_password = "d1gitalpr3servation!"

login_data = {
    "email": ds_user,
    "password": ds_password
}

headers = {
    'Content-Type': 'application/json', 'Accept': 'application/json'
}

# Login to ArchivesSpace and return SessionID

as_base_url = "http://lac-archives-test.is.ed.ac.uk"
as_user = "admin"
as_password = "t0tt3nh@m"
as_archival_repo = "18"
as_url_port = "8089"


def login_to_dspace():
    response = requests.post(endpoint, data=login_data)
    set_cookie = response.headers["Set-Cookie"].split(";")[0]
    session_id = set_cookie[set_cookie.find("=") + 1:]
    print(session_id)
    return session_id


def as_login():
    files = {
        'password': (None, as_password),
    }
    response = requests.post(f"{as_base_url}:{as_url_port}/users/{as_user}/login", files=files)
    print(response.json()['session'])
    return response.json()['session']


def format_metadata(key, value, lang="en"):
    """Reformats the metadata for the REST API."""
    return {'key': key, 'value': value, 'language': lang}


def create_dspace_record(metadata, ds_collection, session_id):
    item = {"type": "item", "metadata": metadata}  #
    collection_url = "{}/rest/collections/{}/items".format(api_base_url, ds_collection)
    response = requests.post(collection_url,
                             cookies={"JSESSIONID": session_id},
                             data=json.dumps(item),
                             headers=headers
                             )
    response.raise_for_status()
    response_object = response.json()
    print(f'this is the response object {response_object}')
    return response_object


# Uploads the image into the DSPACE object
def upload_image(ds_object_link, image_to_upload, ds_object_tag):
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    with open("tad_uploader/static/" + image_to_upload, 'rb') as content:
        ds_object_tag = str(ds_object_tag) + ".jpg"
        print(ds_object_tag)
        requests.post("{}/{}/bitstreams?name={}".format(api_base_url, ds_object_link, ds_object_tag),
                      data=content,
                      headers=headers,
                      cookies={"JSESSIONID": login_to_dspace()})
        print(f"image with the id: {ds_object_tag} successfully uploaded")


def get_as_agent(as_base_url, as_url_port, as_session_id, agent_id):  # use image_id as agent_id as they are the same
    link_to_agent = f'{as_base_url}:{as_url_port}/agents/people/{agent_id}'
    as_headers = {
        'X-ArchivesSpace-Session': as_session_id
    }
    response = requests.get(link_to_agent, as_headers)
    as_agent = response.json()
    return as_agent


def update_as_agent(as_base_url, as_url_port, as_session_id, agent_id, as_agent, link_to_image, rights_statement):
    link_to_agent = f'{as_base_url}:{as_url_port}/agents/people/{agent_id}'
    as_headers = {
        'X-ArchivesSpace-Session': as_session_id
    }
    as_agent['notes'][0]['label'] = "Image"
    as_agent['notes'][0]['subnotes'][0]['content'] = "<img src='{}.jpg'/>".format(link_to_image)
    as_agent['notes'].append({'jsonmodel_type': 'note_bioghist', 'label': 'Image Rights', 'publish': False,
                              'subnotes': [
                                  {'content': rights_statement, 'jsonmodel_type': 'note_text', 'publish': False}]})
    response = requests.post(link_to_agent, headers=as_headers, data=json.dumps(as_agent))
    print(response.status_code)


@bp.route('/upload_to_as', methods=['GET', 'POST'])
@login_required
def upload_to_as():
    ds_session_id = login_to_dspace()
    as_session_id = as_login()
    images = Image.query.all()
    for image in images:
        if image.title and image.contributor_id and image.rights and image.path:
            image_formatted = [format_metadata("dc.identifier", image.contributor_id),
                               format_metadata("dc.title", image.title),
                               format_metadata("dc.rights", image.rights)
                               ]
            print(image_formatted)
            ds_object = create_dspace_record(image_formatted, ds_collection, ds_session_id)
            upload_image(ds_object['link'], image.path, image.contributor_id)
            link_to_image = "{}/bitstream/handle/{}/{}".format(api_base_url, ds_object['handle'], image.contributor_id)
            as_agent = get_as_agent(as_base_url, as_url_port, as_session_id, image.contributor_id)
            if "notes" in as_agent and as_agent['notes']:
                update_as_agent(as_base_url, as_url_port, as_session_id, image.contributor_id, as_agent, link_to_image,
                                image.rights)
                print(
                    f" the image with the id: {image.contributor_id} and the title: {image.title} with the rights: {image.rights} has been uploaded to {link_to_image}")
            else:
                print(
                    f"The Agent with the id {image.contributor_id} is not in ArchivesSpace or {as_agent} has no label")
    # if condition: upload successfull return successfull page and what is uploaded - if not than what is not uploaded
    # clear db after succesfull upload
    delete_all()
    return redirect(url_for('uploader.csv_uploader'))
