all: update install clean

update:
	cmd=$$(sed '/^\s/ d' packages.txt 2> /dev/null | awk '{ print $$1 }' | sed 's/AUR\///' | tr '\n' ' '); \
	if [ "$$cmd" == "" ];then \
		sudo bauerbill -Su --aur-only; \
	else \
		sudo bauerbill -S $$cmd --aur-only; \
	fi;

install: build
	cp build-make build/Makefile
	$(MAKE) -C build all

clean:
	rm -rf build
	rm -rf packages.txt
