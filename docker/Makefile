# envs to set before use this script
.ONESHELL:

DEVELOP?=0
DOCKER_PASS?=
DOCKER_USER?=
VERSION?=0.1.0
BASE?=$(shell echo "${VERSION}" | sed "s/\([0-9]*\)\.\([0-9]*\)\.\(.*\)/\1.\2/g" )
PUSH_BASE?=0
DEVELOP?=1
BUILD_DATE:="$(shell date +"%Y-%m-%d %H:%M")"
# below vars are used internally
BUILD_OPTIONS?=--squash
CMD?=run
WORKER?='??'
CONTAINER_NAME?=sos-${VERSION}
LAZO?=$(shell which lazo)

DOCKER_REGISTRY=ghcr.io
DOCKER_IMAGE_NAME=saxix/smart_register
DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:${VERSION}
DOCKER_TARGET=${DOCKER_REGISTRY}/${DOCKER_IMAGE}
DOCKERFILE?=Dockerfile

RUN_OPTIONS?=
PIPENV_ARGS?=

ISDIRTY=$(shell git status --porcelain)
IMAGE_EXISTS=$(shell docker ps -a | grep "${DOCKER_REGISTRY}/${DOCKER_IMAGE}")

.PHONY: help runlocal
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

build-base:
	cd .. && docker build \
			${BUILD_OPTIONS} \
			-t ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}/base:${BASE} \
			-f docker/${DOCKERFILE}.base .
	#cd .. && git tag base-${BASE}
	docker tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}/base:${BASE} ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}/base:latest
ifeq ($(PUSH_BASE), 1)
	docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}/base:${BASE}
	docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}/base:latest
endif
	docker images | grep "${DOCKER_IMAGE_NAME}/base" | grep ${BASE}

check:
	@[ -z "`git status --porcelain`" ] || ( git status ; echo "Uncommited changes"; exit 1 )
	export IMAGE_EXISTS=`curl --silent --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}" https://gitlab.com/api/v4/projects/22122245/registry/repositories/1473455/tags/${VERSION} | jq '.location'`
	@[ "${IMAGE_EXISTS}" != null ] || ( echo "Docker image '${DOCKER_TARGET}' already exists"; exit 1 )
	@[ -n "`git tag -l ${VERSION}`" ] || git tag -m "v${VERSION}"  ${VERSION}

.build:
	cd .. && docker build \
			--build-arg BASE_IMAGE="${BASE}" \
			--build-arg DEVELOP=${DEVELOP} \
			--build-arg VERSION=${VERSION} \
			--build-arg BUILD_DATE=${BUILD_DATE} \
			--build-arg GITHUB_API_TOKEN=${GITLAB_API_TOKEN} \
			-t ${DOCKER_REGISTRY}/${DOCKER_IMAGE} \
			-f docker/${DOCKERFILE} .
	git tag $VERSION
	git push --tags
	docker images | grep "${DOCKER_IMAGE_NAME}" | grep ${VERSION}

build: check .build

.push:
	git push

