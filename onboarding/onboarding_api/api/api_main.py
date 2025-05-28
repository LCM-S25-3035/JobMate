from fastapi import FastAPI
from api import resume, users

app = FastAPI()

# Register routers
app.include_router(resume.router, prefix="/resume", tags=["Resume"])
app.include_router(users.router, prefix="/users", tags=["Users"])