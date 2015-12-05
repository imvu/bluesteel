""" Presenter views, layout page functions """

from django.conf import settings
from django.http import HttpResponse
from django.middleware import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.presenter.schemas import BluesteelWorkerSchemas
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.httpcommon import res
from app.logic.httpcommon import val
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

def get_worker_urls(domain, worker_id):
    """ Returns all the urls associated with a worker """
    obj = {}
    obj['update_activity_point'] = ViewUrlGenerator.get_worker_update_activity_full_url(
        domain,
        worker_id
    )
    return obj

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

def get_worker_info(request, worker_uuid):
    if request.method == 'GET':
        worker = WorkerEntry.objects.all().filter(uuid=worker_uuid).first()

        obj = {}
        obj['csrf_token'] = csrf.get_token(request)

        if worker == None:
            return res.get_response(400, 'Worker not found', obj)
        else:
            ret_worker = worker.as_object()
            ret_worker['last_update'] = str(ret_worker['last_update'])
            ret_worker['url'] = get_worker_urls(request.get_host(), ret_worker['id'])
            obj['worker'] = ret_worker
            return res.get_response(200, 'Worker found', obj)
    else:
        return res.get_only_get_allowed({})


@csrf_exempt
def create_worker_info(request):
    if request.method == 'POST':
        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed(
                {}
            )

        (obj_validated, val_resp_obj) = val.validate_obj_schema(
            post_info,
            BluesteelWorkerSchemas.CREATE_WORKER_INFO_SCHEMA
        )
        if not obj_validated:
            return res.get_schema_failed(val_resp_obj)

        obj = val_resp_obj
        username_trimmed = obj['uuid'][:30]

        worker = WorkerEntry.objects.all().filter(uuid=username_trimmed).first()
        if worker == None:
            user = User.objects.filter(username=username_trimmed).first()
            if not user:
                user = User.objects.create_user(
                    username=username_trimmed,
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

            ret = {}
            ret['worker'] = new_worker.as_object()
            ret['worker']['url'] = get_worker_urls(request.get_host(), ret['worker']['id'])
            ret['worker']['last_update'] = str(ret['worker']['last_update'])

            return res.get_response(200, 'Worker created succesfuly!', ret)
        else:
            return res.get_response(405, 'Worker already created', {})
    else:
        return res.get_only_post_allowed({})


def login_worker_info(request):
    if request.method == 'POST':
        (json_valid, post_info) = val.validate_json_string(request.body)
        if not json_valid:
            return res.get_json_parser_failed({})

        (obj_validated, obj) = val.validate_obj_schema(post_info, BluesteelWorkerSchemas.LOGIN_WORKER_SCHEMA)
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

def update_worker_activity(request, worker_id):
    if request.method == 'POST':
        worker = WorkerEntry.objects.filter(id=worker_id).first()
        if worker:
            worker.save()
            return res.get_response(200, 'Acitivity updated', {})
        else:
            return res.get_response(404, 'Worker not found!', {})
    else:
        return res.get_only_post_allowed({})
