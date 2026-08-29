from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.audit import log_action
from app.core.limiter import limiter

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_in: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user. Keep it open for initial provisioning.
    """
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
    
    # Also check id
    if session.get(User, user_in.id):
        raise HTTPException(
            status_code=400,
            detail="The user with this ID already exists."
        )

    user = User(
        id=user_in.id,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    log_action(session, "register_user", "user", user.id, user.id, {"email": user.email, "role": user.role})
    
    return user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Using form_data.username to lookup by email.
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.id, "email": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

ROLE_PERMISSIONS = [
    {
        "role": "admin",
        "description": "Full administrative control of the system",
        "permissions": ["Manage Users", "Manage Devices", "Trigger OTA Updates", "View Audit Logs", "Configure Machines", "File Uploads"]
    },
    {
        "role": "faculty",
        "description": "Laboratory faculty and instructors",
        "permissions": ["View Devices", "Trigger OTA Updates", "Configure Machines", "File Uploads"]
    },
    {
        "role": "technician",
        "description": "Maintenance and hardware technicians",
        "permissions": ["View Devices", "Trigger OTA Updates", "Manage Maintenance Records", "Restart Devices"]
    },
    {
        "role": "student",
        "description": "Regular students and guests",
        "permissions": ["Public Chat Only"]
    }
]

@router.get("/roles")
def list_system_roles():
    """
    Returns the read-only authorization system role matrix.
    """
    return ROLE_PERMISSIONS

