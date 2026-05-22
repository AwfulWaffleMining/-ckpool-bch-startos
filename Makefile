.PHONY: all build pack clean

PACKAGE_ID = ckpool-bch
VERSION     = 1.0.0
ARCH        = x86_64
IMAGE_ID    = ckpool

all: pack

# Build the Docker image
build:
	docker buildx build \
		--platform linux/amd64 \
		--output "type=docker,name=$(IMAGE_ID):latest" \
		--load \
		-f Dockerfile .
	mkdir -p images/$(ARCH)
	docker save $(IMAGE_ID):latest -o images/$(ARCH)/$(IMAGE_ID).tar

# Pack the s9pk
pack: build
	npm ci
	start-sdk pack
	@echo ""
	@echo "✅  Built: $(PACKAGE_ID).s9pk"
	@ls -lh $(PACKAGE_ID).s9pk

# Clean build artifacts
clean:
	rm -rf images/
	rm -f $(PACKAGE_ID).s9pk

# Sideload to a running StartOS instance (set STARTOS_IP env var)
install: pack
	@if [ -z "$(STARTOS_IP)" ]; then echo "Set STARTOS_IP=<ip> first"; exit 1; fi
	curl -sk -X POST \
		"https://$(STARTOS_IP)/api/v0/package/sideload" \
		-H "Content-Type: application/octet-stream" \
		--data-binary @$(PACKAGE_ID).s9pk
