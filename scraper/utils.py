import shutil
import os
import tempfile

import urllib.request as ulib
import urllib.parse as urlparse
import urllib.parse

from tqdm import tqdm
from pathlib import Path
from wget import filename_fix_existing


def parse_download_link(url):
    link = str(url)
    link = link[link.rfind('https'):]
    link = urllib.parse.unquote(link)
    print(link)
    return link


def combine_extracted_info(headers, values):
    assert len(headers) == len(values)
    model_semantic = ''
    for i in range(len(headers)):
        model_semantic += f'{headers[i]}: {values[i]}. '
    return model_semantic


def create_dir_hierarchy(main_dir, breadcrumb):
    main_dir = Path(main_dir)
    new_dir = Path('F:\\test\\')
    for dir_name in breadcrumb:
        new_dir = main_dir / Path(dir_name)
        Path.mkdir(new_dir, parents=True, exist_ok=True)
        main_dir = new_dir
    return new_dir


def get_destination_path(destination_dir, breadcrumbs, model_id):
    breadcrumbs.append(model_id)
    destination_dir = create_dir_hierarchy(destination_dir, breadcrumbs)
    # destination_path = destination_dir / Path(model_id)  # Path(f'{filename}.zip')
    destination_path = destination_dir
    return destination_path


def download_file(url, out):
    def download(url, out):
        """High level function, which downloads URL into file in current
        directory. Almost the same implementation as in wget, but not buggy :)
        (Standard lib crashes, exception in parsing amazon header, other format)
        :param out: output filename
        :return:    filename where URL is downloaded to
        """
        filename = out
        if os.path.exists(filename):
            filename = filename_fix_existing(filename)

        binurl = list(urlparse.urlsplit(url))
        binurl[2] = urlparse.quote(binurl[2])
        binurl = urlparse.urlunsplit(binurl)

        ulib.urlretrieve(binurl, filename)

        return filename

    return download(url, out)


def read_urls_from_file(file_path):
    print(f'Reading model_urls...')
    model_urls = []
    with open(file_path) as file:
        for url in tqdm(file.readlines()):
            model_urls.append(url)

    return model_urls
