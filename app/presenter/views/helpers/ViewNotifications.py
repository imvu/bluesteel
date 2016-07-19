""" View Notification generator """

from django.conf import settings
from django.contrib.auth.models import User
from app.presenter.views.helpers import ViewUrlGenerator
from app.logic.mailing.models.StackedMailModel import StackedMailEntry

def create_notification_email(receiver_email, title, content, group_names):
    """ Send an email notification plus the same email to users of group_names """
    StackedMailEntry.objects.create(
        sender=settings.DEFAULT_FROM_EMAIL,
        receiver=receiver_email,
        title=title,
        content=content
    )

    for group in group_names:
        users = User.objects.filter(groups__name=group)
        for user in users:
            StackedMailEntry.objects.create(
                sender=settings.DEFAULT_FROM_EMAIL,
                receiver=user.email,
                title=title,
                content=content
            )


def notify_json_invalid(receiver_email, msg):
    """ Will send notificaiton about invalid jsons """
    title = 'Json invalid'
    content = 'Json invalid.\nOriginal Json: {0}'.format(msg)
    create_notification_email(receiver_email, title, content, ['admin'])


def notify_schema_failed(receiver_email, msg, schema_msg):
    """ Will send notificaiton about json schema failures """
    title = 'Schema failed notification'
    content = 'Schema failed.\nOriginal Json: {0}\n\n Json schema message: {1}'.format(
        msg,
        schema_msg
    )

    create_notification_email(receiver_email, title, content, ['admin'])


def notify_benchmark_command_failure(receiver_email, benchmark_execution_id, commit_hash, domain):
    """ Will send a notification about command failures """
    title = 'Benchmark execution with failed commands on commit: {0}'.format(commit_hash)
    content = 'There were commands that failed to execute.\nTake a look at: {0}'.format(
        ViewUrlGenerator.get_benchmark_execution_full_url(
            domain,
            benchmark_execution_id)
        )

    create_notification_email(receiver_email, title, content, ['admin'])

def notify_benchmark_fluctuation(receiver_email, benchmark_execution_id, commit_hash, domain):
    """ Will send notificaiton about benchmark fluctuation """
    title = 'Benchmark execution fluctuation on commit: {0}'.format(commit_hash)
    content = 'There were fluctuations on the benchmark execution.\nTake a look at: {0}'.format(
        ViewUrlGenerator.get_benchmark_execution_window_full_url(
            domain,
            benchmark_execution_id)
        )

    create_notification_email(receiver_email, title, content, [''])
