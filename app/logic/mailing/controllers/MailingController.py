""" Mailing Controller file """

from django.core.mail import send_mass_mail
from django.utils import timezone
from app.logic.mailing.models.StackedMailModel import StackedMailEntry

class MailingController(object):
    """ Mailing Controller offers functions to send emails """

    @staticmethod
    def send_stacked_emails():
        """ Send all the stacked emails """

        mail_to_send = StackedMailEntry.objects.filter(is_sent=False)

        mail_stack = []
        for mail in mail_to_send:
            mail_stack.append(mail.get_email_as_data())

        send_mass_mail(mail_stack, fail_silently=False)

        for mail in mail_to_send:
            mail.is_sent = True
            mail.sent_at = timezone.now()
            mail.save()
