""" Presenter views, benchmark notifications page functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.benchmark.models.BenchmarkFluctuationWaiverModel import BenchmarkFluctuationWaiverEntry
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.httpcommon import res
from django.shortcuts import redirect

DEFINITION_ITEMS_PER_PAGE = 12
PAGINATION_HALF_RANGE = 2

def get_notification_controls():
    """ Returns a list of control buttons for the benchmark notification page """
    controls = []
    return controls


def get_benchmark_notifications(request):
    """ With this function we will redirect to a propper page. """
    del request

    project = GitProjectEntry.objects.all().order_by('-id').first()

    proj_id = 0
    if project is not None:
        proj_id = project.id

    url = ViewUrlGenerator.get_notification_url(proj_id)

    return redirect(url)

def get_notifications_of_git_project(request, git_project_id):
    """ Returns html for the benchmark definition page """
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_notification_controls()

    git_projects = GitProjectEntry.objects.all().order_by('-id')

    projects = []
    for git_project in git_projects:
        project = {}
        project['name'] = git_project.name
        project['url'] = ViewUrlGenerator.get_notification_url(git_project.id)
        project['selected'] = git_project.id == git_project_id
        projects.append(project)


    waivers = BenchmarkFluctuationWaiverEntry.objects.filter(
        git_user__project__id=git_project_id).order_by('-git_user__name')

    entries = []
    for waiver in waivers:
        entry = {}
        entry['name'] = waiver.git_user.name
        entry['email'] = waiver.git_user.email
        entry['notification_allowed'] = waiver.notification_allowed
        entry['url'] = {}
        entry['url']['allow'] = ViewUrlGenerator.get_notification_allow_url(waiver.id)
        entry['url']['deny'] = ViewUrlGenerator.get_notification_deny_url(waiver.id)
        entries.append(entry)

    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_notification_controls()
    data['projects'] = projects
    data['entries'] = entries

    return res.get_template_data(request, 'presenter/benchmark_notification.html', data)
