#!/bin/sh

echo "Migrate the Database at startup of project"

python source/manage.py makemigrations
# Wait for few minute and run db migraiton
while ! python source/manage.py migrate  2>&1; do
   echo "Migration is in progress status"
   sleep 3
done

echo "Django docker is fully configured successfully."
