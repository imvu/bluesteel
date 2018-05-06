""" Presenter json views, layout page functions """

from app.logic.mailing.controllers import MailingController
from app.logic.benchmark.models.BenchmarkFluctuationWaiverModel import BenchmarkFluctuationWaiverEntry
from app.logic.httpcommon import res

def send_notifications(request):
    """ Sends all the stacked emails to notify users """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    MailingController.MailingController.send_stacked_emails()

    return res.get_response(200, 'Stacked emails sent', {})


def modify_fluctuation_waiver(request, waiver_id, value):
    """ Modify the fluctuation waiver to allow or deny notifications. """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    waiver = BenchmarkFluctuationWaiverEntry.objects.filter(id=waiver_id).first()

    if waiver is None:
        return res.get_response(404, 'Waiver does not exists!', {})

    waiver.notification_allowed = value
    waiver.save()
    return res.get_response(200, 'Waiver modified succesfully!', {})
