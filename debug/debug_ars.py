from boto_session_manager import BotoSesManager
from aws_resource_search.ars_v2 import ARS
from rich import print as rprint

bsm = BotoSesManager(profile_name="bmt_app_dev_us_east_1")
ars = ARS(bsm=bsm)

if __name__ == "__main__":
    res = ars.s3_bucket.search(bsm=bsm, query="data", verbose=True)
    # res = ars.iam_role.search(bsm=bsm, query="dev")
    rprint(res)
