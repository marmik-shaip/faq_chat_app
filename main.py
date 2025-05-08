import logging
import os

import typer
from dotenv import load_dotenv

from commands.db_cmds import DbCmds

# pylint: disable=wrong-import-position
from common import helper
from container import Container

logging.basicConfig(level=logging.DEBUG)
os.makedirs("logs", exist_ok=True)
load_dotenv(".env")
app = typer.Typer()


@app.command("create-db")
def create_db():
    cmds = DbCmds()
    cmds("create-db")


@app.command("worker")
def run_worker(log_level: str = "DEBUG"):
    # pylint: disable=import-outside-toplevel,unused-import
    from celery_app import celery_app

    celery_app.conf.beat_schedule = {
        "check-form-filling-message-1-min": {
            "task": "ml.check_form_filling_message",
            "schedule": 60.0,
            "args": (),
            "options": {"queue": "insight-form-filling-tasks-queue"},
        },
    }

    worker = celery_app.Worker(
        queues=[
            "celery",
            "insight-form-filling-tasks-queue",
        ],
        loglevel=log_level,
        concurrency=8,
        beat=True,
    )
    worker.start()


@app.command("server")
def run_server():
    import uvicorn
    from server_app import fastapi_app

    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        log_config=os.path.join(os.path.dirname(__file__), "./configs/logging.ini"),
    )


# @app.command("add-job-in-celery")
# def add_job_in_celery():
#     from celery import signature
#     from celery_app import celery_app
#
#     def create_sig(name, args):
#         return signature(name, args=args, app=celery_app, immutable=True)
#
#     sig = create_sig("ml.print_message", args=("test message",))
#     sig.apply_async()


if __name__ == "__main__":
    app_container = Container()

    app_container.init_resources()
    app_container.wire(
        modules=[__name__]
        + helper.get_modules_under("commands")
        + helper.get_modules_under("routes")
        + helper.get_modules_under("services")
        + helper.get_modules_under("entities")
        + helper.get_modules_under("repositories")
    )

    app()
