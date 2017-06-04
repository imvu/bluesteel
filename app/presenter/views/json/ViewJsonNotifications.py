""" Presenter json views, layout page functions """

from app.logic.mailing.controllers import MailingController
from app.logic.httpcommon import res

def send_notifications(request):
    """ Sends all the stacked emails to notify users """
    if request.method != 'POST':
        return res.get_only_post_allowed({})

    MailingController.MailingController.send_stacked_emails()

    return res.get_response(200, 'Stacked emails sent', {})
