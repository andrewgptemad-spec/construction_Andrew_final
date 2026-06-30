# Deploy on PythonAnywhere Free

This project is a normal Django app, so the easiest free deployment is PythonAnywhere.
Firebase Hosting is not a good match because it does not directly run a Django server.

## 1. Create the free account

Create a free Beginner account at PythonAnywhere. Your free site will look like:

```text
https://yourusername.pythonanywhere.com
```

## 2. Upload the project

Upload this project folder to PythonAnywhere, for example:

```text
/home/yourusername/construction_Andrew_final
```

If you want the existing local data, upload these too:

```text
db.sqlite3
media/
```

## 3. Create a virtual environment

Open a PythonAnywhere Bash console and run:

```bash
cd ~/construction_Andrew_final
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If PythonAnywhere offers a newer Python version in your account, use that version instead.

## 4. Configure environment variables

In the PythonAnywhere web app page, add these environment variables, replacing `yourusername`:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=make-a-long-random-secret-key-here
DJANGO_ALLOWED_HOSTS=yourusername.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_SSL_REDIRECT=True
```

To generate a secret key in the Bash console:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5. Prepare the database and static files

Run:

```bash
cd ~/construction_Andrew_final
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_data
python manage.py createsuperuser
```

Skip `seed_data` if you uploaded an existing `db.sqlite3` that already has your villas and categories.

## 6. Create the web app

In PythonAnywhere:

1. Open the **Web** tab.
2. Click **Add a new web app**.
3. Choose **Manual configuration**.
4. Choose the same Python version as your virtual environment.
5. Set **Source code** to:

```text
/home/yourusername/construction_Andrew_final
```

6. Set **Working directory** to:

```text
/home/yourusername/construction_Andrew_final
```

7. Set **Virtualenv** to:

```text
/home/yourusername/construction_Andrew_final/.venv
```

## 7. Configure the WSGI file

Open the WSGI configuration file from the PythonAnywhere Web tab and replace its contents with:

```python
import os
import sys

path = '/home/yourusername/construction_Andrew_final'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `yourusername` with your PythonAnywhere username.

## 8. Configure static and uploaded files

In the Web tab, add static file mappings:

```text
URL: /static/
Directory: /home/yourusername/construction_Andrew_final/staticfiles
```

```text
URL: /media/
Directory: /home/yourusername/construction_Andrew_final/media
```

## 9. Reload

Click **Reload** in the Web tab.

Open:

```text
https://yourusername.pythonanywhere.com
```

Log in with the superuser account you created.

## Important notes

- The free plan is good for a small personal app or demo.
- SQLite is acceptable for this small project, but only one person should edit data heavily at the same time.
- Uploaded invoices live in `media/`, so back up both `db.sqlite3` and `media/`.
- Do not use the old README default login on the public internet. Create a new strong admin password.
