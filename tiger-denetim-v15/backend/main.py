from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import connection, dashboard, triggers, deletions, changelog, snapshot, jobs, query, reports

app = FastAPI(title="Tiger Denetim API", version="1.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connection.router, prefix="/api", tags=["Connection"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(triggers.router, prefix="/api", tags=["Triggers"])
app.include_router(deletions.router, prefix="/api", tags=["Deletions"])
app.include_router(changelog.router, prefix="/api", tags=["Changelog"])
app.include_router(snapshot.router, prefix="/api", tags=["Snapshot"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
