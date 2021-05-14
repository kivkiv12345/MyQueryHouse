Please see "requirements.txt" for packages needed and used in the creation of this application.
Certain libraries or classes are borrowed from third party sources.

The application is intended to be run from the command line (ideally using a virtual environment).
To do this; perform the following from the command line:
-> Navigate to the directory of MyQueryHouse/
-> Execute: "python3 -m venv env"
-> Execute: "source env/bin/activate"
-> Execute: "pip3 install -r requirements.txt"
-> Execute: "python3 app.py"

The application also includes unit tests, perform the following to run them:
-> Execute "python3 unit_tests.py"


In terms of boring afterthoughts:
Although it might've increased the code complexity slightly,
i've decided to prevent the user from running importation
modules directly, by raising SystemExit in the corresponding modules.
In addition; I also set out to keep each module below 500 lines of code,
and to scope them to different levels of complexity.
I took these measures to keep the program comprehensible at scale,
as I have yet to write many larger programs from scratch.

In relation to these factors:
I also attempted to keep certain modules/layers separate (such as the ORM layer),
although; this may not have been immediately obvious.
I did this in hopes of reusing parts of the program for future projects.
Lest existing solutions, such as: SQLAlchemy, suffice sufficient improvements;
in which case, i might use them instead.

In any case:
Having created my own 'ORM' has been quite the interesting experience.
for this reason; i will probably attribute the majority of the educational experience to its creation.
It should be noted however, that I also see great value in the ease of use and quality of the Python/Docker-API.
It's therefore very possible that any of my future programmatic use of Docker, may happen using it.
Though i have no lack of critique for Tkinter, i will also reluctantly admit
that sensible use of walrus operators and Frame widgets make the framework atleast somewhat tolerable.

Overall; my biggest regret is having to deliver a program,
which undoubtedly still includes loose ends and unfinished features.
In all honesty, swiftness has certainly not been my greatest virtue during its creation.
But in my own defense, i will attribute atleast some of these setbacks to overengineering.

I am optimistic that i will find this past month's accomplishment
as a great inspiration and value for any future projects.
