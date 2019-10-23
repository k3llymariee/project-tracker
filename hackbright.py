"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student.
    
    Example:
        >>> get_student_by_github('jhacks')
        Student: Jane Hacker
        GitHub account: jhacks

    """

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    # fetchone will return None if no records returned
    if row:
        print("Student: {} {}\nGitHub account: {}".format(row[0], row[1], row[2]))
    else:
        print("No record of that student")

def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
        INSERT INTO students (first_name, last_name, github)
            VALUES (:first_name, :last_name, :github)    
        """

    db.session.execute(QUERY, {'first_name' : first_name,
                                'last_name' : last_name,
                                'github' : github})
    db.session.commit()
    print(f"Successully added student: {first_name} {last_name}")


def get_project_by_title(title):
    """Given a project title, print information about the project.

    EXAMPLE:
        >>> get_project_by_title('Markov')
        RESULT:
        ID: 1
        TITLE: Markov
        DESCRIPTION: Tweets generated from Markov chains
        MAX GRADE: 50
    """
    
    # psuedocode: 
    # pass in title to a query the looks up project info 
    # WHERE project_name = title
    # execute a query with a placeholder for the title
    # print information

    QUERY = """
        SELECT * FROM projects
        WHERE title = :title
        """

    cursor = db.session.execute(QUERY, {'title': title})

    result = cursor.fetchone()

    proj_id, title, description, max_grade = result  # unpack the resulting tuple

    print('RESULT:')
    print('ID:', proj_id)
    print('TITLE:', title)
    print('DESCRIPTION:', description)
    print('MAX GRADE:', max_grade)


def get_grade_by_github_title(github, title):
    """Print grade student received for a project.
    
    EXAMPLE:
    >>> get_grade_by_github_title('jhacks', 'Markov')
    GRADE: 10

    """
    
    QUERY = """
        SELECT grade FROM grades
        WHERE student_github = :student_github
            AND project_title = :project_title 
    """

    cursor = db.session.execute(QUERY, {'student_github': github,
                                        'project_title': title})

    result = cursor.fetchone()[0]

    print('GRADE:', result)

def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation.

    EXAMPLE:
        >>> assign_grade('k3llymariee', 'Markov', 5)
        Successfully added k3llymariee's grade of 5 for Markov

    """
    
    QUERY = """
        INSERT INTO grades (student_github, project_title, grade)
            VALUES (:github, :title, :grade)    
        """

    db.session.execute(QUERY, {'github': github, 
                                'title': title,
                                'grade': grade})

    db.session.commit()

    print(f'Successfully added {github}\'s grade of {grade} for {title}')

def add_project(title, description, max_grade):
    """ Create a new project and print a confirmation """

    QUERY = """
        INSERT INTO projects (title, description, max_grade)
            VALUES (:title, :decription, :max_grade)      
        """

    db.session.execute(QUERY, {'title': title,
                                'decription': description,
                                'max_grade': max_grade})

    db.session.commit()

    print(f'Successfully added {title} to the projects tables')

def get_all_grades(first_name, last_name):
    """ Print all grades for a student given their Github name

    Example:
        >>> get_all_grades('Jane', 'Hacker')
        Grades for Jane Hacker:
        **********
        Project Title: Markov
        Grade: 10
        **********
        Project Title: Blockly
        Grade: 2
        **********
    """

    QUERY = """
        SELECT 
            project_title, grade
        FROM grades
        JOIN students 
            ON students.github = grades.student_github
        WHERE students.first_name = :first_name
            AND students.last_name = :last_name
        """

    cursor = db.session.execute(QUERY, 
                                {'first_name': first_name, 
                                'last_name': last_name})

    results = cursor.fetchall()

    print(f"Grades for {first_name} {last_name}:")
    print('*' * 10)

    if len(results) == 0:
        print("No grades for this student")
    else:
        for result in results:
            project_title, grade = result
            print("Project Title:", project_title)
            print("Grade:", grade)
            print('*' * 10)


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack! # why isnt command part of args
            make_new_student(first_name, last_name, github)

        elif command == "new_project":
            max_grade = args[-1]
            title = args[0]  # we assume titles have no spaces
            description = ' '.join(args[1:-1])
            add_project(title, description, max_grade)

        elif command == "get_grades":
            first_name, last_name = args
            get_all_grades(first_name, last_name)

        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
