""" Presenter json views, Project page functions """

# Duplicate code
# pylint: disable=R0801

from django.db import transaction
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.schemas import BluesteelSchemas
from app.logic.benchmark.models.BenchmarkDefinitionModel import BenchmarkDefinitionEntry
from app.logic.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.logic.bluesteel.controllers.BluesteelProjectController import BluesteelProjectController
from app.logic.bluesteel.controllers.BluesteelLayoutController import BluesteelLayoutController
from app.logic.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.logic.gitrepo.models.GitBranchModel import GitBranchEntry
from app.logic.commandrepo.models.CommandSetModel import CommandSetEntry
from app.logic.commandrepo.controllers.CommandController import CommandController
from app.logic.httpcommon import res
from app.logic.httpcommon import val

def filter_folder_path(path):
    """ This function will filter out \\..\\ or \\ at the begining. Also if path becomes empty, . will be used """
    local_search_path = path
    local_search_path = local_search_path.replace('\\..\\', '\\')
    local_search_path = local_search_path.replace('/../', '/')
    if local_search_path.startswith('/') or local_search_path.startswith('\\'):
        local_search_path = local_search_path[1:]
    if not local_search_path:
        local_search_path = '.'
    return local_search_path


@transaction.atomic
def save_project(request, project_id):
    """ Save project properties """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
    if project_entry is None:
        return res.get_response(404, 'Bluesteel project not found', {})

    (json_valid, post_info) = val.validate_json_string(request.body)
    if not json_valid:
        return res.get_json_parser_failed({})

    (obj_validated, val_resp_obj) = val.validate_obj_schema(post_info, BluesteelSchemas.SAVE_PROJECT)

    if not obj_validated:
        return res.get_schema_failed(val_resp_obj)

    CommandSetEntry.objects.filter(group=project_entry.command_group).delete()

    local_search_path = filter_folder_path(val_resp_obj['git_project_folder_search_path'])

    project_entry.name = val_resp_obj['name']
    project_entry.git_project_folder_search_path = local_search_path
    project_entry.save()

    CommandController.add_full_command_set(project_entry.command_group, 'CLONE', 0, val_resp_obj['clone'])
    CommandController.add_full_command_set(project_entry.command_group, 'FETCH', 1, val_resp_obj['fetch'])

    return res.get_response(200, 'Project saved', {})

@transaction.atomic
def delete_project(request, project_id):
    """ Delete project on a layout """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    project_entry = BluesteelProjectEntry.objects.filter(id=project_id).first()
    if project_entry is None:
        return res.get_response(404, 'Bluesteel project not found', {})

    layout_id = project_entry.layout.id
    project_entry.layout.active = False
    project_entry.layout.save()

    BluesteelProjectController.delete_project(project_entry)
    BluesteelLayoutController.sort_layout_projects_by_order(project_entry.layout)

    obj = {}
    obj['redirect'] = ViewUrlGenerator.get_layout_edit_url(layout_id)
    return res.get_response(200, 'Project deleted', obj)

def get_project_list_from_layout(request, layout_id):
    """ Return project ids, names and get-branch-list url """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    layout = BluesteelLayoutEntry.objects.filter(id=layout_id).first()
    if layout is None:
        return res.get_response(400, 'Layout not found', {})

    project_entries = BluesteelProjectEntry.objects.filter(layout=layout).order_by('order')

    projects = []
    for project in project_entries:
        obj = {}
        obj['id'] = project.id
        obj['name'] = project.name
        obj['url'] = {}
        obj['url']['project_branch_list'] = ViewUrlGenerator.get_project_branch_list_url(project.git_project.id)
        obj['url']['project_definition_list'] = ViewUrlGenerator.get_project_definition_list_url(project.id)
        projects.append(obj)

    data = {}
    data['projects'] = projects

    return res.get_response(200, 'Projects info found', data)


def get_branch_names_from_project(request, project_id):
    """ Return branch ids, names """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    project = BluesteelProjectEntry.objects.filter(id=project_id).first()

    if project is None:
        return res.get_response(400, 'Project not found', {})

    branch_entries = GitBranchEntry.objects.filter(project__id=project.git_project.id).order_by('order')

    branches = []
    for branch in branch_entries:
        obj = {}
        obj['id'] = branch.id
        obj['name'] = branch.name
        branches.append(obj)

    data = {}
    data['branches'] = branches

    return res.get_response(200, 'Project branches info found', data)


def get_definitions_from_project(request, project_id):
    """ Return Benchmark Definition ids, names """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    def_entries = BenchmarkDefinitionEntry.objects.filter(project__id=project_id, active=True).order_by('name')

    definitions = []
    for definition in def_entries:
        obj = {}
        obj['id'] = definition.id
        obj['name'] = definition.name
        obj['url'] = {}
        obj['url']['worker_list'] = ViewUrlGenerator.get_benchmark_definition_workers_url(definition.id)
        definitions.append(obj)

    data = {}
    data['definitions'] = definitions

    return res.get_response(200, 'Project definitions info found', data)
