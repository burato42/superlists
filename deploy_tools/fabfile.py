import random
from fabric.connection import Connection
from patchwork.files import exists, append


def deploy(con):
    site_folder = f'/home/{con.user}/sites/{con.host}'
    con.run(f'mkdir -p {site_folder}')
    with con.cd(site_folder):
        _get_latest_source(con)
        _update_virtualenv(con)
        _create_or_update_dotenv(con)
        _update_static_files(con)
        _update_database(con)


def _get_latest_source(сon):
    if exists('.git'):
        сon.run('git fetch')
    else:
        сon.run(f'git clone {REPO_URL} .')
    current_commit = сon.local("git log -n 1 --format=%H", capture=True)
    сon.run(f'git reset --hard {current_commit}')


def _update_virtualenv(сon):
    if not exists('virtualenv/bin/pip'):
        сon.run(f'python3.6 -m venv virtualenv')
    сon.run('./virtualenv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv(сon):
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={сon.host}')
    current_contents = сon.run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        сon.append('.env', f'DJANGO_SECRET_KEY={new_secret}')


def _update_static_files(сon):
    сon.run('./virtualenv/bin/python manage.py collectstatic --noinput')


def _update_database(сon):
    сon.run('./virtualenv/bin/python manage.py migrate --noinput')


if __name__ == '__main__':
    host = 'superlists-staging.tmrm.me'
    c = Connection(host=host, user='burato42')

    REPO_URL = 'https://github.com/burato42/superlists.git'

    deploy(c)
