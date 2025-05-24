include ../.env
export $(shell sed 's/=.*//' ../.env)

build:
	docker build -t $(HUB_URL)/$(APP_NAME)/frontend:$(FRONTEND_VERSION) .

publish:
	docker push $(HUB_URL)/$(APP_NAME)/frontend:$(FRONTEND_VERSION)
