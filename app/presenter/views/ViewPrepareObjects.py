""" Prepare objects for template consumption """

from app.presenter.views import ViewUrlGenerator

def prepare_layout_for_html(layout):
    """ Adds information to layout objects for template interaction """
    layout['url'] = {}
    layout['url']['edit'] = ViewUrlGenerator.get_layout_edit_url(layout['id'])
    layout['url']['save'] = ViewUrlGenerator.get_save_layout_url(layout['id'])
    layout['url']['add_project'] = ViewUrlGenerator.get_add_default_project_url(layout['id'])
    return layout

def prepare_project_for_html(project):
    """ Adds information to project objects for template interaction """
    project['url'] = {}
    project['url']['save'] = ViewUrlGenerator.get_save_project_url(project['id'])
    project['url']['delete'] = ViewUrlGenerator.get_delete_project_url(project['id'])
    return project
