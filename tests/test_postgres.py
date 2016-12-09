# coding: utf-8
import os
import imp

from fabric.state import env

env.forward_agent = True
env.use_ssh_config = True
# env.skip_bad_hosts = True


ROOT = os.path.dirname(os.path.dirname(__file__))
# sys.path.insert(0, ROOT)

fabmisc = imp.load_module(
    "fabmisc", *imp.find_module(
        "fabmisc", [ROOT]))
lazy = fabmisc.lazy


packages = fabmisc.Packages(
    lazy(env, 'apt', []),
    lazy(env, 'pip', []))
postgres = fabmisc.Postgres('9.5')
postgres_database = fabmisc.PostgresDatabase(
    'test_db_name', 'test_user', 'test_pass')


# $ fab -f test_postgres.py -H vmubuntu0 tasks.postgresdatabase.backup_to_local:/tmp/hoge.xz  # NOQA
# $ unxz -c /tmp/hoge.xz
# $ fab -f test_postgres.py -H vmubuntu0 tasks.postgresdatabase.restore_from_local:/tmp/hoge.xz  # NOQA
