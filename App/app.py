from fastapi import FastAPI, BackgroundTasks
from .Editor.editorRoutes import videditor_router
from App import bot
from App.utilis import WorkerClient, SERVER_STATE
from .Generate.generatorRoutes import generator_router, database, database_url, models

app = FastAPI()
manager = WorkerClient()


@app.on_event("startup")
async def startup_event():
    try:
        await models._create_all(database_url)
    except:
        pass
    finally:
        if not database.is_connected:
            await database.connect()
        await database.execute("pragma journal_mode=wal;")

    await bot.start()
    # if SERVER_STATE.MASTER:

    # response = await manager.register_worker()
    # if not response:
    #    print("Error registering worker")


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(videditor_router)
app.include_router(generator_router)
