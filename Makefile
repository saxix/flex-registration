help:
	echo ""

clean:
	# cleaning
	@rm -fr dist '~build' .pytest_cache .coverage src/smart_admin.egg-info build
	@find . -name __pycache__ -o -name .eggs | xargs rm -rf
	@find . -name "*.py?" -o -name ".DS_Store" -o -name "*.orig" -o -name "*.min.min.js" -o -name "*.min.min.css" -prune | xargs rm -rf

fullclean:
	@rm -rf .tox .cache
	$(MAKE) clean

lint:
	@flake8 src/ tests/
	@isort src/ tests/

.PHONY: build docs


.build:
	docker build \
		-t saxix/flex-registration \
		-f docker/Dockerfile .
	docker images | grep ${DOCKER_IMAGE_NAME}

heroku:
	@git push develop heroku:master
	@git checkout develop
	@echo "check demo at https://flex-register.herokuapp.com/"

heroku-reset: heroku
	heroku pg:reset --confirm django-smart-admin
	heroku run python manage.py migrate
	heroku run python manage.py collectstatic --noinput

