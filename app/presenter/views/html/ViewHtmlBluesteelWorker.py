""" Presenter views, Html BluesteelWorker page functions """

from django.conf import settings
from django.http import HttpResponse
from app.logic.httpcommon import res
import os
import zipfile

def zip_folder_and_return_path(path_to_compress, path_destination, name_destination):
    """ Compress a folder and return the path of the resulting zip file """
    if not os.path.exists(path_destination):
        os.makedirs(path_destination)

    path_final = os.path.join(path_destination, name_destination)
    zip_file = zipfile.ZipFile(path_final, 'w')

    for root, dirs, files in os.walk(path_to_compress):
        del dirs
        for file_entry in files:
            if file_entry.endswith('.py') or file_entry.endswith('.json'):
                zip_file.write(os.path.join(root, file_entry), os.path.basename(file_entry))
    zip_file.close()
    return path_final

def get_worker(request):
    """ Returns the worker scripts compressed in a zip file """
    if request.method == 'GET':
        path_final = zip_folder_and_return_path(
            os.path.join(settings.BASE_DIR, '..', 'app', 'logic', 'bluesteelworker', 'download'),
            os.path.join(settings.TMP_ROOT, 'zip'),
            'BluesteelWorker.zip'
        )

        myfile = open(path_final)

        response = HttpResponse(myfile.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=BluesteelWorker.zip'
        myfile.close()
        return response
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
