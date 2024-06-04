import json

from sqlitedict import SqliteDict

db = SqliteDict("/Users/tbatters/BIG-STUFF/0example.sqlite", autocommit=True)


db[
    "4ccb527c2bae2957cf90983cffbfee2545466e89c079cbc9d52f9ed38d7923e5"
] = '{"type": "d", "mode": "drwxr-xr-x", "user": "tbatters", "group": 1946612988, "uid": 1274123082, "gid": 1946612988, "path": "Users/tbatters/Documents-Mirrored", "healthy": true, "source": "", "linktarget": "", "flags": 0, "mtime": "2020-05-23T12:34:40.493423", "size": 0}'


db["A"] = json.loads(
    '{"type": "d", "mode": "drwxr-xr-x", "user": "tbatters", "group": 1946612988, "uid": 1274123082, "gid": 1946612988, "path": "Users/tbatters/Documents-Mirrored", "healthy": true, "source": "", "linktarget": "", "flags": 0, "mtime": "2020-05-23T12:34:40.493423", "size": 0}'
)


result = db["4ccb527c2bae2957cf90983cffbfee2545466e89c079cbc9d52f9ed38d7923e5"]
print("result = ", result)

result = db["A"]
print("result A = ", result)


db.commit()
