import os
from os import path
import glob
import csv
from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from werkzeug.exceptions import abort

from tad_uploader.auth import login_required
from tad_uploader.db import get_db

bp = Blueprint('uploader', __name__)


@bp.route('/')
def index():
    return render_template('uploader/index.html')


@bp.route('/image_uploader', methods=['GET', 'POST'])
@login_required
def image_uploader():
    image_names = os.listdir('tad_uploader/static/uploads/images')
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join('tad_uploader/static/uploads/images', f.filename))
    return render_template('uploader/image_upload.html', image_names=image_names)


@bp.route('/delete_latest_image', methods=['GET', 'POST'])
@login_required
def delete_latest_image():
    if os.listdir('static/uploads/images/'):
        list_of_files = glob.glob('tad_uploader/static/uploads/images/*')  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        os.remove(latest_file)
    return redirect(url_for('uploader.image_uploader'))


@bp.route('/delete_all', methods=['GET', 'POST'])
@login_required
def delete_all():
    list_of_files = glob.glob('tad_uploader/static/uploads/images/*')
    if os.listdir('static/uploads/images'):
        for f in list_of_files:
            os.remove(f)
    else:
        print("Directory is empty")
    return redirect(url_for('uploader.image_uploader'))


@bp.route('/get/img/<img_to_delete>', methods=['GET', 'POST'])
@login_required
def delete_image(img_to_delete):
    os.remove('tad_uploader/static/uploads/images/' + img_to_delete)
    return redirect(url_for('uploader.image_uploader'))


@bp.route('/csv_uploader', methods=['GET', 'POST'])
@login_required
def csv_uploader():
    csvs = os.listdir('tad_uploader/static/uploads/csv')
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join('tad_uploader/static/uploads/csv', f.filename))
        with open('tad_uploader/static/uploads/csv/' + f.filename, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(int(row['Contributor ID']), row['Title of Photo'], row['Rights Statement'])
        # read csv and save it to model python csv reader with for loop -> create a new instance of model
    return render_template('uploader/csv_upload.html', csvs=csvs)


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
    os.remove('tad_uploader/static/uploads/csv/' + csv_to_delete)
    return redirect(url_for('uploader.csv_uploader'))