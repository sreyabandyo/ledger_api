from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    owner_name: str = Field(
        min_length=1,
        max_length=100
    )

class DepositRequest(BaseModel):
    amount_pence: int = Field(gt=0)

class WithdrawalRequest(BaseModel):
    amount_pence: int = Field(gt=0)

class TransferRequest(BaseModel):
    from_account_id: int = Field(gt=0)
    to_account_id: int = Field(gt=0)
    amount_pence: int = Field(gt=0)