
define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean:  ## remove development artifacts and working directory
	# cleaning
	@rm -fr dist '~build' .pytest_cache .coverage src/smart_admin.egg-info build
	@find . -name __pycache__ -o -name .eggs | xargs rm -rf
	@find . -name "*.py?" -o -name ".DS_Store" -o -name "*.orig" -o -name "*.min.min.js" -o -name "*.min.min.css" -prune | xargs rm -rf

fullclean:  ## remove all development artifacts including tox
	@rm -rf .tox .cache
	$(MAKE) clean

lint:  ## code lint
	pre-commit run --all-files

heroku:  ## deploy on Heroku
	git checkout heroku
	git merge develop
	@git push heroku heroku:master
	@echo "check demo at https://flex-register.herokuapp.com/"
	heroku run python manage.py upgrade --no-input
	git checkout develop

heroku-reset:  ## Reset Heroku environment
	heroku pg:reset --confirm flex-register
	$(MAKE) heroku

#
# ONLY INITIAL DEVELOPMENT STAGE
# REMOVE AFTER FIRST OFFICIAL DEPLOYMENT IN ANY ENV
#
.init-db:
	#psql -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres -c "DROP DATABASE IF EXISTS test_sos"
	#psql -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres -c "DROP DATABASE IF EXISTS sos"
	#psql -h ${BITCASTER_DATABASE_HOST} -p ${BITCASTER_DATABASE_PORT} -U postgres -c "CREATE DATABASE sos"

reset-migrations: ## reset django migrations
	find src -name '0*[1,2,3,4,5,6,7,8,9,0]*' | xargs rm -f
	# we need to run this two times to properly handle Stripe dependency
	./manage.py makemigrations core --empty
	sed -i '/from /a from django.contrib.postgres.operations import CITextExtension' src/smart_register/core/migrations/0001_initial.py
	sed -i '/operations = \[/a CITextExtension()' src/smart_register/core/migrations/0001_initial.py
	./manage.py makemigrations
	./manage.py makemigrations --check
	./manage.py upgrade --no-input

i18n:  ## i18n support
	cd src && django-admin makemessages --all --settings=sos.config.settings -d djangojs --pythonpath=. --ignore=~*
	cd src && django-admin makemessages --all --settings=sos.config.settings --pythonpath=. --ignore=~*
	cd src && django-admin compilemessages --settings=sos.config.settings --pythonpath=. --ignore=~*
	git commit -m "Update translations"
