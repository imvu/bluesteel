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


def notify_benchmark_command_failure(bench_exec_id, bench_exec_receiver_email, bench_exec_commit_hash, report, domain):
    """ Will send a notification about command failures """

    title = 'Benchmark execution with failed commands on commit: {0}'.format(bench_exec_commit_hash)
    content = ''
    content += 'There were commands that failed to execute.\n\n'
    content += 'Executed commands:\n'

    for com in report['command_set']:
        content += '---------------------------------------\n'
        content += 'Command:\n{0}\n\n'.format(com['command'])
        content += 'Command Result Status:\n{0}\n\n'.format(com['result']['status'])
        content += 'Command Result Out:\n{0}\n\n'.format(com['result']['out'])
        content += 'Command Result Err:\n{0}\n\n'.format(com['result']['error'])
        content += '---------------------------------------\n'

    content += 'Take a look at: {0}'.format(
        ViewUrlGenerator.get_benchmark_execution_complete_full_url(
            domain,
            bench_exec_id)
        )

    create_notification_email(bench_exec_receiver_email, title, content, ['admin'])

def notify_benchmark_fluctuation(benchmark_execution, domain, fluctuations):
    """ Will send notificaiton about benchmark fluctuation """

    title = 'Benchmark execution fluctuation around commit: {0}'.format(benchmark_execution.commit.commit_hash)
    content = ''
    content += 'When Benchmark Execution with id: {0} was submitted, ' \
        'the system noticed a fluctuation around it.\n'.format(
            benchmark_execution.id
        )
    content += '    - This is the information of the Benchmark Execution:\n'
    content += '        Commit Hash: {0}.\n'.format(benchmark_execution.commit.commit_hash)
    content += '        Commit Author: {0}.\n'.format(benchmark_execution.commit.author.name)
    content += '        Commit Author Email: {0}.\n'.format(benchmark_execution.commit.author.email)
    content += '        Commit Author Date: {0}.\n'.format(benchmark_execution.commit.author_date)
    content += '\n'
    content += '        Worker Name: {0}.\n'.format(benchmark_execution.worker.name)
    content += '        Worker Operative System: {0}.\n'.format(benchmark_execution.worker.operative_system)
    content += '\n'
    content += '        Benchmark Definition Name: {0}.\n'.format(benchmark_execution.definition.name)
    content += '\n'
    content += '    - Around this commit there were fluctuations with those information:\n'

    for fluc in fluctuations:
        fluc_change = float(fluc['max']) - float(fluc['min'])
        fluc_percent = (fluc_change / float(fluc['min'])) * 100.0

        content += '\n'
        content += '        Result ID with fluctuations: {0}\n'.format(fluc['id'])
        content += '            Minimum Value: {0}\n'.format(fluc['min'])
        content += '            Maximum Value: {0}\n'.format(fluc['max'])
        content += '            Percent Value: {0}%\n'.format(fluc_percent)
        content += '\n'

    content += '    - You can visualize the result with:\n'
    content += '        URL: {0}\n'.format(
        ViewUrlGenerator.get_benchmark_execution_window_full_url(
            domain,
            benchmark_execution.id)
        )

    create_notification_email(benchmark_execution.commit.author.email, title, content, [''])
