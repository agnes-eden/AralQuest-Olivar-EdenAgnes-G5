# AralQuest

AralQuest is a Django learning application for Grade 3–4 students and teachers in the Philippines. Its core feature is a simple learning-quest flow: teachers publish short multiple-choice questions, students answer them and receive feedback, and teachers can review results for their quests.

## Current features

- Student registration, login, logout, and profile management
- Separate student and teacher dashboards with role-based access
- Teacher-created quests in Reading, Language, or Math for Grade 3 or Grade 4
- Quest create, read, update, and delete screens for the teacher who created each quest
- Student quest browsing, answering, retries, and personal progress view
- Teacher results view showing the latest answer for each learner on a teacher's quest
- Teacher activity overview listing students who submitted answers to the teacher's quests
- PostgreSQL persistence through Django models and migrations

### Progress-tracking scope

Each learner's latest answer is stored per quest. Retrying updates that result; it does not create a full attempt history. Teachers can review results for quests they created and see a simple cross-quest activity summary of students who submitted answers. Competency/remediation analytics are not included yet. Offline/PWA functionality is also not included yet.

## User flows

### Student

1. Register an account; new registrations are assigned the Student role.
2. Log in and set Grade 3 or Grade 4 in **My profile**.
3. Open **Explore quests** and choose a published quest for that grade.
4. Submit an answer, view feedback, retry if desired, and review saved results in **My progress**.

### Teacher

1. Register an account, then have an administrator assign its profile the Teacher role.
2. Log in and open **Manage learning quests** from the teacher dashboard.
3. Create and publish a quest with a subject, grade, question, four distinct answer choices, and the correct answer.
4. Edit or delete that quest, open **View results** to review answers for one quest, or open **View student activity** to see learners who submitted answers across your quests.

Teachers can only manage their own quests. Students can only play published quests; if a student has a grade set, only quests for that grade are shown. Retrying updates the student's latest saved result for that quest.

## Requirements

- Python compatible with Django 6.1
- PostgreSQL
- pip

## Setup on Windows

Run these commands from the repository root in PowerShell.

1. Create a virtual environment and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

2. Create a PostgreSQL database and a `.env` file in the repository root:

   ```dotenv
   SECRET_KEY=replace-with-a-long-random-secret
   DEBUG=True
   DB_NAME=aralquest
   DB_USER=postgres
   DB_PASSWORD=your-local-database-password
   DB_HOST=localhost
   DB_PORT=5432
   DB_SSLMODE=disable
   ```

   `DB_SSLMODE=disable` is suitable for a local PostgreSQL server. For a hosted database, use the SSL mode required by the provider. Keep `.env` private; do not commit credentials.

3. Apply migrations and start the development server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

4. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

If PowerShell activation is unavailable, use the virtual environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Assigning the Teacher role

Public registration creates student accounts. To assign a teacher role:

1. Create an administrator account:

   ```powershell
   python manage.py createsuperuser
   ```

2. Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and sign in.
3. Open **Accounts → User profiles**, edit the profile for the intended teacher account, and set **Role** to **Teacher**.
4. Sign in with that teacher account and choose **Manage learning quests** from the teacher dashboard.

Registration creates a profile for each new account. Edit that existing profile rather than trying to add a duplicate.

## Validation

Quest fields are required and restricted to the supported subjects, grades, and answer labels. Answer choices must be distinct; repeating a choice displays **“Each answer choice must be different.”** on the quest form. The correct result is calculated on the server when a student submits an answer.

To see this validation in the UI, log in as a teacher, open **Create a quest**, enter the same text in two answer-choice fields, and submit. The quest is not saved until the choices are different.

## Tests

With the test database configured and accessible, run:

```powershell
python manage.py test
```

## Production note

The included settings are intended for development. Before deployment, configure a private `SECRET_KEY`, set `DEBUG=False`, restrict `ALLOWED_HOSTS`, and configure database SSL appropriately.
