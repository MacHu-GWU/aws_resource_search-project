# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .. import res_lib
from ..terminal import format_key_value, ShortcutEnum
from ..searchers_enum import SearcherEnum

if T.TYPE_CHECKING:
    from ..ars import ARS


@dataclasses.dataclass
class RdsDbInstance(res_lib.BaseDocument):
    status: str = dataclasses.field()
    klass: str = dataclasses.field()
    engine: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    db_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            status=resource["DBInstanceStatus"],
            klass=resource.get("DBInstanceClass", "Unknown"),
            engine=resource.get("Engine", "Unknown"),
            id=resource["DBInstanceIdentifier"],
            name=resource["DBInstanceIdentifier"],
            db_arn=resource["DBInstanceArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("identifier", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}, {}".format(
            format_key_value("status", self.status),
            format_key_value("class", self.klass),
            format_key_value("engine", self.engine),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.db_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.rds.get_database_instance(id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        url = self.get_console_url(ars.aws_console)
        detail_items = [
            Item("arn", self.arn, url=url),
            Item("DBInstanceIdentifier", self.id),
        ]

        with self.enrich_details(detail_items):
            res = ars.bsm.rds_client.describe_db_instances(DBInstanceIdentifier=self.name)
            dbs = res.get("DBInstances", [])
            if len(dbs) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 DB instance not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            db = dbs[0]
            DBInstanceStatus = db["DBInstanceStatus"]
            DBInstanceClass = db.get("DBInstanceClass", "Unknown")
            Engine = db.get("Engine", "Unknown")
            EngineVersion = db.get("EngineVersion", "Unknown")
            Host = db.get("Endpoint", {}).get("Address", "Unknown")
            Port = db.get("Endpoint", {}).get("Port", "Unknown")
            MasterUsername = db.get("Engine", "Unknown")
            DBName = db.get("Engine", "Unknown")
            MultiAZ = db.get("MultiAZ", "Unknown")
            AvailabilityZone = db.get("AvailabilityZone", "Unknown")
            AutoMinorVersionUpgrade = db.get("AutoMinorVersionUpgrade", "Unknown")
            PubliclyAccessible = db.get("PubliclyAccessible", "Unknown")
            StorageType = db.get("StorageType", "Unknown")
            AllocatedStorage = db.get("AllocatedStorage", "Unknown")
            StorageEncrypted = db.get("StorageEncrypted", "Unknown")
            DeletionProtection = db.get("DeletionProtection", "Unknown")
            DBClusterIdentifier = db.get("DBClusterIdentifier", "Unknown")

            detail_items.extend([
                Item("DBInstanceStatus", DBInstanceStatus, url=url),
                Item("DBInstanceClass", DBInstanceClass, url=url),
                Item("Engine", Engine, url=url),
                Item("EngineVersion", EngineVersion, url=url),
                Item("Host", Host, url=url),
                Item("Port", Port, url=url),
                Item("MasterUsername", MasterUsername, url=url),
                Item("DBName", DBName, url=url),
                Item("MultiAZ", MultiAZ, url=url),
                Item("AvailabilityZone", AvailabilityZone, url=url),
                Item("AutoMinorVersionUpgrade", AutoMinorVersionUpgrade, url=url),
                Item("PubliclyAccessible", PubliclyAccessible, url=url),
                Item("StorageType", StorageType, url=url),
                Item("AllocatedStorage", AllocatedStorage, url=url),
                Item("StorageEncrypted", StorageEncrypted, url=url),
                Item("DeletionProtection", DeletionProtection, url=url),
                Item("DBClusterIdentifier", DBClusterIdentifier, url=ars.aws_console.rds.get_database_cluster(id_or_arn=DBClusterIdentifier)),
            ])

            tags: dict = {dct["Key"]: dct["Value"] for dct in db.get("TagList", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items
    # fmt: on


rds_db_instance_searcher = res_lib.Searcher(
    # list resources
    service="rds",
    method="describe_db_instances",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
            "PageSize": 100,
        },
    },
    result_path=res_lib.ResultPath("DBInstances"),
    # extract document
    doc_class=RdsDbInstance,
    # search
    resource_type=SearcherEnum.rds_db_instance,
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="klass"),
        res_lib.sayt.NgramWordsField(name="engine", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="db_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class RdsDbCluster(res_lib.BaseDocument):
    status: str = dataclasses.field()
    klass: str = dataclasses.field()
    engine: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    db_arn: str = dataclasses.field()

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            status=resource["Status"],
            klass=resource.get("DBClusterInstanceClass", "Unknown"),
            engine=resource.get("Engine", "Unknown"),
            id=resource["DBClusterIdentifier"],
            name=resource["DBClusterIdentifier"],
            db_arn=resource["DBClusterArn"],
        )

    @property
    def title(self) -> str:
        return format_key_value("identifier", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}, {}".format(
            format_key_value("status", self.status),
            format_key_value("class", self.klass),
            format_key_value("engine", self.engine),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.db_arn

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.rds.get_database_cluster(id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        url = self.get_console_url(ars.aws_console)
        detail_items = [
            Item("arn", self.arn, url=url),
            Item("DBClusterIdentifier", self.id),
        ]
        with self.enrich_details(detail_items):
            res = ars.bsm.rds_client.describe_db_clusters(DBClusterIdentifier=self.name)
            dbs = res.get("DBClusters", [])
            if len(dbs) == 0:
                return [
                    res_lib.DetailItem.new(
                        title="🚨 DB cluster not found, maybe it's deleted?",
                        subtitle=f"{ShortcutEnum.ENTER} to verify in AWS Console",
                        url=url,
                    )
                ]
            db = dbs[0]

            Status = db["Status"]
            engine = db.get("Engine", "Unknown")
            EngineVersion = db.get("EngineVersion", "Unknown")
            Endpoint = db.get("Endpoint", "Unknown")
            ReaderEndpoint = db.get("ReaderEndpoint", "Unknown")
            CustomEndpoints = db.get("CustomEndpoints", "Unknown")
            Port = db.get("Port", "Unknown")
            MasterUsername = db.get("Engine", "Unknown")
            DatabaseName = db.get("DatabaseName", "Unknown")
            MultiAZ = db.get("MultiAZ", "Unknown")
            AvailabilityZones = db.get("AvailabilityZones", "Unknown")
            IAMDatabaseAuthenticationEnabled = db.get("IAMDatabaseAuthenticationEnabled", "Unknown")
            DeletionProtection = db.get("DeletionProtection", "Unknown")
            DBClusterMembers = db.get("DBClusterMembers", [])
            DBClusterInstanceClass = db.get("DBClusterInstanceClass", "Unknown")

            detail_items.extend([
                Item("Status", Status, url=url),
                Item("engine", engine, url=url),
                Item("EngineVersion", EngineVersion, url=url),
                Item("Endpoint", Endpoint, url=url),
                Item("ReaderEndpoint", ReaderEndpoint, url=url),
                Item("CustomEndpoints", CustomEndpoints, url=url),
                Item("Port", Port, url=url),
                Item("MasterUsername", MasterUsername, url=url),
                Item("DatabaseName", DatabaseName, url=url),
                Item("MultiAZ", MultiAZ, url=url),
                Item("AvailabilityZones", AvailabilityZones, url=url),
                Item("IAMDatabaseAuthenticationEnabled", IAMDatabaseAuthenticationEnabled, url=url),
                Item("DeletionProtection", DeletionProtection, url=url),
                *[
                    Item(
                        f"🖥️ db instance",
                        member["DBInstanceIdentifier"],
                        url=ars.aws_console.rds.get_database_instance(id_or_arn=member["DBInstanceIdentifier"]),
                        uid="db instance {}".format(member["DBInstanceIdentifier"])
                    )
                    for member in DBClusterMembers
                ],
                Item("DBClusterInstanceClass", DBClusterInstanceClass, url=url),
            ])

            tags: dict = {dct["Key"]: dct["Value"] for dct in db.get("TagList", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags))
        return detail_items
    # fmt: on


rds_db_cluster_searcher = res_lib.Searcher(
    # list resources
    service="rds",
    method="describe_db_clusters",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
        },
    },
    result_path=res_lib.ResultPath("DBClusters"),
    # extract document
    doc_class=RdsDbCluster,
    # search
    resource_type=SearcherEnum.rds_db_cluster,
    fields=[
        res_lib.sayt.StoredField(name="raw_data"),
        res_lib.sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="klass"),
        res_lib.sayt.NgramWordsField(name="engine", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.IdField(name="id", field_boost=5.0, stored=True),
        res_lib.sayt.NgramWordsField(name="name", minsize=2, maxsize=4, stored=True),
        res_lib.sayt.StoredField(name="db_arn"),
    ],
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)
