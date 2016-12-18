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

nginx = fabmisc.Nginx()
postgres = fabmisc.Postgres('9.5')
postgres_database = fabmisc.PostgresDatabase(
    'gitbucket', 'gitbucket', 'gitbucket_pass')
plugins = {
    'gitbucket-h2-backup-plugin':
    'https://github.com/gitbucket-plugins/gitbucket-h2-backup-plugin/'
    'releases/download/1.3.0/gitbucket-h2-backup.jar',
    'gitbucket-gist-plugin':
    'https://github.com/gitbucket/gitbucket-gist-plugin/'
    'releases/download/4.3.0/gitbucket-gist-plugin_2.11-4.3.0.jar',
    'gitbucket-pages-plugin': 'https://github.com/yaroot/'
    'gitbucket-pages-plugin/releases/download/v0.8/pages-plugin_2.11-0.8.jar',
    'gitbucket-network-plugin': 'https://github.com/mrkm4ntr/'
    'gitbucket-network-plugin/releases/download/1.1/'
    'gitbucket-network-plugin_2.11-1.1.jar',
}

java = fabmisc.OracleJava()
tomcat = fabmisc.Tomcat('8', java.getJavaHome())
gitbucket = fabmisc.GitBucket(
    '4.7.1', tomcat, plugins=plugins, db=postgres_database)
gitbucket_site = fabmisc.NginxSite(nginx, 'tomcat',
                                   locations=(gitbucket, ))

# # install gitbucket, with_postgres
# $ fab -f test_gitbucket.py -H <hostname> tasks.run
# edit /usr/share/tomcat8/.gitbucket/gitbucket.conf
# base_url=http\://192.168.11.15/tomcat8/gitbucket
