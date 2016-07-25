""" Presenter views, Json BluesteelWorker functions """

from django.middleware import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from app.logic.bluesteelworker.models.WorkerModel import WorkerEntry
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.presenter.schemas import BluesteelWorkerSchemas
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.httpcommon import res
from app.logic.httpcommon import val

def get_entry_points_urls(domain):
    """ Returns bootstrap urls for workers """
    obj = {}
    obj['layouts_url'] = ViewUrlGenerator.get_layout_point_full_url(domain)
    obj['worker_info_url'] = ViewUrlGenerator.get_worker_info_point_full_url(domain)
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
    if request.method == 'GET':
        obj = get_entry_points_urls(request.get_host())
        return res.get_response(200, 'Entry points', obj)
    else:
        return res.get_only_get_allowed({})


def get_worker_info(request, worker_uuid):
    if request.method == 'GET':
        worker = WorkerEntry.objects.filter(uuid=worker_uuid).first()

        obj = {}
        obj['csrf_token'] = csrf.get_token(request)

        if worker is None:
            return res.get_response(400, 'Worker not found', obj)
        else:
            ret_worker = worker.as_object()
            ret_worker['last_update'] = str(ret_worker['last_update'])
            ret_worker['url'] = get_worker_urls(request.get_host(), ret_worker['id'], ret_worker['uuid'])
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

        worker = WorkerEntry.objects.filter(uuid=username_trimmed).first()
        if worker is None:
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

            bench_def_entries = BenchmarkDefinitionEntry.objects.all()
            commit_entries = GitCommitEntry.objects.all()

            BenchmarkExecutionController.create_bench_executions_from_worker(
                new_worker,
                commit_entries,
                bench_def_entries)

            ret = {}
            ret['worker'] = new_worker.as_object()
            ret['worker']['url'] = get_worker_urls(request.get_host(), ret['worker']['id'], ret['worker']['uuid'])
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

def save_worker(request, worker_id):
    if request.method == 'POST':
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
    else:
        return res.get_only_post_allowed({})
