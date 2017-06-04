""" Benchmark Fluctuation Controller file """

import sys
from app.logic.benchmark.models.BenchmarkExecutionModel import BenchmarkExecutionEntry
from app.logic.benchmark.models.BenchmarkFluctuationOverrideModel import BenchmarkFluctuationOverrideEntry
from app.logic.gitrepo.controllers.GitController import GitController
from app.logic.gitrepo.models.GitProjectModel import GitProjectEntry
from app.logic.gitrepo.models.GitCommitModel import GitCommitEntry

class BenchmarkFluctuationController(object):
    """ Benchmark Fluctuation controller with helper functions """

    @staticmethod
    def init_unified_result_structure():
        """ Initializes a default structure with propper fields for parent, current and son results """
        obj = {}
        obj['parent'] = {}
        obj['parent']['has_results'] = False
        obj['parent']['median'] = 0
        obj['parent']['fluctuation_ratio'] = 0.0
        obj['parent']['commit_hash'] = ''
        obj['current'] = {}
        obj['current']['has_results'] = False
        obj['current']['median'] = 0
        obj['current']['commit_hash'] = ''
        obj['son'] = {}
        obj['son']['has_results'] = False
        obj['son']['median'] = 0
        obj['son']['fluctuation_ratio'] = 0.0
        obj['son']['commit_hash'] = ''
        return obj

    @staticmethod
    def store_result_on_channel(unified_fluctuation, channel_name, result, commit_hash):
        """ We will store the result on parent, current or son channels only if vertical_bars appar """
        if result['visual_type'] == 'vertical_bars':
            unified_fluctuation[result['id']][channel_name]['has_results'] = True
            unified_fluctuation[result['id']][channel_name]['median'] = result['median']
            unified_fluctuation[result['id']][channel_name]['commit_hash'] = commit_hash
        return unified_fluctuation

    @staticmethod
    def store_results_on_unified_fluctuation(unified_fluctuation, channel_name, results):
        """ Store all the results of a given channel: parent, current, son """
        if results is None:
            return

        for result in results['results']:
            res_id = result['id']
            if res_id not in unified_fluctuation:
                unified_fluctuation[res_id] = BenchmarkFluctuationController.init_unified_result_structure()

            BenchmarkFluctuationController.store_result_on_channel(
                unified_fluctuation,
                channel_name,
                result,
                results['commit_hash'])

    @staticmethod
    def from_results_to_unified_fluctuation(results_parent, results_current, results_son):
        """ Unifies parent, current and son results by id """

        unified = {}

        BenchmarkFluctuationController.store_results_on_unified_fluctuation(unified, 'parent', results_parent)
        BenchmarkFluctuationController.store_results_on_unified_fluctuation(unified, 'current', results_current)
        BenchmarkFluctuationController.store_results_on_unified_fluctuation(unified, 'son', results_son)

        return unified

    @staticmethod
    def get_ratio(initial_value, later_value):
        """ Computes the ratio of later value vs the initial one """
        if float(initial_value) < 0.000001:
            return 1.0

        ratio_change = float(later_value) - float(initial_value)
        ratio = ratio_change / float(initial_value)
        return ratio

    @staticmethod
    def compute_fluctuation_ratio(unified_fluctuation):
        """ Computes fluctuation ratios on every id, on the parent, and the son """
        for fluc_id in unified_fluctuation.keys():
            fluc = unified_fluctuation[fluc_id]
            if not fluc['current']['has_results']:
                continue

            med_current = fluc['current']['median']

            if fluc['parent']['has_results']:
                med_parent = fluc['parent']['median']
                parent_fluc = BenchmarkFluctuationController.get_ratio(med_current, med_parent)
                fluc['parent']['fluctuation_ratio'] = parent_fluc

            if fluc['son']['has_results']:
                med_son = fluc['son']['median']
                son_fluc = BenchmarkFluctuationController.get_ratio(med_current, med_son)
                fluc['son']['fluctuation_ratio'] = son_fluc
        return unified_fluctuation

    @staticmethod
    def get_benchmark_fluctuation(project, benchmark_def_id, worker_id, commit_hash, fluctuation_window):
        """ Returns fluctuation information from a commit range """
        hashes = GitController.get_commit_hashes_parents_and_children(project, commit_hash, fluctuation_window)
        benchmarks = {}
        fluctuations = []

        for comm_hash in hashes:
            bench = BenchmarkExecutionEntry.objects.filter(
                definition__id=benchmark_def_id,
                worker__id=worker_id,
                commit__commit_hash=comm_hash).first()
            if not bench:
                continue

            results = bench.get_benchmark_results()

            for result in results:
                if result['id'] not in benchmarks:
                    benchmarks[result['id']] = []
                benchmarks[result['id']].append(result)

        for key in benchmarks:
            median_min = sys.float_info.max
            median_max = sys.float_info.min

            need_append = False

            for bench in benchmarks[key]:
                if bench['visual_type'] == 'vertical_bars':
                    need_append = True
                    median_min = min(median_min, bench['median'])
                    median_max = max(median_max, bench['median'])

            if need_append:
                fluctuation = {}
                fluctuation['id'] = key
                fluctuation['min'] = median_min
                fluctuation['max'] = median_max
                fluctuations.append(fluctuation)

        return fluctuations

    @staticmethod
    def get_benchmark_fluctuation_adjacent(project, benchmark_def_id, worker_id, commit_hash):
        """ Returns fluctuation information from a commit, its parent, and its child """
        commit_entry = GitCommitEntry.objects.filter(project=project, commit_hash=commit_hash).first()
        commit_son = GitCommitEntry.objects.filter(project=project, git_son_commit__parent=commit_entry).first()
        commit_parent = GitCommitEntry.objects.filter(project=project, git_parent_commit__son=commit_entry).first()

        results_current = None
        results_parent = None
        results_son = None

        if commit_entry:
            bench = BenchmarkExecutionEntry.objects.filter(
                definition__id=benchmark_def_id,
                worker__id=worker_id,
                commit__project=project,
                commit__id=commit_entry.id).first()

            if bench:
                results_current = {}
                results_current['commit_hash'] = commit_entry.commit_hash
                results_current['results'] = bench.get_benchmark_results()

        if commit_son:
            bench = BenchmarkExecutionEntry.objects.filter(
                definition__id=benchmark_def_id,
                worker__id=worker_id,
                commit__project=project,
                commit__id=commit_son.id).first()

            if bench:
                results_son = {}
                results_son['commit_hash'] = commit_son.commit_hash
                results_son['results'] = bench.get_benchmark_results()

        if commit_parent:
            bench = BenchmarkExecutionEntry.objects.filter(
                definition__id=benchmark_def_id,
                worker__id=worker_id,
                commit__project=project,
                commit__id=commit_parent.id).first()

            if bench:
                results_parent = {}
                results_parent['commit_hash'] = commit_parent.commit_hash
                results_parent['results'] = bench.get_benchmark_results()

        uni_fluc = BenchmarkFluctuationController.from_results_to_unified_fluctuation(
            results_parent,
            results_current,
            results_son)

        uni_fluc = BenchmarkFluctuationController.compute_fluctuation_ratio(uni_fluc)
        return uni_fluc

    @staticmethod
    def does_benchmark_fluctuation_exist(benchmark_exec_entry):
        """ Returns true if fluctuation exists and fluctuations info """
        bench_exec = BenchmarkExecutionEntry.objects.filter(id=benchmark_exec_entry.id).first()
        if bench_exec is None:
            return (False, [])

        commit_hash = bench_exec.commit.commit_hash
        project = GitProjectEntry.objects.filter(id=bench_exec.definition.project.id).first()

        uni_fluctuations = BenchmarkFluctuationController.get_benchmark_fluctuation_adjacent(
            project=project,
            benchmark_def_id=bench_exec.definition.id,
            worker_id=bench_exec.worker.id,
            commit_hash=commit_hash
        )

        max_fluctuation_ratio = float(bench_exec.definition.max_fluctuation_percent) / 100.0
        fluctuation_overrides = BenchmarkFluctuationController.get_fluctuation_overrides(bench_exec.definition.id)

        return BenchmarkFluctuationController.get_fluctuations_with_overrides_applied(
            uni_fluctuations,
            max_fluctuation_ratio,
            fluctuation_overrides)


    @staticmethod
    def get_fluctuation_overrides(benchmark_definition_id):
        """ Return a dictionary with all the fluctuation overrides (id + value) """
        fluctuations_overrides = BenchmarkFluctuationOverrideEntry.objects.filter(
            definition__id=benchmark_definition_id)

        fluc_dict = {}

        for overrides in fluctuations_overrides:
            fluc_dict[overrides.result_id] = float(overrides.override_value) / 100.0

        return fluc_dict


    @staticmethod
    def get_fluctuations_with_overrides_applied(fluctuations, default_fluctuation_ratio, fluctuation_overrides):
        """ Returns a list of fluctuations with the fluctuation overrides already applied """
        ret_fluctuations = {}
        for fluc_id in fluctuations.keys():
            fluc = fluctuations[fluc_id]

            ratio_to_apply = default_fluctuation_ratio
            if fluc_id in fluctuation_overrides:
                ratio_to_apply = fluctuation_overrides[fluc_id]

            if fluc['parent']['has_results'] and abs(fluc['parent']['fluctuation_ratio']) >= ratio_to_apply:
                ret_fluctuations[fluc_id] = fluc
                continue

            if fluc['son']['has_results'] and abs(fluc['son']['fluctuation_ratio']) >= ratio_to_apply:
                ret_fluctuations[fluc_id] = fluc
                continue

        return (len(ret_fluctuations.keys()) > 0, ret_fluctuations)
