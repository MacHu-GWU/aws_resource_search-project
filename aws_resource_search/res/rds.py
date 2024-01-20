# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import sayt.api as sayt
import aws_console_url.api as acu

from .. import res_lib as rl

if T.TYPE_CHECKING:
    from ..ars_def import ARS


@dataclasses.dataclass
class RdsDbInstance(rl.ResourceDocument):
    # fmt: off
    status: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True)})
    engine: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="engine", minsize=2, maxsize=4, stored=True)})
    # fmt: on

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
        return rl.format_key_value("identifier", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}, {}".format(
            rl.format_key_value("status", self.status),
            rl.format_key_value("class", self.klass),
            rl.format_key_value("engine", self.engine),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["DBInstanceArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.rds.get_database_instance(id_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.rds.databases

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        detail_items.append(
            from_detail("DBInstanceIdentifier", self.id, url=url),
        )

        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.rds_client.describe_db_instances(DBInstanceIdentifier=self.name)
            dbs = res.get("DBInstances", [])
            if len(dbs) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 DB instance not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
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

            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class RdsDbInstanceSearcher(rl.BaseSearcher[RdsDbInstance]):
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
    result_path=rl.ResultPath("DBInstances"),
    # extract document
    doc_class=RdsDbInstance,
    # search
    resource_type=rl.SearcherEnum.rds_db_instance.value,
    fields=RdsDbInstance.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.rds_db_instance.value),
    more_cache_key=None,
)


@dataclasses.dataclass
class RdsDbCluster(rl.ResourceDocument):
    # fmt: off
    status: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="status", minsize=2, maxsize=4, stored=True)})
    engine: str = dataclasses.field(metadata={"field": sayt.NgramWordsField(name="engine", minsize=2, maxsize=4, stored=True)})
    # fmt: on

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
        return rl.format_key_value("identifier", self.name)

    @property
    def subtitle(self) -> str:
        return "{}, {}, {}, {}".format(
            rl.format_key_value("status", self.status),
            rl.format_key_value("class", self.klass),
            rl.format_key_value("engine", self.engine),
            self.short_subtitle,
        )

    @property
    def autocomplete(self) -> str:
        return self.name

    @property
    def arn(self) -> str:
        return self.raw_data["DBClusterArn"]

    def get_console_url(self, console: acu.AWSConsole) -> str:
        return console.rds.get_database_cluster(id_or_arn=self.arn)

    @classmethod
    def get_list_resources_console_url(cls, console: acu.AWSConsole) -> str:
        return console.rds.databases

    # fmt: off
    def get_details(self, ars: "ARS") -> T.List[rl.DetailItem]:
        from_detail = rl.DetailItem.from_detail
        url = self.get_console_url(console=ars.aws_console)
        detail_items = rl.DetailItem.get_initial_detail_items(doc=self, ars=ars)

        detail_items.append(
            from_detail("DBClusterIdentifier", self.id, url=url),
        )
        with rl.DetailItem.error_handling(detail_items):
            res = ars.bsm.rds_client.describe_db_clusters(DBClusterIdentifier=self.name)
            dbs = res.get("DBClusters", [])
            if len(dbs) == 0:
                return [
                    rl.DetailItem.new(
                        title="🚨 DB cluster not found, maybe it's deleted?",
                        subtitle=f"{rl.ShortcutEnum.ENTER} to verify in AWS Console",
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
                from_detail("Status", Status, url=url),
                from_detail("engine", engine, url=url),
                from_detail("EngineVersion", EngineVersion, url=url),
                from_detail("Endpoint", Endpoint, url=url),
                from_detail("ReaderEndpoint", ReaderEndpoint, url=url),
                from_detail("CustomEndpoints", CustomEndpoints, url=url),
                from_detail("Port", Port, url=url),
                from_detail("MasterUsername", MasterUsername, url=url),
                from_detail("DatabaseName", DatabaseName, url=url),
                from_detail("MultiAZ", MultiAZ, url=url),
                from_detail("AvailabilityZones", AvailabilityZones, url=url),
                from_detail("IAMDatabaseAuthenticationEnabled", IAMDatabaseAuthenticationEnabled, url=url),
                from_detail("DeletionProtection", DeletionProtection, url=url),
                *[
                    from_detail(
                        f"🖥️ db instance",
                        member["DBInstanceIdentifier"],
                        url=ars.aws_console.rds.get_database_instance(id_or_arn=member["DBInstanceIdentifier"]),
                        uid="db instance {}".format(member["DBInstanceIdentifier"])
                    )
                    for member in DBClusterMembers
                ],
                from_detail("DBClusterInstanceClass", DBClusterInstanceClass, url=url),
            ])

            tags = rl.extract_tags(res)
            detail_items.extend(rl.DetailItem.from_tags(tags, url))
        return detail_items
    # fmt: on


class RdsDbClusterSearcher(rl.BaseSearcher[RdsDbCluster]):
    pass


rds_db_cluster_searcher = rl.BaseSearcher(
    # list resources
    service="rds",
    method="describe_db_clusters",
    is_paginator=True,
    default_boto_kwargs={
        "PaginationConfig": {
            "MaxItems": 9999,
        },
    },
    result_path=rl.ResultPath("DBClusters"),
    # extract document
    doc_class=RdsDbCluster,
    # search
    resource_type=rl.SearcherEnum.rds_db_cluster.value,
    fields=RdsDbCluster.get_dataset_fields(),
    cache_expire=rl.config.get_cache_expire(rl.SearcherEnum.rds_db_cluster.value),
    more_cache_key=None,
)
