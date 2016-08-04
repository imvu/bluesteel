""" Presenter views, Html BluesteelWorker page functions """

import os
import zipfile
import json
from django.conf import settings
from django.http import HttpResponse
from app.logic.httpcommon import res
from app.presenter.views.helpers import ViewUrlGenerator

def zip_folder_and_return_path(path_to_compress, path_destination, name_destination, settings_obj):
    """ Compress a folder and return the path of the resulting zip file """
    if not os.path.exists(path_destination):
        os.makedirs(path_destination)

    path_final = os.path.join(path_destination, name_destination)

    rel_root = os.path.abspath(path_to_compress)
    with zipfile.ZipFile(path_final, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(os.path.join('core', 'settings.json'), json.dumps(settings_obj))
        for root, dirs, files in os.walk(path_to_compress):
            del dirs
            zip_file.write(root, os.path.relpath(root, rel_root))
            for fil in files:
                file_name = os.path.join(root, fil)
                if os.path.isfile(file_name) and file_name.endswith('.py'):
                    archive_name = os.path.join(os.path.relpath(root, rel_root), fil)
                    zip_file.write(file_name, archive_name)

    return path_final

def get_worker(request):
    """ Returns the worker scripts compressed in a zip file """
    if request.method == 'GET':
        settings_obj = {}
        settings_obj['entry_point'] = ViewUrlGenerator.get_worker_entry_point_full_url(request.get_host())
        settings_obj['tmp_path'] = ['..', 'tmp', 'worker_tmp']

        path_final = zip_folder_and_return_path(
            os.path.join(settings.BASE_DIR, '..', 'app', 'logic', 'bluesteelworker', 'download'),
            os.path.join(settings.TMP_ROOT, 'zip'),
            'BluesteelWorker.zip',
            settings_obj
        )

        myfile = open(path_final)

        response = HttpResponse(myfile.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=BluesteelWorker.zip'
        myfile.close()
        return response
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
