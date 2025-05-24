include ../.env
export $(shell sed 's/=.*//' ../.env)

build:
	docker build -t $(HUB_URL)/$(APP_NAME)/data-science:$(DATA_SCIENCE_VERSION) .

publish:
	docker push $(HUB_URL)/$(APP_NAME)/datas-cience:$(DATA_SCIENCE_VERSION)
