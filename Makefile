build:
	sudo docker build -t dmitriyvasil1986/expenses:latest .

push:
	sudo docker push dmitriyvasil1986/expenses

build-push: build push
