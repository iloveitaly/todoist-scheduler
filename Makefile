.PHONY: build build-debug docker-push

IMAGE_TAG ?= latest
GITHUB_REPOSITORY ?= $(shell gh repo view --json nameWithOwner --jq '.nameWithOwner' | tr -d '[:space:]')
IMAGE_NAME ?= ghcr.io/$(GITHUB_REPOSITORY)

# TODO once nixpacks is updated to support asdf we can remove hardcoded environment variables below
# 		 https://github.com/railwayapp/nixpacks/pulls?q=is%3Apr+author%3Ailoveitaly

# label is important here in order for the package to show up on the github repo
BUILD_CMD = nixpacks build . --name $(IMAGE_NAME) \
		--env NIXPACKS_PYTHON_VERSION \
		--env NIXPACKS_POETRY_VERSION \
		--label org.opencontainers.image.source=https://github.com/$(GITHUB_REPOSITORY) \
		--platform linux/arm64/v8 \
		--tag $(IMAGE_TAG)

build:
	$(BUILD_CMD)

build-shell: build
	docker run -it $(IMAGE_NAME):$(IMAGE_TAG) bash -c 'source /opt/venv/bin/activate'

build-dump:
	$(BUILD_CMD) --out .

build-debug: build-dump
	BUILDX_EXPERIMENTAL=1 docker buildx debug --invoke bash build . -f ./.nixpacks/Dockerfile

docker-push: build
	docker push $(IMAGE_NAME):$(IMAGE_TAG)