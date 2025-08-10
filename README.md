# Multifunctional Chalcogenide Materials Database @ Zhou Research Group, University of Kansas

If you're reading this, you're probably a developer looking to work on this database. If not, don't worry about this repository! 

## Tech Stack

In simplest terms, a tech stack is the tools and services used in a project. There are many moving parts to this:

1. [Vercel](https://vercel.com/): frontend and serverless backend
    - We host two things here: our fastapi python backend (`./app/api/.`) and our Svelte frontend (`./app/.`).
2. [Supabase](https://supabase.com/): PostgreSQL database hosting
    - In `./migration/` there are scripts to: initialize a sql database and populate it from the json files. Once this is done, dump the database to a .sql file and push it to supabase, where it will then be accessible to our website.
    - Our fastapi backend relies on the supabase library to query the database.

## Project dependencies

This project uses [Poetry](https://python-poetry.org/) and [npm](https://www.npmjs.com/) to handle dependency management for python and the frontend, respectively. Please check their websites for installation instructions.

Additionally, [PostgreSQL](https://www.postgresql.org/) is required to make changes to the database, so please install this if you wish to do so.

Once installed:

1. `cd` to the repository root, containing `pyproject.toml` and run `poetry lock && poetry install` to install all python dependencies into a virtual environment.
2. `cd` to `./app/` and run `npm install` to install all node dependencies to work on the frontend.

> ### Disclaimer for devenv users & those interested in devenv 
> A `devenv.nix` and `devenv.yaml` configuration file have been included in the repository, which may provide a quick and easy way to get started with the project.
> 
> [devenv](https://devenv.sh/) is a declarative nix-based configuration tool for developers. Devenv can significantly reduce the effort needed to configure poetry and npm. At the time of writing, this is __only__ available on unix-based systems (Mac and Linux), unless you wish to use WSL on Windows (The author of this discourages such behavior, since nix via WSL is generally an unpleasant experience). 
> 
> Assuming devenv is set up, npm, poetry, and postgres will be installed when navigating to this repository in a terminal. Packages are installed normally using poetry and npm, as described above.

## Working on the PostgreSQL database

Before discussing how to make changes to the data here, you should understand how to initialize and push a database to production. Assuming you are starting fresh, having just installed the project dependencies:

1. **Create** a local database with: `psql -U postgres -c "CREATE DATABASE local_db;"`.
2. **Populate** the database with the necessary schema with: `psql -U postgres -d local_db -f ./migration/v5_create_database.sql`.
3. **Parse** all json files in `./json/`, and populate the database with: `poetry run python ./migration/v5_populate_database_from_json.py`.
4. **Dump** the local database to a .sql file which can be uploaded by running: `pg_dump -U postgres -h localhost -d local_db > ./migration/db_dump.sql`.
5. **Push** the database to Supabase by running: `psql -h db.akpcvtofvdtynqzshweu.supabase.co -p 5432 -d postgres -U postgres < ./migration/db_dump.sql`
