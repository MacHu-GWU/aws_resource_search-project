from boto_session_manager import BotoSesManager
import aws_console_url.api as acu
from aws_resource_search.ars_base_v2 import ARSBase
from aws_resource_search.res.s3 import s3_bucket_searcher
from aws_resource_search.res.iam import iam_role_searcher
from rich import print as rprint

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
ars = ARSBase(bsm=bsm)

if __name__ == "__main__":
    # res = s3_bucket_searcher.search(
    #     bsm=bsm,
    #     query="pipe",
    # )
    # res = iam_role_searcher.search(
    #     bsm=bsm,
    #     query="dev",
    # )

    res = ars._get_searcher("s3-bucket").search(None)
    rprint(res)
