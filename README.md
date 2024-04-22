# CENTRIBAL DJANGO APP
This is a Django app that allows users to create and manage their own events. The app is built using Django and Django Rest Framework


## Installation
This project was developed in Ubuntu 20.04, so the following instructions are for Ubuntu 20.04 or Linux distribution. If you are using another operating system, you may need to adjust the instructions accordingly. 
I cannot guarantee that the project will work on other operating systems such Windows.

1- `Docker` \
2- `Docker-compose` \
3- `Python 3.10` ```(I use pyenv to manage python versions)``` 

### Docker container of MySQL
- First you need to have Docker installed on your machine. You can download docker from [here](https://www.docker.com/products/docker-desktop)
You can run the following command to run a MySql container (also you can use the database generated in the [docker-compose.yaml](docker-compose.yaml) file, but is not recommended because will cross the data with the Django app container). Use the port  `3307` to avoid conflicts with the local MySql server.
```bash
docker run --name local-mysql -p 3307:3307 -e MYSQL_ROOT_PASSWORD=secret -d mysql:latest
```
- Once you have created the database container, you need to create the database for the Django app. You can do this by running the following command:
```bash
docker exec -it local-mysql bash
```
- Now that you are inside the container, you can run the following command to create the database:
```sql
mysql -u root -p
```
- Place the password configured ```secret``` in the Docker run command and then run the following command to create the database:
```sql
CREATE DATABASE IF NOT EXISTS centribal;
```
- Once you have created the database, you need to set the database by running the following command:
```sql
USE centribal;
```
- Now you can exit the mysql shell by running the following command (twice):
```sql
exit
```
### Docker compose for the Django app

Run the following command to build the docker images and run the container with a MySql database and the Django app.
```bash
docker-compose up -d
```

---
### Django app
Once you have created the database, you need set the environment variables in the `.env.development` file. \
In this case you need to access to the `local-mysql` container to get the IP address of the container. 
* You can run the following command to get the IP address of the container:
```bash
  docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' local-mysql
  ```
* Now you can set the variable `MYSQL_HOST` in the environment variable [.env.development](.env.development) file:
---

- Place in the root directory of the project, you can run the following command to install the required packages:
```bash
pip install --no-cache-dir -r requirements.txt
```
- Now you can run the following command to apply the migrations:
```bash
python manage.py migrate
```

#### Now you can run the following command to create a superuser for manage the app in your browser.   
- Use the following command to create the superuser
```bash
python manage.py createsuperuser
```
`optional` Visit the following URL to access the admin panel: http://127.0.0.1:8080/admin/ and login with the superuser credentials before created.

#### Now you can run the following command to initialize the server
- Run the following command to run the server, use port 8080 to avoid conflicts with the dockerized server
```bash
python manage.py runserver 8080
```
### Postman collection and environments
- You can import the postman collection and environment from the `postman` folder in the root directory of the project. 

There is a collection and two environments for the development environment and another for the docker environment. \
Import the collection and the environment in Postman and select the environment to use the API. \
`The only change between the environments is the PORT of the API, so you can use the same collection for both environments just changing the PORT in the postman Environment.`
* `Collection`: [Centribal Shop App collection](postman/Centribal Shop App.postman_collection.json), this is the collection of the API endpoints.
* `Environment`: [LOCAL Environment](postman/LOCAL.postman_environment.json), this is for the development so if you want to run tests or debug the app.
* `Environment`: [DOCKER Environment](postman/DOCKER.postman_environment.json), this  is for the dockerized app, so you can test the app in the docker container.


---
### Running the tests
- You can run the following command to run the tests:
```bash
python manage.py test
```
---

Now you have all set, I suggest you to use the postman collection to test the API endpoints, start creating a Product and then create an Order with the product created.\
Example:
1. Create a Product with the endpoint `POST /api/v1/products/new/` with this payload
```json
{
    "name": "White Shirts",
    "reference": "RF-wsh-01",
    "description": "Cotton White shirts with cartoons",
    "stock": 30,
    "currency": "EUR",
    "tax_rate": 21,
    "price_excluding_tax": 12.50
}
```
Once you have created the product, you can create an order with the endpoint `POST /api/v1/orders/new/` with this payload
```json
{
    "product": 3,
    "quantity": 20
}
```
---
This is all you need to run the app, if you have any questions or issues, please let me know. \
@Author: [Alejandro Cabo Marchena](https://www.linkedin.com/in/alejandrokbo/) \
@Email: [alejandro.cabo1991@gmail.com](mailto:alejandro.cabo1991@gmail.com) \
@Github: [Alejandrokbo](https://github.com/Alejandrokbo)

