# Online Food Ordering System

## Project Structure
- `backend/`: Django + Django REST Framework backend.
- `frontend/`: Vue3 + Vite + Element Plus frontend.

## Prerequisites
- Python 3.10+
- Node.js 16+

## Setup & Run

### Backend
1. Navigate to backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start server:
   ```bash
   python manage.py runserver
   ```
   Server will run at `http://127.0.0.1:8000`.

### Frontend
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start development server:
   ```bash
   npm run dev
   ```
   Access the app at `http://localhost:5173`.

## Features
- **User Roles**: Customer, Merchant, Rider, Admin.
- **Authentication**: Register/Login with Token Auth.
- **Customer**: Browse shops, view menu, add to cart, place order, view order history.
- **Merchant**: View incoming orders, accept orders, update status (Cooking).
- **Rider**: View available orders (Cooking), grab orders, update status (Delivering -> Delivered).

## Notes
- Media files (images) are stored in `backend/media/`.
- Default database is SQLite `backend/db.sqlite3`.
