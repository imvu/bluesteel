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
    content += 'Executed commands:\n\n'

    for index, com in enumerate(report['command_set']):
        indx = index + 1
        command = com['command'].strip()
        if com['result']['status'] is not 0:
            content += '{0}.- Command: {1}\n'.format(indx, command)
            content += '             ^ Failed!\n'
            content += '        Result Status: {0}\n'.format(com['result']['status'])
            content += '        Result Out:\n{0}\n'.format(com['result']['out'])
            content += '        Result Err:\n{0}\n'.format(com['result']['error'])
        else:
            content += '{0}.- Command: {1}\n'.format(indx, command)

    content += '\n\nTake a look at: {0}'.format(
        ViewUrlGenerator.get_benchmark_execution_complete_full_url(
            domain,
            bench_exec_id)
        )

    create_notification_email(bench_exec_receiver_email, title, content, ['admin'])

def notify_benchmark_fluctuation(bench_exec_id, commit_obj, worker_obj, bench_def_name, domain, fluctuations):
    """ Will send notificaiton about benchmark fluctuation """

    send_email = False

    title = u'Benchmark execution fluctuation around commit: {0}'.format(commit_obj['hash'])
    content = u''
    content += u'When Benchmark Execution with id: {0} was submitted, ' \
        u'the system noticed a fluctuation around it.\n'.format(
            bench_exec_id
        )
    content += u'    - This is the information of the Benchmark Execution:\n'
    content += u'        Commit Hash: {0}.\n'.format(commit_obj['hash'])
    content += u'        Commit Author: {0}.\n'.format(commit_obj['author']['name'])
    content += u'        Commit Author Email: {0}.\n'.format(commit_obj['author']['email'])
    content += u'        Commit Author Date: {0}.\n'.format(commit_obj['author_date'])
    content += u'\n'
    content += u'        Worker Name: {0}.\n'.format(worker_obj['name'])
    content += u'        Worker Operative System: {0}.\n'.format(worker_obj['operative_system'])
    content += u'\n'
    content += u'        Benchmark Definition Name: {0}.\n'.format(bench_def_name)
    content += u'\n'
    content += u'    - Around this commit there were fluctuations with those information:\n'

    for fluc_id in fluctuations.keys():
        fluc = fluctuations[fluc_id]

        if not fluc['current']['has_results']:
            continue

        fluc_on_parent = (fluc['parent']['has_results']) and (abs(fluc['parent']['fluctuation_ratio']) > 0.0001)
        fluc_on_son = (fluc['son']['has_results']) and (abs(fluc['son']['fluctuation_ratio']) > 0.0001)

        if not fluc_on_parent and not fluc_on_son:
            continue

        content += u'\n'
        content += u'        Result with id \'{0}\' had fluctuations:\n'.format(fluc_id)
        content += u'\n'

        if fluc_on_parent:
            send_email = True
            fluc_value = float(fluc['parent']['fluctuation_ratio']) * 100.0
            content += u'            Parent commit: {0}\n'.format(fluc['parent']['commit_hash'][:7])
            content += u'            Parent median result: {0}\n'.format(fluc['parent']['median'])
            content += u'            Parent fluctuation vs Current commit: {0}%\n'.format(fluc_value)
            content += u'\n'

        content += u'            Current commit: {0}\n'.format(fluc['current']['commit_hash'][:7])
        content += u'            Current median result: {0}\n'.format(fluc['current']['median'])
        content += u'\n'

        if fluc_on_son:
            send_email = True
            fluc_value = float(fluc['son']['fluctuation_ratio']) * 100.0
            content += u'            Son commit: {0}\n'.format(fluc['son']['commit_hash'][:7])
            content += u'            Son median result: {0}\n'.format(fluc['son']['median'])
            content += u'            Son fluctuation vs Current commit: {0}%\n'.format(fluc_value)
            content += u'\n'

    content += u'\n'
    content += u'    - You can visualize the result with:\n'
    content += u'        URL: {0}\n'.format(
        ViewUrlGenerator.get_benchmark_execution_window_full_url(
            domain,
            bench_exec_id)
        )

    if send_email:
        create_notification_email(commit_obj['author']['email'], title, content, [''])
