""" Presenter views, commit functions """

from app.presenter.views.helpers import ViewUrlGenerator
from app.presenter.views.helpers import ViewPrepareObjects
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry
from app.logic.benchmark.controllers.BenchmarkExecutionController import BenchmarkExecutionController
from app.logic.httpcommon import res

def get_commit_ordered_by_worker(request, commit_id):
    """ Returns html for the commit executions ordered by worker """
    if request.method == 'GET':
        commit_entry = GitCommitEntry.objects.filter(id=commit_id).first()
        if not commit_entry:
            return res.get_template_data(request, 'presenter/not_found.html', {})

        ret = BenchmarkExecutionController.get_bench_execs_ordered_by_worker(commit_entry)

        if ret['commit']['parent']['id'] != None:
            com_id = ret['commit']['parent']['id']
            ret['commit']['parent']['url'] = ViewUrlGenerator.get_commit_ordered_by_worker_url(com_id)

        if ret['commit']['son']['id'] != None:
            com_id = ret['commit']['son']['id']
            ret['commit']['son']['url'] = ViewUrlGenerator.get_commit_ordered_by_worker_url(com_id)

        for worker in ret['workers']:
            executions = []
            for execution in worker['executions']:
                obj = {}
                obj['id'] = execution
                obj['url'] = ViewUrlGenerator.get_benchmark_execution_relevant_url(execution)
                executions.append(obj)
            worker['executions'] = executions

        data = {}
        data['commit_data'] = ret
        data['menu'] = ViewPrepareObjects.prepare_menu_for_html([])

        return res.get_template_data(request, 'presenter/commit_by_workers.html', data)
    else:
        return res.get_template_data(request, 'presenter/not_found.html', {})
