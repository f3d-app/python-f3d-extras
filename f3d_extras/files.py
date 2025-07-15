import hashlib
import logging
import shutil
import tempfile
import urllib
import urllib.parse
from pathlib import Path
from urllib import request
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def download_file_if_url(url_or_path: Path | str):
    if isinstance(url_or_path, Path):
        return url_or_path
    else:
        try:
            return download_file(urlparse(url_or_path).geturl())
        except ValueError:
            return Path(url_or_path)


def download_file(url: str | urllib.parse.ParseResult):
    parsed_url = url if isinstance(url, urllib.parse.ParseResult) else urlparse(url)
    url_hash = hashlib.md5(parsed_url.geturl().encode()).hexdigest()
    dl_name = f"{url_hash}-{Path(parsed_url.path).name}"
    dl_path = Path(tempfile.gettempdir()) / dl_name

    if not dl_path.is_file():
        logger.info(f"downloading `{url}` to `{dl_path}` ...")
        req = request.Request(str(url), headers={"User-Agent": "Mozilla/5.0"})
        with request.urlopen(req) as response, open(dl_path, "wb") as f:
            shutil.copyfileobj(response, f)

    logger.info(f"using downloaded `{dl_path}` for `{url}`")

    return dl_path
