from tgbot.data.models import *

# ------------------------------------------------------------------------------------------------------
c_id = Courses.get_or_create(title='Курс 1', z_index=10, testing=False)[0].id

Pages.get_or_create(course_id=c_id, z_index=10,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                             'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                             'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                             'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                             'diam sit. Vestibulum lorem sed risus ultricies tristique nulla. '
                             'Porta nibh venenatis cras sed felis eget velit. Neque egestas '
                             'congue quisque egestas diam in arcu cursus euismod. Ullamcorper '
                             'dignissim cras tincidunt lobortis feugiat vivamus at augue eget. '
                             'Sapien pellentesque habitant morbi tristique senectus et netus et '
                             'malesuada. Tempor nec feugiat nisl pretium. Purus viverra accumsan '
                             'in nisl nisi scelerisque.'))

Pages.get_or_create(course_id=c_id, z_index=20,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                             'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                             'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                             'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra  diam sit.'))

Pages.get_or_create(course_id=c_id, z_index=30,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'))

# ------------------------------------------------------------------------------------------------------
c_id = Courses.get_or_create(title='Курс 2', z_index=20, testing=True)[0].id

Pages.get_or_create(course_id=c_id, z_index=10,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                             'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                             'scelerisque in dictum non consectetur a.'))

q_id = Questions.get_or_create(course_id=c_id, plural=False, various=True, z_index=30,
                               text='Что где когда и почему бы и да ?')[0].id
Answers.get_or_create(question_id=q_id, right=False, text='Потому что да (не правильно)')
Answers.get_or_create(question_id=q_id, right=False, text='Потому что нет (не правильно)')
Answers.get_or_create(question_id=q_id, right=True, text='Я белый лебедь ... (правильно)')

q_id = Questions.get_or_create(course_id=c_id, plural=True, various=True, z_index=20,
                               text='Выбери четный числа')[0].id
Answers.get_or_create(question_id=q_id, right=False, text='1 (не правильно)')
Answers.get_or_create(question_id=q_id, right=True, text='2 (правильно)')
Answers.get_or_create(question_id=q_id, right=False, text='3 (не правильно)')
Answers.get_or_create(question_id=q_id, right=True, text='4 (правильно)')

q_id = Questions.get_or_create(course_id=c_id, plural=False, various=False, z_index=10,
                               text='Введи слово "кот"')[0].id
Answers.get_or_create(question_id=q_id, right=False, text='кот')

# ------------------------------------------------------------------------------------------------------
c_id = Courses.get_or_create(title='Курс 3', z_index=20, testing=False)[0].id


# ------------------------------------------------------------------------------------------------------
c_id = Courses.get_or_create(title='Курс 4', z_index=30, testing=False)[0].id

Pages.get_or_create(course_id=c_id, z_index=10,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                             'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                             'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                             'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                             'diam sit. Vestibulum lorem sed risus ultricies tristique nulla. '
                             'Porta nibh venenatis cras sed felis eget velit. Neque egestas '
                             'congue quisque egestas diam in arcu cursus euismod. Ullamcorper '
                             'dignissim cras tincidunt lobortis feugiat vivamus at augue eget. '
                             'Sapien pellentesque habitant morbi tristique senectus et netus et '
                             'malesuada. Tempor nec feugiat nisl pretium. Purus viverra accumsan '
                             'in nisl nisi scelerisque.'))

Pages.get_or_create(course_id=c_id, z_index=20,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                             'Dui id ornare arcu odio ut sem nulla pharetra diam. Velit '
                             'scelerisque in dictum non consectetur a. Dignissim cras tincidunt '
                             'lobortis feugiat vivamus. Ornare arcu odio ut sem nulla pharetra '
                             'diam sit. Vestibulum lorem sed risus ultricies tristique nulla.'))

Pages.get_or_create(course_id=c_id, z_index=30,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. '
                             'Dui id ornare arcu odio ut sem nulla pharetra diam.'))

Pages.get_or_create(course_id=c_id, z_index=40,
                    content=('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                             'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'))
