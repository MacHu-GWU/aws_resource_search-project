# -*- coding: utf-8 -*-

"""
todo: docstring
"""

import typing as T
import dataclasses
from datetime import datetime

from ...model import BaseAwsResourceModel
from ...cache import cache
from ...constants import LIST_API_CACHE_EXPIRE, FILTER_API_CACHE_EXPIRE
from ...fuzzy import FuzzyMatcher
from ..searcher import Searcher


@dataclasses.dataclass
class GlueJob(BaseAwsResourceModel):
    name: T.Optional[str] = dataclasses.field(default=None)
    type: T.Optional[str] = dataclasses.field(default=None)
    created_by: T.Optional[str] = dataclasses.field(default=None)
    create_at: T.Optional[datetime] = dataclasses.field(default=None)
    last_modified_by: T.Optional[str] = dataclasses.field(default=None)
    last_modified_at: T.Optional[datetime] = dataclasses.field(default=None)
    role_arn: T.Optional[str] = dataclasses.field(default=None)
    resource_arn: T.Optional[str] = dataclasses.field(default=None)
    max_capacity: T.Optional[int] = dataclasses.field(default=None)
    max_retries: T.Optional[int] = dataclasses.field(default=None)
    timeout: T.Optional[int] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)


class GlueJobFuzzyMatcher(FuzzyMatcher[GlueJob]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class GlueDatabase(BaseAwsResourceModel):
    catalog_id: T.Optional[str] = dataclasses.field(default=None)
    database: T.Optional[str] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    create_time: T.Optional[datetime] = dataclasses.field(default=None)
    location_uri: T.Optional[str] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)

    @property
    def name(self) -> str:  # pragma: no cover
        return self.database


class GlueDatabaseFuzzyMatcher(FuzzyMatcher[GlueDatabase]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class GlueTable(BaseAwsResourceModel):
    catalog_id: T.Optional[str] = dataclasses.field(default=None)
    database: T.Optional[str] = dataclasses.field(default=None)
    table: T.Optional[str] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    create_time: T.Optional[datetime] = dataclasses.field(default=None)
    update_time: T.Optional[datetime] = dataclasses.field(default=None)
    arn: T.Optional[str] = dataclasses.field(default=None)

    @property
    def name(self) -> str:  # pragma: no cover
        return self.table


class GlueTableFuzzyMatcher(FuzzyMatcher[GlueTable]):
    def get_name(self, item) -> T.Optional[str]:
        return item.name


@dataclasses.dataclass
class GlueSearcher(Searcher):
    """
    todo: docstring
    """

    def parse_list_jobs(self, res) -> T.List[GlueJob]:
        """
        Parse response of: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/list_jobs.html
        """
        lst = list()
        for dct in res.get("Jobs", []):
            glue_job = GlueJob(
                name=dct.get("Name"),
                type=dct.get("Type"),
                created_by=dct.get("CreatedBy"),
                create_at=dct.get("CreateDate"),
                last_modified_by=dct.get("LastModifiedBy"),
                last_modified_at=dct.get("LastModifiedDate"),
                role_arn=dct.get("RoleArn"),
                resource_arn=dct.get("ResourceArn"),
                max_capacity=dct.get("MaxCapacity"),
                max_retries=dct.get("MaxRetries"),
                timeout=dct.get("timeout"),
            )
            self._enrich_aws_account_and_region(glue_job)
            glue_job.arn = self.aws_console.glue.get_job_arn(glue_job.name)
            glue_job.console_url = self.aws_console.glue.get_job(glue_job.name)
            lst.append(glue_job)
        return lst

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_jobs(
        self,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[GlueJob]:
        paginator = self.bsm.glue_client.get_paginator("get_jobs")
        glue_jobs = list()
        for res in paginator.paginate(
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        ):
            glue_jobs.extend(self.parse_list_jobs(res))
        return glue_jobs

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_jobs(self, query_str: str) -> T.List[GlueJob]:
        return GlueJobFuzzyMatcher.from_items(self.list_jobs()).match(query_str)

    def parse_get_databases(self, res) -> T.List[GlueDatabase]:
        """
        Parse response of: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/get_databases.html
        """
        lst = list()
        for dct in res.get("DatabaseList", []):
            glue_database = GlueDatabase(
                catalog_id=dct.get("CatalogId"),
                database=dct.get("Name"),
                description=dct.get("Description"),
                create_time=dct.get("CreateTime"),
                location_uri=dct.get("LocationUri"),
            )
            self._enrich_aws_account_and_region(glue_database)
            glue_database.arn = self.aws_console.glue.get_database_arn(
                name=glue_database.name
            )
            glue_database.console_url = self.aws_console.glue.get_database(
                database=glue_database.name,
                catalog_id=glue_database.catalog_id,
            )
            lst.append(glue_database)
        return lst

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_databases(
        self,
        catalog_id: T.Optional[str] = None,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[GlueDatabase]:
        paginator = self.bsm.glue_client.get_paginator("get_databases")
        glue_databases = list()
        kwargs = dict(
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        )
        if catalog_id:
            kwargs["CatalogId"] = catalog_id
        for res in paginator.paginate(**kwargs):
            glue_databases.extend(self.parse_get_databases(res))
        return glue_databases

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_databases(
        self,
        query_str: str,
        catalog_id: T.Optional[str] = None,
    ) -> T.List[GlueDatabase]:
        return GlueDatabaseFuzzyMatcher.from_items(
            self.list_databases(catalog_id=catalog_id)
        ).match(query_str)

    def parse_get_tables(self, res) -> T.List[GlueTable]:
        """
        Parse response of: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/get_databases.html
        """
        lst = list()
        for dct in res.get("TableList", []):
            glue_table = GlueTable(
                catalog_id=dct.get("CatalogId"),
                database=dct.get("DatabaseName"),
                table=dct.get("Name"),
                description=dct.get("Description"),
                create_time=dct.get("CreateTime"),
                update_time=dct.get("UpdateTime"),
            )
            self._enrich_aws_account_and_region(glue_table)
            glue_table.arn = self.aws_console.glue.get_table_arn(
                database=glue_table.database, table=glue_table.table
            )
            glue_table.console_url = self.aws_console.glue.get_table(
                database=glue_table.database,
                table=glue_table.table,
                catalog_id=glue_table.catalog_id,
            )
            lst.append(glue_table)
        return lst

    @cache.better_memoize(expire=LIST_API_CACHE_EXPIRE)
    def list_tables(
        self,
        database: str,
        catalog_id: T.Optional[str] = None,
        expression: T.Optional[str] = None,
        max_items: int = 1000,
        page_size: int = 100,
    ) -> T.List[GlueTable]:
        paginator = self.bsm.glue_client.get_paginator("get_tables")
        glue_tables = list()
        kwargs = dict(
            DatabaseName=database,
            PaginationConfig=dict(
                MaxItems=max_items,
                PageSize=page_size,
            ),
        )
        if catalog_id:
            kwargs["CatalogId"] = catalog_id
        if expression:
            kwargs["Expression"] = expression
        for res in paginator.paginate(**kwargs):
            glue_tables.extend(self.parse_get_tables(res))
        return glue_tables

    @cache.better_memoize(expire=FILTER_API_CACHE_EXPIRE)
    def filter_tables(
        self,
        query_str: str,
        database: str,
        catalog_id: T.Optional[str] = None,
        expression: T.Optional[str] = None,
    ) -> T.List[GlueTable]:
        return GlueTableFuzzyMatcher.from_items(
            self.list_tables(
                database=database,
                catalog_id=catalog_id,
                expression=expression,
            )
        ).match(query_str)
