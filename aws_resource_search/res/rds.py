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
    engine: str = dataclasses.field()
    id: str = dataclasses.field()
    name: str = dataclasses.field()

    @property
    def klass(self) -> str:
        return self.raw_data.get("DBInstanceClass", "Unknown")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            status=resource["DBInstanceStatus"],
            engine=resource.get("Engine", "Unknown"),
            id=resource["DBInstanceIdentifier"],
            name=resource["DBInstanceIdentifier"],
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
        return self.raw_data["DBInstanceArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.rds.get_database_instance(id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        from_detail = res_lib.DetailItem.from_detail
        url = self.get_console_url(ars.aws_console)
        detail_items = [
            from_detail("arn", self.arn, url=url),
            from_detail("DBInstanceIdentifier", self.id, url=url),
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
                from_detail("DBInstanceStatus", DBInstanceStatus, url=url),
                from_detail("DBInstanceClass", DBInstanceClass, url=url),
                from_detail("Engine", Engine, url=url),
                from_detail("EngineVersion", EngineVersion, url=url),
                from_detail("Host", Host, url=url),
                from_detail("Port", Port, url=url),
                from_detail("MasterUsername", MasterUsername, url=url),
                from_detail("DBName", DBName, url=url),
                from_detail("MultiAZ", MultiAZ, url=url),
                from_detail("AvailabilityZone", AvailabilityZone, url=url),
                from_detail("AutoMinorVersionUpgrade", AutoMinorVersionUpgrade, url=url),
                from_detail("PubliclyAccessible", PubliclyAccessible, url=url),
                from_detail("StorageType", StorageType, url=url),
                from_detail("AllocatedStorage", AllocatedStorage, url=url),
                from_detail("StorageEncrypted", StorageEncrypted, url=url),
                from_detail("DeletionProtection", DeletionProtection, url=url),
                from_detail("DBClusterIdentifier", DBClusterIdentifier, url=ars.aws_console.rds.get_database_cluster(id_or_arn=DBClusterIdentifier)),
            ])

            tags: dict = {dct["Key"]: dct["Value"] for dct in db.get("TagList", [])}
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class RdsDbInstanceSearcher(res_lib.Searcher[RdsDbInstance]):
    pass


rds_db_instance_searcher = RdsDbInstanceSearcher(
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
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="engine", minsize=2, maxsize=4, stored=True),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)


@dataclasses.dataclass
class RdsDbCluster(res_lib.BaseDocument):
    status: str = dataclasses.field()
    engine: str = dataclasses.field()

    @property
    def klass(self) -> str:
        return self.raw_data.get("DBInstanceClass", "Unknown")

    @classmethod
    def from_resource(cls, resource, bsm, boto_kwargs):
        return cls(
            raw_data=resource,
            status=resource["Status"],
            engine=resource.get("Engine", "Unknown"),
            id=resource["DBClusterIdentifier"],
            name=resource["DBClusterIdentifier"],
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
        return self.raw_data["DBClusterArn"]

    def get_console_url(self, console: res_lib.acu.AWSConsole) -> str:
        return console.rds.get_database_cluster(id_or_arn=self.arn)

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[res_lib.DetailItem]:
        Item = res_lib.DetailItem.from_detail
        url = self.get_console_url(ars.aws_console)
        detail_items = [
            Item("arn", self.arn, url=url),
            Item("DBClusterIdentifier", self.id, url=url),
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
            detail_items.extend(res_lib.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class RdsDbClusterSearcher(res_lib.Searcher[RdsDbCluster]):
    pass


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
    fields=res_lib.define_fields(
        # fmt: off
        fields=[
            res_lib.sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True),
            res_lib.sayt.NgramWordsField(name="engine", minsize=2, maxsize=4, stored=True),
        ],
        # fmt: on
    ),
    cache_expire=24 * 60 * 60,
    more_cache_key=None,
)
