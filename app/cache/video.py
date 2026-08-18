import os
import json


CACHE_ROOT = "/data/cache/video"

CHUNK_SIZE = 4 * 1024 * 1024



class VideoCache:


    def __init__(self):

        os.makedirs(
            CACHE_ROOT,
            exist_ok=True
        )



    def get_dir(
        self,
        file_id
    ):

        path = os.path.join(
            CACHE_ROOT,
            str(file_id)
        )

        os.makedirs(
            path,
            exist_ok=True
        )

        return path



    def chunk_path(
        self,
        file_id,
        index
    ):

        return os.path.join(
            self.get_dir(file_id),
            f"{index:06d}.chunk"
        )



    def exists(
        self,
        file_id,
        index
    ):

        return os.path.exists(
            self.chunk_path(
                file_id,
                index
            )
        )



    def read(
        self,
        file_id,
        index
    ):

        path = self.chunk_path(
            file_id,
            index
        )

        if not os.path.exists(path):

            return None


        with open(
            path,
            "rb"
        ) as f:

            return f.read()



    def write(
        self,
        file_id,
        index,
        data
    ):

        path = self.chunk_path(
            file_id,
            index
        )

        with open(
            path,
            "wb"
        ) as f:

            f.write(data)



    def save_meta(
        self,
        file_id,
        meta
    ):

        path = os.path.join(
            self.get_dir(file_id),
            "meta.json"
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                meta,
                f,
                ensure_ascii=False,
                indent=2
            )



    def load_meta(
        self,
        file_id
    ):

        path = os.path.join(
            self.get_dir(file_id),
            "meta.json"
        )

        if not os.path.exists(path):

            return None


        with open(
            path,
            encoding="utf-8"
        ) as f:

            return json.load(f)
