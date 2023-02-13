# Rates Exercise

A solution for the [rates-task](https://github.com/xeneta/ratestask) exercise.

To run this locally, you can follow the steps in Initialization for an instant setup.
You can opt to do this manually too if you follow the steps in Manual Setup.

# Instant Setup

## Initialization via Docker

For a one time setup and run, you may run the following command:

```bash
docker compose up --build api
```

The app is running on http://localhost:5000

## Known Issues

When re-running the `docker compose up` command, you might encounter a `Permission denied` error involving the created volume `data`. To mitigate, you may run the following first:

```bash
 sudo chmod 777 data
```

# Manual Setup

Do this only if you want to do a manual setup over the instant setup + initialization via Docker above.

## Setup your local run

As this uses the [rates-task](https://github.com/xeneta/ratestask) resources (initialized dataset), we can use its [corresponding Dockerfile](https://github.com/xeneta/ratestask/blob/trunk/Dockerfile) also found in `task/` folder for our database:

```bash
> cd rates-exercise/task/
> docker build -t ratestask .                                           # this builds the image based on the Dockerfile
> docker run -p 0.0.0.0:5432:5432 --name ratestask ratestask            # this instantiates the container using the `ratestask` image
> docker exec -e PGPASSWORD=ratestask -it ratestask psql -U postgres    # this runs the Postgres instance for database connection
```

Then, use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies:

```bash
> cd ..                                     # returns us to root folder of rates-exercise
> pip install -r requirements.txt
```

## Running the application

Run the following in your terminal:

```bash
> flask run
```

The app is running on http://localhost:5000

## Running the tests

Run the tests with:

```bash
>  py.test test_app.py 
```

To run tests with coverage:

```bash
>  py.test test_app.py --cov=.
```

If you use VS Code and have the [Coverage Gutters](https://marketplace.visualstudio.com/items?itemName=ryanluker.vscode-coverage-gutters) extension, you can also use:

```bash
>  py.test test_app.py --cov-report xml:cov.xml --cov=.
```

# Structure
```
- sql/                  - Contains SQL files
- task/                 - Copy of `ratestask` repository
- app.py                - Main application
- config.py             - Config file
- constants.py          - Contains constants, such as raw SQL strings
- helpers.py            - Contains helper functions
- test_app.py           - Tests for main application
- Dockerfile            - Docker file for running the application
- docker-compose.yml    - Docker compose YAML file for running both the database and application 
```