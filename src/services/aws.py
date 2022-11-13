

from functools import partial
from pathlib import Path
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError
from src.lib import utils
from src.services.environment import Environment


class AWS:
    s3: Any = boto3.client("s3",
                           aws_access_key_id=Environment.AWS_CONFIG["AWS_ID"],
                           aws_secret_access_key=Environment.AWS_CONFIG["AWS_KEY"])

    @classmethod
    def s3_bucket(cls):
        return AWS.s3.Bucket("memehub")

    @classmethod
    def upload_to_aws(cls, file_path: str, Key: str, Bucket: str = Environment.AWS_CONFIG["BUCKET"]):
        try:
            cls.s3.head_object(Bucket=Bucket, Key=Key)
        except ClientError:
            cls.s3.upload_file(file_path, Bucket, Key)

    @classmethod
    def upload_file(cls, file: Path, bucket_folder: str, root_folder: str, stem: bool):
        if not file.is_file():
            return
        file_path = str(file).replace("\\", "/")
        keypath = str(bucket_folder+file.name if stem else file)
        Key = keypath.replace(root_folder, bucket_folder)
        cls.upload_to_aws(file_path=file_path, Key=Key)

    @classmethod
    def upload_folder(cls, folder: str, bucket_folder: str, multi: bool = True, limit: Optional[int] = None, stem: bool = False):
        glob = Path(folder).glob('**/*')
        files = (next(glob) for _ in range(limit)) if limit else glob
        _ = utils.process(partial(cls.upload_file, root_folder=folder, bucket_folder=bucket_folder, stem=stem), files, multi=multi)


# def meme_clf_to_aws() -> None:
#     success = upload_to_aws(LOAD_STATIC_PATH.format(LTS_MEME_CLF_VERSION) + "static.json")
#     print("static " + str(success))
#     success = upload_to_aws(LTS_MEME_CLF_REPO.format("jit") + "features.pt")
#     print("features " + str(success))
#     success = upload_to_aws(LTS_MEME_CLF_REPO.format("jit") + "dense.pt")
#     print("dense " + str(success))


# def stonks_to_aws() -> None:
#     names = [os.path.splitext(filename)[0]for filename in os.listdir(LOAD_STONK_REPO.format("jit"))]
#     stats: Dict[str, int] = dict(num_names=len(names), success=0, failed=0)
#     for name in names:
#         success = upload_to_aws(LOAD_STONK_REPO.format("jit") + f"{name}.pt")
#         stats["success" if success else "failed"] += 1
#         clear_output()
#         utils.display_df(pd.DataFrame.from_records([stats]))
