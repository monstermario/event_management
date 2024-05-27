# Event Management System

## Overview

The Event Management System is a RESTful API built using Django and Django REST Framework. It allows users to manage events, including creating, editing, viewing, and registering for events. The system features secure authentication with JWT token rotation.

## Features

- User registration and authentication
- Token rotation with JWT (access token and refresh token)
- Create, edit, and delete events
- View all events and events created by the user
- Register and unregister for events
- Event capacity management
- Comprehensive API documentation with Swagger and ReDoc
- Unit and integration tests

## Technologies Used

- Python
- Django
- Django REST Framework
- SQLite (default database)
- JWT (JSON Web Tokens)
- Swagger (drf-yasg)

## Getting Started

### Prerequisites

- Python
- Django
- Django REST Framework
- SQLite

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/monstermario/event_management.git
    cd event_management
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate   
    # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply the migrations:
    ```sh
    python manage.py migrate
    ```

5. Create a superuser:
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```sh
    python manage.py runserver
    ```

7. Access the API documentation:
    - Swagger: `http://localhost:8000/swagger/`
    - ReDoc: `http://localhost:8000/redoc/`

## Running Tests
To run the tests, use the following command:

  ```json
  python manage.py test
  ```
## License
This project is licensed under the MIT License. See the LICENSE file for details.
