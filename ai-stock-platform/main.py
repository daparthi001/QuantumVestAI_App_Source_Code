from fastapi import FastAPI
from webapi import sentiment, admin, whitepaper_analysis

app = FastAPI()

app.include_router(sentiment.router)
app.include_router(admin.router)
app.include_router(whitepaper_analysis.router)