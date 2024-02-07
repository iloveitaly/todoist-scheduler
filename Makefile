.PHONY: build build-debug docker-push

IMAGE_NAME ?= $(shell gh repo view --json name --jq '.name' | tr -d '[:space:]')
IMAGE_TAG ?= latest
GITHUB_REPOSITORY ?= ghcr.io/$(shell gh repo view --json nameWithOwner --jq '.nameWithOwner' | tr -d '[:space:]')

# NOTE this requires a custom nixpacks build to work:
# 		 https://github.com/railwayapp/nixpacks/pulls?q=is%3Apr+author%3Ailoveitaly

# label is important here in order for the package to show up on the github repo
BUILD_CMD = nixpacks build . --name $(IMAGE_NAME) \
		--label org.opencontainers.image.source=https://github.com/$(GITHUB_REPOSITORY) \
		--platform linux/arm64/v8 \
		--tag $(IMAGE_TAG)

build:
	$(BUILD_CMD)

build-shell: build
	docker run -it $(IMAGE_NAME):$(IMAGE_TAG) bash -c 'source /opt/venv/bin/activate'

build-debug:
	$(BUILD_CMD) --out .

docker-push: build
	docker push $(IMAGE_NAME):$(IMAGE_TAG)