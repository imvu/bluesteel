""" Presenter views, Feed page functions """

from django.core.paginator import Paginator
from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.httpcommon import res, pag
from app.logic.httpcommon.Page import Page

FEED_REPORT_ITEMS_PER_PAGE = 12
PAGINATION_HALF_RANGE = 2

def get_feed_report(request, feed_report_id):
    """ Returns html for the worker reports page """
    if request.method == 'GET':
        feed = FeedEntry.objects.filter(id=feed_report_id).first()
        if not feed:
            return res.get_template_data(request, 'presenter/not_found.html', {})
        data = {}
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])
        data['report'] = feed.as_object()

        return res.get_template_data(request, 'presenter/worker_report.html', data)
    else:
        return res.get_only_get_allowed({})

def get_feed_reports_from_worker(request, worker_id, page_index):
    """ Returns a single item list of all the feeds produced by a worker """
    if request.method == 'GET':
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
        data['pagination'] = ViewPrepareObjects.prepare_pagination_feed_reports(worker_id, page_indices)
        data['items'] = items

        return res.get_template_data(request, 'presenter/single_item_list.html', data)
    else:
        return res.get_only_get_allowed({})