.run:
	mkdir -p ../${VOLUME}
	cd .. && docker run \
	 		--rm \
	 		--name=${CONTAINER_NAME} \
			-p 8000:8000 \
			-p 8001:8001 \
			-e ADMIN_EMAIL="${ADMIN_EMAIL}" \
			-e ADMIN_PASSWORD="${ADMIN_PASSWORD}" \
			-e ADMIN_USERNAME="${ADMIN_USERNAME}" \
			-e ADMINS="" \
			-e ALLOWED_HOSTS="*" \
			-e CHANNEL_URLS="${CHANNEL_URLS}" \
			-e CELERY_BROKER_URL="${CELERY_BROKER_URL}" \
			-e ASGI_SERVER="${ASGI_SERVER}" \
			-e DATABASE_URL="${DATABASE_URL}" \
			-e DEBUG="0" \
			-e DEV_FOOTER_INFO="${DEV_FOOTER_INFO}" \
			-e DJANGO_SETTINGS_MODULE="sos.config.settings" \
			-e GOOGLE_ANALYTICS_GTAG_PROPERTY_ID=${GOOGLE_ANALYTICS_GTAG_PROPERTY_ID} \
			-e REDIS_URL="${REDIS_URL}" \
			-e SECRET_KEY="${SECRET_KEY}" \
			-e FERNET_KEYS="${FERNET_KEYS}" \
			-e CACHE_DEFAULT="${CACHE_DEFAULT}" \
			-e CACHE_CHAT="${CACHE_CHAT}" \
			-e SENTRY_DSN="${SENTRY_DSN}" \
			-e SOCIAL_AUTH_GOOGLE_OAUTH_KEY="${SOCIAL_AUTH_GOOGLE_OAUTH_KEY}" \
			-e SOCIAL_AUTH_GOOGLE_OAUTH_SECRET="${SOCIAL_AUTH_GOOGLE_OAUTH_SECRET}" \
			-e SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS=${SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS} \
			-e STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY} \
			-e STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY} \
			-e STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET} \
			-e TWILIO_ACCOUNT_SID=${TWILIO_SID} \
			-e TWILIO_TOKEN=${TWILIO_TOKEN} \
			-e TWILIO_SERVICE= \
			-e STATIC_ROOT=/var/sos/static/ \
			-e STATICFILES_STORAGE="sos.web.storage.ForgivingManifestStaticFilesStorage"\
			-v '${PWD}/../.build/docker/var/:/var/sos/' \
			${RUN_OPTIONS} \
			${DOCKER_REGISTRY}/${DOCKER_IMAGE} \
			${CMD}

# 			-e STATICFILES_STORAGE="django.contrib.staticfiles.storage.ManifestStaticFilesStorage"\
#docker push registry.gitlab.com/bitcaster/bitcaster

release: .docker-login ## relase version $VERSION
	docker tag ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${VERSION} ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest
	docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${VERSION}

run:  ## run image locally
	$(MAKE) .run

test:  ## test docker image
	CMD='sh -c "whoami && django-admin collectstatic --no-input -v 3 && django-admin check --deploy"' \
	$(MAKE) .run

shell:  ## run docker and spawn a shell
	DOCKER_IMAGE=${DOCKER_IMAGE_NAME}:latest RUN_OPTIONS=-it CMD='/bin/sh' $(MAKE) .run

IMAGE=${DOCKER_REGISTRY}/bitcaster/sos/docker-builder:19.03.12
docker-builder:
	cd .. && docker build \
		--squash \${BUILD_OPTIONS} \
		-t ${IMAGE} \
		-f docker/${DOCKERFILE}.builder .
	@echo ${GITLAB_API_TOKEN} | docker login ${DOCKER_REGISTRY} -u ${DOCKER_USERNAME} --password-stdin
	docker push ${IMAGE}

docker-builder-test:
	docker run \
		-e RANCHER_AUTH=${RANCHER_AUTH} \
		-e RANCHER_CLUSTER=${RANCHER_CLUSTER} \
		-e RANCHER_PROJECT=${RANCHER_PROJECT} \
		-i \
		-t ${IMAGE} \
		/bin/sh


.deploy:
	${LAZO} rancher \
		--insecure \
		--use-names \
		--auth ${RANCHER_AUTH} \
		--base-url ${RANCHER_BASE_URL} \
		upgrade \
		--no-check \
		--workload ${WORKER} \
		--username saxix \
		--project ${RANCHER_PROJECT} \
		--password ${GITLAB_API_TOKEN} \
		-r http://registry.gitlab.com \
		-i registry.gitlab.com/${DOCKER_IMAGE_NAME}:${VERSION}
	@printf "\033[0;32mDeployed Version \033[1;37m${VERSION}\033[0;32m on ${WORKER}. Image \033[1;37m${DOCKER_IMAGE_NAME}:${VERSION}\n"

deploy:  ## deploy on xavier
	WORKER='bitcaster-ns:sos-qa' $(MAKE) .deploy

deploy-prod:  ## deploy on xavier
	WORKER='bitcaster-ns:sos' $(MAKE) .deploy
