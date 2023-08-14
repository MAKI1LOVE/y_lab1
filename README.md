# y_lab1
First and second task.

## Requirements
* python3
* docker-compose

## Install
Change `.env.example` as you need and copy it to `.env`.

Run `docker-compose up -d`.

Run tests with `docker-compose -f docker-compose-test.yml up --abort-on-container-exit`

## Using excel to update menus
To update menus from excel file you need to create folder `admin` in `app` root and put there `Menu.xlsx` file. It is already presented.

If no root is presented or file has different name, celery task will do nothing.

If you want to change excel menus, you should not change `id` of menus, submenus and dishes, they are used to update presented items.
But you can easily change other values.

Also you should keep excel structure: for menus no zero cells, for submenus 1 zero cell, for dishes 2 zero cells.

## Star tasks
Task 2 * - make one query for `/api/v1/menus` endpoint in `app/src/api/v1/menus/crud.py:get_all_menus()`
