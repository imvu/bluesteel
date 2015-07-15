""" Presenter views, layout page functions """

from django.conf import settings
from django.http import HttpResponse
from django.middleware import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from app.service.strongholdworker.models.WorkerModel import WorkerEntry
from app.service.strongholdworker.views import WorkerSchemas
from app.util.httpcommon import res
from app.util.httpcommon import val
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
            if file_entry.endswith('.py'):
                zip_file.write(os.path.join(root, file_entry), os.path.basename(file_entry))
    zip_file.close()
    return path_final

def is_username_registered(username):
    """ Returns true or false if the user is registered inside DB"""
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    return True


def get_worker(request):
    """ Returns the worker scripts compressed in a zip file """
    if request.method == 'GET':
        path_final = zip_folder_and_return_path(
            os.path.join(settings.BASE_DIR, '..', 'app', 'service', 'strongholdworker', 'download'),
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

def get_worker_info(request, worker_uuid):
    if request.method == 'GET':
        worker = WorkerEntry.objects.all().filter(uuid=worker_uuid).first()

        obj = {}
        obj['csrf_token'] = csrf.get_token(request)

        if worker == None:
            return res.get_response(400, 'Worker not found', obj)
        else:
            obj['worker'] = worker.as_object()
            return res.get_response(200, 'Worker found', obj)
    else:
        return res.get_only_get_allowed({})


@csrf_exempt
def create_worker_info(request):
    if request.method == 'POST':
        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, WorkerSchemas.CREATE_WORKER_INFO_SCHEMA)
        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        obj = val_resp_obj

        worker = WorkerEntry.objects.all().filter(uuid=obj['uuid']).first()
        if worker == None:
            if is_username_registered(obj['uuid']):
                return res.get_response(405, 'Worker not found but user already present!', {})
            else:
                user = User.objects.create_user(
                    username=obj['uuid'][:30],
                    email=None,
                    password=obj['uuid']
                )
                user.save()

                new_worker = WorkerEntry.objects.create(
                    uuid=obj['uuid'],
                    name=obj['host_name'],
                    operative_system=obj['operative_system'],
                    user=user
                )
                new_worker.save()

                return res.get_response(200, 'Worker created succesfuly!', new_worker.as_object())
        else:
            return res.get_response(405, 'Worker already created', {})
    else:
        return res.get_only_post_allowed({})


def login_worker_info(request):
    if request.method == 'POST':
        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, obj) = val.validate_obj_schema(post_info, WorkerSchemas.LOGIN_WORKER_SCHEMA)
        if not obj_validated:
            return res.get_schema_failed(obj)

        user = authenticate(username=obj['username'], password=obj['password'])
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                return res.get_response(200, 'Access granted!', {})
            else:
                return res.get_response(200, 'The password is valid, but the account has been disabled!', {})
        else:
            # the authentication system was unable to verify the username and password
            return res.get_response(401, 'Access denied!', {})
    else:
        return res.get_only_post_allowed({})

