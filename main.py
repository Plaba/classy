#!/usr/bin/env python3

import os
import click
import classy_config
from markdownify import markdownify
from datetime import datetime
    
CONFIG = classy_config.ClassyConfig()

@click.group()
def main():
    pass

@main.command()
@click.option('--path', default=CONFIG["school_workspace"], help='Path to the new school workspace')
def init(path):
    CONFIG["school_workspace"] = path

    CONFIG.ask_or_get('current_semester', 'Enter the current semester (YYYY-SPRING or YYYY-FALL)')
    CONFIG['semester_workspace'] = os.path.join(CONFIG['school_workspace'], CONFIG['current_semester'])

    os.makedirs(CONFIG['semester_workspace'], exist_ok=True)

    click.echo('Initialized semester workspace in {}'.format(CONFIG['semester_workspace']))

    CONFIG.ask_or_get('canvas_api_url', 'Enter your Canvas domain')
    CONFIG.ask_or_get('canvas_api_key', 'Enter your Canvas API key')

    api = CONFIG.get_canvas_api()
    user = api.get_current_user()

    click.echo('Logged in to Canvas as {}'.format(user.get_profile()["name"]))

    CONFIG['courses'] = {CONFIG['current_semester']: []}
    for course in api.get_courses():
        try:
            if click.confirm('Add {} to the semester workspace?'.format(course.course_code)):
                
                course_code = click.prompt('Save course as', default=course.course_code)
                CONFIG['courses'][CONFIG['current_semester']].append( {
                    'name': course.name,
                    'code': course_code,
                    'id': course.id
                })


                os.makedirs(os.path.join(CONFIG['semester_workspace'], course_code), exist_ok=True)
        except:
            pass
    
    CONFIG.save()

    for course in CONFIG['courses'][CONFIG['current_semester']]:
        click.echo('Adding assignments from course {}'.format(course['code']))
        
        for assignment in api.get_course(course['id']).get_assignments():

            if assignment.due_at is not None:
                assigned_date = datetime.strptime(assignment.due_at, '%Y-%m-%dT%H:%M:%SZ')
                assignment_folder_name = '{:0>2}-{:0>2}-{}'.format(assigned_date.month, assigned_date.day, assignment.name)
            else:
                assignment_folder_name = assignment.name

            if assignment.locked_for_user:                
                click.echo('Skipping assignment {} because it is locked'.format(assignment.name))
                continue

            assignment_path = os.path.join(CONFIG['semester_workspace'], course['code'], 'assignments', assignment_folder_name)
            os.makedirs(assignment_path, exist_ok=True)
            
            if assignment.description is not None and assignment.description != '':
                with open(os.path.join(assignment_path, 'README.md'), 'w') as f:
                    f.write(markdownify(assignment.description))

@main.command()
@click.argument('course_code', required=True, type=str)
def notes(course_code):

    found_course = False

    for course in CONFIG['courses'][CONFIG['current_semester']]:
        print(course)
        if course['code'] != course_code:
            continue
        found_course = True
        os.makedirs(os.path.join(CONFIG['semester_workspace'], course_code, 'notes'), exist_ok=True)

        today = datetime.today()
        notes_path = os.path.join(CONFIG['semester_workspace'], course_code, 'notes', '{:0>2}-{:0>2}.md'.format(today.month, today.day))
        with open(notes_path, 'w') as f:
            f.write('# {}: {}\n'.format(course["name"],today.strftime('%B %d, %Y')))
        os.system('code {}'.format(notes_path))
        break
    if not found_course:
        click.echo('Course {} not found'.format(course_code))

if __name__ == '__main__':
    main()
    