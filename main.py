import re
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="Credit Card Validator API", version="1.0.0")

# Simple in-memory rate limiting
rate_limit_store = {}

def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != "cc-api-key-placeholder":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key

def rate_limit(request: Request):
    client_ip = request.client.host
    if client_ip in rate_limit_store:
        requests, window_start = rate_limit_store[client_ip]
        if time.time() - window_start < 60:
            if requests >= 100:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            rate_limit_store[client_ip] = (requests + 1, window_start)
        else:
            rate_limit_store[client_ip] = (1, time.time())
    else:
        rate_limit_store[client_ip] = (1, time.time())

class CardRequest(BaseModel):
    card_number: str

class CardResponse(BaseModel):
    valid: bool
    card_type: Optional[str]
    luhn_check: bool
    message: str

def get_card_type(number: str) -> Optional[str]:
    """Identify card type from number pattern."""
    number = number.replace(" ", "").replace("-", "")
    
    patterns = {
        "Visa": r"^4[0-9]{12}(?:[0-9]{3})?$",
        "Mastercard": r"^5[1-5][0-9]{14}$",
        "American Express": r"^3[47][0-9]{13}$",
        "Discover": r"^6(?:011|5[0-9]{2})[0-9]{12,15}$",
        "Diners Club": r"^3(?:0[0-5]|[68][0-9])[0-9]{11,12}$",
        "JCB": r"^(?:2131|1800|35\d{3})\d{11}$",
        "UnionPay": r"^62[0-5]\d{14,17}$"
    }
    
    for card_type, pattern in patterns.items():
        if re.match(pattern, number):
            return card_type
    
    # Check by length for Visa variants
    if len(number) in [13, 16, 19] and number.startswith("4"):
        return "Visa"
    
    return None

def luhn_check(number: str) -> bool:
    """Validate card number using Luhn algorithm."""
    number = number.replace(" ", "").replace("-", "")
    
    if not number.isdigit():
        return False
    
    digits = [int(d) for d in number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    
    return checksum % 10 == 0

@app.get("/health")
def health():
    return {"status": "ok", "service": "cc-validator"}

@app.post("/validate", dependencies=[Depends(rate_limit)])
def validate_card(request: CardRequest, _: str = Depends(verify_api_key)):
    number = request.card_number.replace(" ", "").replace("-", "")
    
    if not number or not number.isdigit():
        return CardResponse(
            valid=False,
            card_type=None,
            luhn_check=False,
            message="Invalid input: must be numeric digits only"
        )
    
    luhn_valid = luhn_check(number)
    card_type = get_card_type(number) if luhn_valid else None
    
    if luhn_valid and card_type:
        return CardResponse(
            valid=True,
            card_type=card_type,
            luhn_check=True,
            message=f"Valid {card_type} card number"
        )
    elif luhn_valid:
        return CardResponse(
            valid=False,
            card_type=None,
            luhn_check=True,
            message="Valid format but unknown card type"
        )
    else:
        return CardResponse(
            valid=False,
            card_type=None,
            luhn_check=False,
            message="Invalid card number (Luhn check failed)"
        )

@app.post("/detect-type", dependencies=[Depends(rate_limit)])
def detect_type(request: CardRequest, _: str = Depends(verify_api_key)):
    card_type = get_card_type(request.card_number)
    if card_type:
        return {"card_type": card_type, "detected": True}
    return {"card_type": None, "detected": False}