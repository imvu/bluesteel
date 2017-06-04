""" Presenter views, Json BluesteelWorker functions """

# Duplicate code
# pylint: disable=R0801

from django.db import transaction
from django.middleware import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from app.logic.benchmark.controllers.BenchmarkDefinitionController import BenchmarkDefinitionController
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.bluesteelworker.models.WorkerFilesHashModel import WorkerFilesHashEntry
from app.presenter.schemas import BluesteelWorkerSchemas
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.httpcommon import res
from app.logic.httpcommon import val

def get_entry_points_urls(domain):
    """ Returns bootstrap urls for workers """
    obj = {}
    obj['layouts_url'] = ViewUrlGenerator.get_layout_point_full_url(domain)
    obj['worker_info_url'] = ViewUrlGenerator.get_worker_info_point_full_url(domain)
    obj['worker_files_hash_url'] = ViewUrlGenerator.get_worker_files_hash_full_url(domain)
    obj['worker_download_url'] = ViewUrlGenerator.get_download_worker_full_url(domain)
    obj['create_worker_url'] = ViewUrlGenerator.get_worker_create_point_full_url(domain)
    obj['login_worker_url'] = ViewUrlGenerator.get_worker_login_point_full_url(domain)
    obj['acquire_benchmark_execution_url'] = ViewUrlGenerator.get_acquire_bench_exe_full_url(domain)
    obj['notifications_url'] = ViewUrlGenerator.get_notification_send_all_full_url(domain)
    return obj

def get_worker_urls(domain, worker_id, worker_uuid):
    """ Returns all the urls associated with a worker """
    obj = {}
    obj['update_activity_point'] = ViewUrlGenerator.get_worker_update_activity_full_url(
        domain,
        worker_id
    )
    obj['worker_info_full'] = ViewUrlGenerator.get_worker_info_full_url(domain, worker_uuid)
    return obj

def get_bootstrap_urls(request):
    """ Returns the bootstrap entry urls """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    obj = get_entry_points_urls(request.get_host())
    return res.get_response(200, 'Entry points', obj)

def get_worker_info(request, worker_uuid):
    """ Returns worker info based on uuid """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    worker = WorkerEntry.objects.filter(uuid=worker_uuid).first()

    obj = {}
    obj['csrf_token'] = csrf.get_token(request)

    if worker is None:
        return res.get_response(400, 'Worker not found', obj)

    ret_worker = worker.as_object()
    ret_worker['last_update'] = str(ret_worker['last_update'])
    ret_worker['url'] = get_worker_urls(request.get_host(), ret_worker['id'], ret_worker['uuid'])
    obj['worker'] = ret_worker
    return res.get_response(200, 'Worker found', obj)


def get_worker_files_hash(request):
    """ Returns the hash of all the files of the worker source code """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    worker_files_hash = WorkerFilesHashEntry.objects.all().first()

    if not worker_files_hash:
        return res.get_response(400, 'Worker files hash not found', {})

    obj = {}
    obj['worker_files_hash'] = worker_files_hash.files_hash
    return res.get_response(200, 'Worker files hash', obj)


def get_worker_names_and_ids(request):
    """ Returns the list of all workers plus its ids """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    worker_entries = WorkerEntry.objects.all()

    data = {}
    data['workers'] = []

    for worker in worker_entries:
        obj = {}
        obj['name'] = worker.name
        obj['id'] = worker.id
        obj['operative_system'] = worker.operative_system
        data['workers'].append(obj)

    return res.get_response(200, 'Worker list', data)

@csrf_exempt
def create_worker_info(request):
    """ Creates a worker given its info """

    if request.method != 'POST':
        return res.get_only_post_allowed({})

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

    worker = WorkerEntry.objects.filter(uuid=username_trimmed).first()
    if worker is not None:
        return res.get_response(405, 'Worker already created', {})

    user = User.objects.filter(username=username_trimmed).first()
    if not user:
        user = User.objects.create_user(
            username=username_trimmed,
            email=None,
            password=obj['uuid']
        )
        user.save()

    worker_count = WorkerEntry.objects.all().count()

    new_worker = WorkerEntry.objects.create(
        uuid=obj['uuid'],
        name=obj['host_name'],
        operative_system=obj['operative_system'],
        user=user,
        git_feeder=(worker_count == 0)
    )
    new_worker.save()

    BenchmarkDefinitionController.populate_worker_passes_all_definitions()

    ret = {}
    ret['worker'] = new_worker.as_object()
    ret['worker']['url'] = get_worker_urls(request.get_host(), ret['worker']['id'], ret['worker']['uuid'])
    ret['worker']['last_update'] = str(ret['worker']['last_update'])

    return res.get_response(200, 'Worker created succesfuly!', ret)


@transaction.atomic
def login_worker_info(request):
    """ Makes login with worker credentials """

    if request.method != 'POST':
        return res.get_only_post_allowed({})

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

        return res.get_response(200, 'The password is valid, but the account has been disabled!', {})

    # the authentication system was unable to verify the username and password
    return res.get_response(401, 'Access denied!', {})

@transaction.atomic
def update_worker_activity(request, worker_id):
    """ Updates worker activity from the last update time """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    worker = WorkerEntry.objects.filter(id=worker_id).first()
    if worker:
        worker.save()
        return res.get_response(200, 'Acitivity updated', {})

    return res.get_response(404, 'Worker not found!', {})


@transaction.atomic
def save_worker(request, worker_id):
    """ Saves workers info """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    (json_valid, post_info) = val.validate_json_string(request.body)
    if not json_valid:
        return res.get_json_parser_failed({})

    (obj_validated, obj) = val.validate_obj_schema(post_info, BluesteelWorkerSchemas.SAVE_WORKER_SCHEMA)
    if not obj_validated:
        return res.get_schema_failed(obj)

    worker = WorkerEntry.objects.filter(id=worker_id).first()
    if worker is None:
        return res.get_response(400, 'Worker not found', obj)
    else:
        worker.description = obj['description']
        worker.git_feeder = obj['git_feeder']
        worker.max_feed_reports = obj['max_feed_reports']
        worker.save()

    return res.get_response(200, 'Worker Saved!', {})


@transaction.atomic
def delete_worker(request, worker_id):
    """ Deletes worker and all its related info from BlueSteel """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    worker = WorkerEntry.objects.filter(id=worker_id).first()
    if worker is None:
        return res.get_response(400, 'Worker not found', {})
    else:
        worker.delete()

    obj = {}
    obj['redirect'] = ViewUrlGenerator.get_worker_all_url(1)
    return res.get_response(200, 'Worker Deleted!', obj)
