""" Presenter views, Feed page functions """

from django.core.paginator import Paginator
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.httpcommon import res, pag
from app.logic.httpcommon.Page import Page

FEED_REPORT_ITEMS_PER_PAGE = 12
PAGINATION_HALF_RANGE = 2
MAX_COMMAND_RESULT_LENGTH = 1000
KEEP_YOUNG_COUNT = 10

def get_feed_controls(worker_id, keep_young_count):
    """ Returns a list of control buttons for the feed report page """
    control1 = {}
    control1['name'] = '  Purge All Reports'
    control1['link'] = ViewUrlGenerator.get_feed_purge_all_reports_url(worker_id)
    control1['icon'] = 'fa fa-trash'
    control1['onclick'] = 'executeAndReload(\'{0}\', \'\');'.format(control1['link'])

    control2 = {}
    control2['name'] = '  Purge Old Reports'
    control2['link'] = ViewUrlGenerator.get_feed_purge_old_reports_url(worker_id, keep_young_count)
    control2['icon'] = 'fa fa-trash'
    control2['onclick'] = 'executeAndReload(\'{0}\', \'\');'.format(control2['link'])

    controls = []
    controls.append(control1)
    controls.append(control2)
    return controls

def trim_report(report):
    """ Trim report output and add the url to download if trimmed """
    for com_set in report['command_group']['command_sets']:
        for com in com_set['commands']:
            len_out = len(com['result']['out'])
            len_err = len(com['result']['error'])

            need_trim = (len_out > MAX_COMMAND_RESULT_LENGTH) or (len_err > MAX_COMMAND_RESULT_LENGTH)

            if need_trim:
                com['result']['out'] = com['result']['out'][0:MAX_COMMAND_RESULT_LENGTH] + ' ...'
                com['result']['error'] = com['result']['error'][0:MAX_COMMAND_RESULT_LENGTH] + ' ...'
                com['url'] = {}
                com['url']['download'] = ViewUrlGenerator.get_command_download_json_url(com['id'])
    return report

def get_feed_report(request, feed_report_id):
    """ Returns html for the worker reports page """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    feed = FeedEntry.objects.filter(id=feed_report_id).first()
    if not feed:
        return res.get_template_data(request, 'presenter/not_found.html', {})
    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['report'] = feed.as_object()

    data['report'] = trim_report(data['report'])

    return res.get_template_data(request, 'presenter/worker_report.html', data)

def get_feed_reports_from_worker(request, worker_id, page_index):
    """ Returns a single item list of all the feeds produced by a worker """
    if request.method != 'GET':
        return res.get_only_get_allowed({})

    feed_entries = FeedEntry.objects.filter(worker__id=worker_id).order_by('-created_at')

    page = Page(FEED_REPORT_ITEMS_PER_PAGE, page_index)
    pager = Paginator(feed_entries, page.items_per_page)
    current_page = pager.page(page.page_index)
    feed_entries = current_page.object_list
    page_indices = pag.get_pagination_indices(page, PAGINATION_HALF_RANGE, pager.num_pages)

    items = []
    for report in feed_entries:
        obj = {}
        obj['name'] = 'REPORT {0}'.format(report.id)
        obj['url'] = ViewUrlGenerator.get_feed_report_url(report.id)
        items.append(obj)

    data = {}
    data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
    data['controls'] = get_feed_controls(worker_id, KEEP_YOUNG_COUNT)
    data['pagination'] = ViewPrepareObjects.prepare_pagination_feed_reports(worker_id, page_indices)
    data['items'] = items

    return res.get_template_data(request, 'presenter/single_item_list.html', data)
