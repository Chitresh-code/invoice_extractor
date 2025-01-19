# Invoice Extractor

## Overview
Invoice Extractor is a web application that allows users to upload PDF files of invoices, process them using LLM models, and extract relevant data into an Excel file. The application supports user authentication and provides different views for admin and regular users.

## Features
- User authentication (login, registration, logout)
- PDF file upload and processing
- AI-based data extraction from PDF files
- Data export to Excel format
- Admin view to manage users

## Technologies Used
- Flask (Python web framework)
- Flask-Login (User authentication)
- Gunicorn (WSGI HTTP server)
- Docker (Containerization)
- Docker Compose (Multi-container Docker applications)
- HTML, CSS, JavaScript (Frontend)
- Jinja2 (Templating engine)
- PostgreSQL (Database, hosted on Neon)

## Setup and Installation

### Prerequisites
- Docker
- Docker Compose

### Steps
1. Clone the repository:
    ```sh
    git clone https://github.com/Chitresh-code/invoice_extractor.git
    cd invoice_extractor
    ```

2. Build and run the Docker containers:
    ```sh
    docker-compose up --build
    ```

3. Access the application at `http://localhost:5000`.

## Usage

### User Authentication
- **Register**: Create a new account.
- **Login**: Access your account.
- **Logout**: Sign out of your account.

### PDF Upload and Processing
1. Login to your account.
2. Upload a PDF file of an invoice.
3. The application will process the PDF and extract relevant data.
4. Download the extracted data in Excel format.

### Admin View
- Admin users can view and manage all registered users.
- The admin user can only be made quering the database manually from developer's side for more security.

## Project Structure
```html
invoice_extractor/
│
├── src/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   ├── preprocess.py
│   ├── postprocess.py
├── templates/
│   ├── admin.html
│   ├── index.html
│   ├── login.html
│   ├── download.html
├── static/
│   ├── # static files like css and js.
├── logs/
│   ├── # log files for every module like app.log, src.database.log etc.
├── .env
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
```

## Environment Variables
- `APP_SECRET_KEY`: Secret key for Flask sessions.
- `GEMINI_API_KEY`: API key to use Google Gemini's LLM models.
- `DATABASE_URL`: URL for PostgreSQL Database from Neon.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Links
- [GitHub Repository](https://github.com/Chitresh-code/invoice_extractor)
- [Live Application](https://invoice-extractor-yh0m.onrender.com/)

## Contact
For any inquiries, please contact [gychitresh1290@gmail.com].