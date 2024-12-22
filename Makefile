build:
	sudo docker build -t dmitriyvasil1986/expenses:latest .

push:
	sudo docker push dmitriyvasil1986/expenses

pre_commit:
	pre-commit run --show-diff-on-failure --color=always --all-files

build-push: build push
