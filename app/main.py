from fastapi import FastAPI
from app.routes import user, leads, accounts, opportunities, deals, activities
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.utils.logger import get_logger

logger = get_logger(__name__)

__version__ = "0.0.1"



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("App is starting up...")
    try:
        yield
    except Exception as e:
        # Code here will be executed if the app crashes
        logger.info(f"App is about to crash! Error: {e}")
        raise  # Ensure the exception is still raised
    finally:
        # Shutdown event
        logger.info("App is shutting down...")
        
app = FastAPI(title="CRM System API", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(leads.router, prefix="/leads", tags=["Leads"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
app.include_router(deals.router, prefix="/deals", tags=["Deals"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])

@app.get("/")
def root():
    return {"message": "CRM API is running"}
