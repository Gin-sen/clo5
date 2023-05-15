from typing import Any
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxLogger():
    url: str
    organization: str
    token: str
    bucket: str
    client: InfluxDBClient

    def __init__(self, url, organization, token, bucket) -> None:
        self.url = url
        self.organization = organization
        self.token = token
        self.bucket = bucket
        self.client = InfluxDBClient(url=url, token=token, org=organization)
        self.create_bucket_if_not_exists()

    def create_bucket_if_not_exists(self):
        bucket_api = self.client.buckets_api()
        if bucket_api.find_bucket_by_name(self.bucket) is None:
            bucket_api.create_bucket(self.bucket)


    def log(self, log: Any | None = None):
        #instantiate the WriteAPI
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        write_api.write(
            bucket = self.bucket,
            org = self.organization,
            record = log
        )
        pass
