"""
Edited version of discordbotdash a dashboard
"""
from . import app
def opendash(init_bot):
    """
    Opens the webserver
    """
    app.startApp(init_bot)
