.PHONY: build build-debug

IMAGE_TAG ?= latest
GITHUB_REPOSITORY ?= $(shell gh repo view --json nameWithOwner --jq '.nameWithOwner' | tr -d '[:space:]')
GITHUB_DESCRIPTION ?= $(shell gh api repos/$(GITHUB_REPOSITORY) --jq .description | sed 's/^[ \t]*//;s/[ \t]*$$//')
IMAGE_NAME ?= ghcr.io/$(GITHUB_REPOSITORY)

# label is important here in order for the package to show up on the github repo
BUILD_CMD = nixpacks build . --name $(IMAGE_NAME) \
		--label org.opencontainers.image.source=https://github.com/$(GITHUB_REPOSITORY) \
		--label "org.opencontainers.image.description=$(GITHUB_DESCRIPTION)" \
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
