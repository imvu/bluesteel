""" Command to send emails """

from django.core.management.base import BaseCommand
from app.logic.mailing.controllers import MailingController

class Command(BaseCommand):
    """ Command to send emails """

    args = ''
    help = 'Send all the emails ready'

    def handle(self, *args, **options):
        """ Sends out all the stacked emails ready to send """
        MailingController.MailingController.send_stacked_emails()
