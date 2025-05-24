include ../.env
export $(shell sed 's/=.*//' ../.env)

build:
	docker build -t $(HUB_URL)/$(APP_NAME)/data-analysis:$(DATA_ANALYSIS_VERSION) .

publish:
	docker push $(HUB_URL)/$(APP_NAME)/data-analysis:$(DATA_ANALYSIS_VERSION)
