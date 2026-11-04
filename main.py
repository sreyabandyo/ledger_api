from fastapi import FastAPI

from fastapi import Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Account, Transaction

from schemas import AccountCreate, DepositRequest, WithdrawalRequest, TransferRequest

from fastapi import FastAPI, Depends, HTTPException

app = FastAPI(
    title="Ledger API",
    description="A banking ledger API for accounts and transfers",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/accounts", status_code=201)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    new_account = Account(
        owner_name=account.owner_name
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return {
        "id": new_account.id,
        "owner_name": new_account.owner_name,
        "balance_pence": new_account.balance_pence
    }


@app.get("/accounts")
def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()

    return [
        {
            "id": account.id,
            "owner_name": account.owner_name,
            "balance_pence": account.balance_pence
        }
        for account in accounts
    ]

@app.get("/accounts/{account_id}")
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return {
        "id": account.id,
        "owner_name": account.owner_name,
        "balance_pence": account.balance_pence
    }

@app.post("/accounts/{account_id}/deposit")
def deposit(
    account_id: int,
    deposit: DepositRequest,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.id == account_id
    ).with_for_update().first()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    account.balance_pence += deposit.amount_pence

    transaction = Transaction(
        account_id=account.id,
        transaction_type="deposit",
        amount_pence=deposit.amount_pence
        )
    
    db.add(transaction)

    db.commit()
    db.refresh(account)

    return {
        "id": account.id,
        "owner_name": account.owner_name,
        "balance_pence": account.balance_pence
    }

@app.post("/accounts/{account_id}/withdraw")
def withdraw(
    account_id: int,
    withdrawal: WithdrawalRequest,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.id == account_id
    ).with_for_update().first()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if account.balance_pence < withdrawal.amount_pence:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds"
        )

    account.balance_pence -= withdrawal.amount_pence

    transaction = Transaction(
        account_id=account.id,
        transaction_type="withdrawal",
        amount_pence=withdrawal.amount_pence
    )

    db.add(transaction)

    db.commit()
    db.refresh(account)

    return {
        "id": account.id,
        "owner_name": account.owner_name,
        "balance_pence": account.balance_pence
    }


@app.post("/transfers")
def transfer_money(
    transfer: TransferRequest,
    db: Session = Depends(get_db)
):
    if transfer.from_account_id == transfer.to_account_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer to the same account"
        )

    account_ids = sorted([
        transfer.from_account_id,
        transfer.to_account_id
    ])

    accounts = (
        db.query(Account)
        .filter(Account.id.in_(account_ids))
        .order_by(Account.id)
        .with_for_update()
        .all()
    )

    account_map = {account.id: account for account in accounts}

    sender = account_map.get(transfer.from_account_id)
    receiver = account_map.get(transfer.to_account_id)

    if sender is None or receiver is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if sender.balance_pence < transfer.amount_pence:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds"
        )

    sender.balance_pence -= transfer.amount_pence
    receiver.balance_pence += transfer.amount_pence

    sender_transaction = Transaction(
        account_id=sender.id,
        transaction_type="transfer_out",
        amount_pence=transfer.amount_pence
    )

    receiver_transaction = Transaction(
        account_id=receiver.id,
        transaction_type="transfer_in",
        amount_pence=transfer.amount_pence
    )

    db.add(sender_transaction)
    db.add(receiver_transaction)

    db.commit()
    db.refresh(sender)
    db.refresh(receiver)

    return {
        "message": "Transfer successful",
        "from_account_id": sender.id,
        "to_account_id": receiver.id,
        "amount_pence": transfer.amount_pence,
        "sender_balance_pence": sender.balance_pence,
        "receiver_balance_pence": receiver.balance_pence
    }


@app.get("/accounts/{account_id}/transactions")
def get_transactions(
    account_id: int,
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.id.desc()).all()

    return [
        {
            "id": transaction.id,
            "account_id": transaction.account_id,
            "transaction_type": transaction.transaction_type,
            "amount_pence": transaction.amount_pence,
            "created_at": transaction.created_at
        }
        for transaction in transactions
    ]
