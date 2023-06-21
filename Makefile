TAGS := $(patsubst %.yaml,%,$(wildcard *.yaml))
TAGS := $(filter-out docker-compose,$(TAGS))

.PHONY: all $(TAGS)

all: $(TAGS)

$(TAGS):
	    @echo ""
	    @echo ""
	    @echo "building config for: ${@}.yaml"
	    @echo ""
	    @echo ""
	    @export TAG=$@ && podman-compose up -d --build --force-recreate

config:
	
	    @export TAG= && podman-compose up -d --build --force-recreate

	    

