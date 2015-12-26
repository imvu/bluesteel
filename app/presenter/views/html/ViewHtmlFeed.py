""" Presenter views, Feed page functions """

from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.gitfeeder.models.FeedModel import FeedEntry
from app.logic.httpcommon import res

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
