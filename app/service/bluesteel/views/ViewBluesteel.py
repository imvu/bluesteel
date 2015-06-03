""" Bluesteel views """

from app.service.bluesteel.models.BluesteelCommandModel import BluesteelCommandEntry
from app.service.bluesteel.models.BluesteelCommandSetModel import BluesteelCommandSetEntry
from app.service.bluesteel.models.BluesteelProjectModel import BluesteelProjectEntry
from app.service.bluesteel.models.BluesteelLayoutModel import BluesteelLayoutEntry
from app.service.gitrepo.models.GitProjectModel import GitProjectEntry
from app.util.httpcommon import res


def create_command(command_set, order, command):
    """ Creates a default command """
    BluesteelCommandEntry.objects.create(
        bluesteel_command_set=command_set,
        order=order,
        command=command
    )

def create_default_command_set_clone(project):
    """ Creates a default command set with CLONE type"""
    command_set_clone = BluesteelCommandSetEntry.objects.create(
        bluesteel_project=project,
        command_set_type=BluesteelCommandSetEntry.CLONE,
    )

    create_command(command_set_clone, 0, 'git clone http://www.test.com')

def create_default_command_set_fetch(project):
    """ Creates a default command set with FETCH type """
    command_set_fetch = BluesteelCommandSetEntry.objects.create(
        bluesteel_project=project,
        command_set_type=BluesteelCommandSetEntry.FETCH,
    )

    create_command(command_set_fetch, 0, 'git checkout master')
    create_command(command_set_fetch, 1, 'git reset --hard origin/master')
    create_command(command_set_fetch, 2, 'git clean -f -d -q')
    create_command(command_set_fetch, 3, 'git pull -r origin master')
    create_command(command_set_fetch, 4, 'git checkout master')
    create_command(command_set_fetch, 5, 'git submodule sync')
    create_command(command_set_fetch, 6, 'git submodule update --init --recursive')


def post_create_new_layout(request):
    """ Create a new layout and return the ID of it """
    if request.method == 'POST':
        new_layout = BluesteelLayoutEntry.objects.create(name='default-name')

        new_git_project = GitProjectEntry.objects.create(url='http://www.test.com')

        new_project = BluesteelProjectEntry.objects.create(
            layout=new_layout,
            archive='default-archive',
            name='project-name',
            git_project=new_git_project
        )

        create_default_command_set_clone(new_project)
        create_default_command_set_fetch(new_project)

        data = {}
        data['layout'] = {}
        data['layout']['id'] = new_layout.id
        data['layout']['name'] = new_layout.name

        return res.get_response(200, 'New layout created', data)
    else:
        return res.get_only_post_allowed({})
