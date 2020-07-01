import sys
import logging
import os
import json
from configredis.setredis import SetRedis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def project_name(path=os.getcwd(), dirs=(".git",), default=None):
    """
    get current project name.
    :param path: scripts path
    :param dirs: save rule e.g: catch git
    :param default: if set default then save to the default absolute path
    :return: project root directory name
    """
    prev, path = None, os.path.abspath(path)
    while prev != path:
        if any(os.path.isdir(os.path.join(path, d)) for d in dirs):
            return path.split('/')[-1]
        prev, path = path, os.path.abspath(os.path.join(path, os.pardir))
    return default


project_name_ = project_name()


def lookup_proj_config(proj_name=None):
    """
    lookup project config on redis.
    :param proj_name: project name which lookup from redis.
    """
    proj_name = proj_name or project_name_
    return {k: json.loads(v) for k, v in SetRedis().getfiels(proj_name).items()}


mapping_ = {**{'default': {}, 'dev': {}, 'pro': {}}, **lookup_proj_config()}

"""
need import below func to your config file.
import your config from your config file for connection. e.g: config = configs()
"""


def defaultconfig(**mapping):
    """
    set default env args.
    need import this func to your config document.
    :param mapping: dict
    """
    mapping_['default'] = mapping


def devconfig(**mapping):
    """
    set development env args.
    need import this func to your config document.
    :param mapping: dict
    """
    mapping_['dev'] = mapping


def proconfig(**mapping):
    """
    Set production env args.
    need import this func to your config document.
    :param mapping: dict
    """
    mapping_['pro'] = mapping


def configs():
    """
    get config info according env args. [defult/dev/pro]
    need import this func to your END of config document.
    :return: env config info as dict.
    """
    env = sys.argv[-1].lower()
    if env not in mapping_:
        logger.warning(' Not catch env args or defultconfig not setup. e.g: python sample.py dev|pro')
        logger.warning(' Will start under dev env? exit: ctrl+c')
        logger.info(f' Current env is dev')
        return {**mapping_['dev'], **mapping_['default']}
    else:
        logger.info(f' Current env is {env}')
        return {**mapping_[env], **mapping_['default']}


class ConfigArgs:
    """
    get config args value from redis.
    """
    def __getitem__(self, key):
        """
        sample:
        con = SetRedis()
        print(con['dev'])
        :param key: name is 'dev'
        :return: SetRedis().getfiels(name) -> dict e.g: {'disk_name': 'TenTBc'}
        """
        ConfigUpdate.upsert_config_to_redis(notify=True)
        item = SetRedis().getfiels(project_name_)
        return json.loads(item.get(key)) if item.get(key) else ''


class ConfigUpdate:
    @classmethod
    def upsert_config_to_redis(cls, mapping=None, notify=True):
        """
        insert or update current config to redis.
        """
        SetRedis().upsert(project_name_, mapping=mapping or mapping_, notify=False)
        logger.info(f"Project: {project_name_}'s config has been written to redis.") if notify else None

    @classmethod
    def upsert_field_to_redis(cls, env='default', notify=True, **kwargs):
        mapping_[env] = {**mapping_[env], **kwargs}
        SetRedis().upsert(project_name_, mapping=mapping_, notify=False)
        logger.info(f"Project: {project_name_}'s {env} config fileds has been written to redis.") if notify else None
