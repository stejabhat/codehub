# CodeHub

A code snippet sharing platform with a cosmic vintage theme. Built with Django and Tailwind CSS.

## Features

### Authentication
- User registration & login
- Protected routes

### Snippet Management
- Create, edit, delete snippets
- Syntax highlighting (Pygments)
- File upload
- Tags

### Collaboration
- Comments on snippets
- Suggest code edits
- Upvote/downvote voting

### Advanced
- Version history with revert
- Fork snippets
- Collections (public/private)

### Notifications
- Comments, votes, suggestions

## Setup

```bash
cd codehub
python3 -m venv venv
source venv/bin/activate
pip install django pygments
python manage.py migrate
python manage.py runserver
```

## Tech Stack

- Django 4.2
- Tailwind CSS (CDN)
- Pygments

## URLs

| Route | Description |
|-------|-------------|
| `/` | Home |
| `/upload/` | New snippet |
| `/snippet/<id>/` | View |
| `/snippet/<id>/edit/` | Edit |
| `/snippet/<id>/versions/` | History |
| `/snippet/<id>/fork/` | Fork |
| `/collections/` | Collections |
| `/notifications/` | Notifications |
