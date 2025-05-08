import logging
import time


class AwsTextract:
    def __init__(self, client):
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.client = client

    def wait_for_job_to_complete(self, job_id):
        response = None
        while True:
            response = self.client.get_document_text_detection(JobId=job_id)

            if response['JobStatus'] in ['SUCCEEDED', 'FAILED']:
                break
            self.log.info('Waiting for job to complete job_id=%s', job_id)
            time.sleep(5)
        return response

    def collect_response(self, job_id, response):
        responses = [response]
        next_token = response.get('NextToken', None)

        while next_token is not None:
            response = self.client.get_document_text_detection(
                JobId=job_id, NextToken=next_token
            )
            responses.append(response)
            next_token = response.get('NextToken', None)

        return responses

    def transcribe_document(self, bucket, prefix):
        self.log.info('Transcribing document bucket=%s prefix=%s', bucket, prefix)
        response = self.client.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': prefix}}
        )

        job_id = response['JobId']

        response = self.wait_for_job_to_complete(job_id)

        if response['JobStatus'] != 'SUCCEEDED':
            raise SystemError(
                f'Error transcribing the document bucket={bucket} prefix={prefix} job_id={job_id}'
            )
        return self.collect_response(job_id, response)