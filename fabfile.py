#
# Fabric script to manage verese
#

import os
from time import strftime

from fabric.api import env, run, sudo, local, \
     cd, hosts, runs_once, prompt, require

env.user = "ardupad"
env.hosts = ["ardupad.cc:2222"]
env.backup_dir = "/home/ardupad/backup/ardupad.cc"

@runs_once
def production():
    """ The production environment """
    env.remote_app_dir = "/home/ardupad/public_html/"
    env.branch = "master"
    env.database = None

def update_code():
    """
    Push code to github
    Pull code from server
    """
    require('remote_app_dir', provided_by=[production])

    local("git push origin master")

    with cd(env.remote_app_dir):
        run("git checkout %s" % env.branch)
        run("git pull origin %s" % env.branch)

def backup(files=True, database=True):
    """
    Backup
    """
    require('branch', provided_by=[production])
    date = strftime("%Y%m%d%H%M")

    if files:
        with cd(os.path.join(env.remote_app_dir, '..')):
            run("tar czf %s/%s/ardupad-%s-%s.tar "
                "ardupad" % (env.backup_dir, env.branch, env.branch, date)
                )

    if database and env.database:
        with cd(os.path.join(env.remote_app_dir, '..')):
            run("mysqldump %s | gzip > %s/%s/ardupad-database-%s-%s.gz" %\
                (env.database, env.backup_dir, env.branch, env.branch, date)
                )

def deploy(do_backup=False, do_update=True):
    require('branch', provided_by=[production])
    require('remote_app_dir', provided_by=[production])

    if do_backup == True:
        backup()

    if do_update == True:
        update_code()

def list_backups():
    require('branch', provided_by=[production])
    run("ls %s/%s" % (env.backup_dir, env.branch))

def restart():
    sudo("/etc/init.d/apache2 graceful", shell=False)
