from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import logging


class Executor:
    def __init__(self, workers, desc=None):
        self.desc = desc
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.executor = ThreadPoolExecutor(max_workers=workers)

    def addJobs(self, jobs, future_to_job=None):
        if future_to_job is None:
            future_to_job = {}
        for job in jobs:
            future = self.executor.submit(job)
            future_to_job[future] = job
        return future_to_job

    def executeAndWait(self, future_to_job):
        jobs_with_error = 0
        for future in as_completed(future_to_job):
            try:
                future.result()
            except:  # pylint: disable=bare-except
                self.log.error('Exception in job', exc_info=1)
                jobs_with_error += 1

        self.log.info(
            'Total Jobs: %d, Jobs with error: %d',
            len(future_to_job),
            jobs_with_error,
        )

    def execute(self, jobs):
        future_to_jobs = self.addJobs(jobs)
        return self.executeAndWait(future_to_jobs)


def execute(jobs, workers=os.cpu_count(), desc=None):
    executor = Executor(workers, desc)
    executor.execute(jobs)


def execute_all(cls, ctxs, workers=os.cpu_count(), desc=None):
    jobs = [cls(ctx) for ctx in ctxs]
    execute(jobs, workers=workers, desc=desc)
