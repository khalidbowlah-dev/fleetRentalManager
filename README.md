# Fleet Rental Manager 🚚

A full-stack Python web application designed to manage heavy-duty vehicle inventory, track dynamic rental pricing, and prevent overlapping reservations. Built using Flask and SQLite3.

## Features Completed
* **User Authentication:** Secure registration and login using hashed passwords.
* **Fleet Inventory Management (US1):** Add and list multiple vehicle instances (e.g., Howo H300, GMC Sierra).
* **Booking Engine (US2 & US3):** Users can select date ranges. The system automatically calculates total costs based on daily rates and rejects overlapping booking dates to prevent double-booking.
* **Automated Status Tracking:** Homepage inventory dynamically updates vehicle status to "Rented" or "Available" based on the current calendar date compared to active database reservations.
* **User Dashboard:** Logged-in users can view their active reservation history and cost receipts.
* **Professional UI:** Fully responsive CSS styling matrix applied across all templates.

## Tech Stack
* **Backend:** Python 3, Flask framework
* **Database:** SQLite3 (Relational architecture with Foreign Keys)
* **Frontend:** HTML5, CSS3, Jinja2 Templating

## How to Run This Project Locally

**1. Clone the repository and navigate into the directory:**
`git clone https://github.com/khalidbowlah-dev/fleetRentalManager.git`
`cd fleetRentalManager`

**2. Install required dependencies:**
`pip install flask werkzeug`

**3. Run the application:**
`python app.py`

**4. Access the web interface:**
Open your web browser and navigate to `http://127.0.0.1:5000`
