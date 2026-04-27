import asyncio
from contextlib import asynccontextmanager

from langchain_google_community import GmailToolkit
from fastapi import FastAPI
from api.routes import router
from utils.poll_email import poll_emails


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Authenticate once at startup, then run polling loop as a background task
    toolkit = GmailToolkit()
    polling_task = asyncio.create_task(poll_emails(toolkit))
    yield
    # Cleanly cancel the polling loop on shutdown
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Agentic Support Assistant", lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)