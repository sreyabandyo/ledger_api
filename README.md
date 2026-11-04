# Banking Ledger API

A RESTful banking ledger API built with Python, FastAPI, MySQL and SQLAlchemy. The application supports account management, deposits, withdrawals, money transfers and persistent transaction history.

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Database Migrations:** Alembic
- **Containerisation:** Docker Compose
- **API Documentation:** Swagger UI

## Features

- Create and retrieve bank accounts
- Deposit and withdraw money
- Transfer money between accounts
- Prevent withdrawals and transfers with insufficient funds
- Record deposits, withdrawals and transfers
- Retrieve transaction history for individual accounts
- Use database transactions to save balance updates and transaction records together
- Use row-level locking during balance updates

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API health |
| GET | `/accounts` | Retrieve accounts |
| POST | `/accounts` | Create an account |
| GET | `/accounts/{account_id}` | Retrieve an account |
| POST | `/accounts/{account_id}/deposit` | Deposit money |
| POST | `/accounts/{account_id}/withdraw` | Withdraw money |
| POST | `/transfers` | Transfer between accounts |
| GET | `/accounts/{account_id}/transactions` | View transaction history |

## Database Design

The application uses two main database tables:

**Accounts**
- Account ID
- Account holder name
- Balance stored in pence

**Transactions**
- Transaction ID
- Associated account ID
- Transaction type
- Amount in pence
- Creation timestamp

Money is stored as integer pence values to avoid floating-point rounding errors.

## Transaction Handling

Deposits and withdrawals update account balances and create corresponding transaction records.

Transfers generate two records:
- `transfer_out` for the sender
- `transfer_in` for the receiver

SQLAlchemy database transactions ensure that balance updates and transaction records are committed together.

Row-level locking helps protect account balances during concurrent operations.

## Getting Started

### Prerequisites

- Python 3.14
- Docker Desktop
- Git

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sreyabandyo/ledger_api.git
   cd ledger_api
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configure the database connection using a local `.env` file. Do not commit database credentials to GitHub.

5. Start the MySQL database using Docker Compose:

   ```bash
   docker compose up -d
   ```

6. Apply database migrations:

   ```bash
   alembic upgrade head
   ```

7. Start the API:

   ```bash
   uvicorn main:app --reload --port 8001
   ```

8. Open the interactive API documentation:

   http://127.0.0.1:8001/docs

## API Documentation

FastAPI automatically generates interactive Swagger documentation.

Once the application is running, visit:

`http://127.0.0.1:8001/docs`

## Testing

The API has been manually tested using Swagger UI.

Verified scenarios include:
- Successful deposits and withdrawals
- Successful transfers between accounts
- Transaction history retrieval
- Nonexistent account handling with HTTP 404 responses

## Future Improvements

- Automated API tests using pytest
- Authentication and authorisation
- Pagination for transaction history
- Improved logging and monitoring
- CI/CD integration using GitHub Actions

## Author

Developed by [sreyabandyo](https://github.com/sreyabandyo).