"""
Discord bot flask webserver
"""
import asyncio
import inspect
import threading
from flask import Flask, request, url_for, redirect, render_template
import git
import sys
import logging
from waitress import serve

loop = asyncio.get_event_loop()
repo = git.Repo(search_parent_directories=True)
app = Flask(__name__)

extserv = Flask('ext-serv')

disabled_cogs = {}
disabled_commands = []

remote = None
bot = None


def get_prefix():
    """
    Gets the prefix for the bot

        Returns:

            prefix(function/str) prefix for bot
    """
    if inspect.isfunction(bot.command_prefix):
        return f"<Function> {bot.command_prefix.__name__}"
    return bot.command_prefix


def start_ws(init_bot):
    """
    Runs the flask app on a separate thread
    """

    global bot

    bot = init_bot
    # start on separate thread so it does not block bot
    threading.Thread(target=serve, args=(app,), kwargs={"listen": '*:5000'}).start()
    # Used for uptime tracking make sure to forward the port
    threading.Thread(target=serve, args=(extserv,), kwargs={"listen": '*:9391'}).start()


@extserv.route("/")
def isup():
    return {
        "Up": "Yes",
        "Down": "Use your eyes dumbass"
    }


@app.route('/data')
def data():
    global remote

    botdict = bot.__dict__
    keypairs = []
    for key in bot.vars:
        keypairs.append((key, botdict[key]))

    if hasattr(bot, "latencies"):
        latencies = bot.latencies
    else:
        latencies = [(0, bot.latency*1000)]

    cogcommands = {}
    for name, cog in bot.cogs.items():
        cogcommands[name] = []
        for command in cog.__cog_commands__:
            cogcommands[name].append((command.name, command.brief,))
    try:
        _remote = str(repo.remotes.origin.fetch()[0].commit)
        if _remote:
            if _remote != remote:
                remote = _remote
    except IndexError:
        pass

    return {
        'local': repo.head.object.hexsha,
        'remote': remote,
        'prefix': 'On Mention',
        'vars': keypairs,
        'shards': latencies,
        'cogs': cogcommands
    }


@app.route("/")
def render_static():
    """
    Homepage
    """
    return redirect(url_for("commands"))


@app.route("/manage", methods=["GET", "POST"])
def manage():
    if request.method == "POST":
        for item in request.form.items():
            if item[0] == 'reboot':
                bot.close_bot()
                sys.exit()
            if item[0] == 'update':
                gitcmd = git.cmd.Git(repo)
                gitcmd.pull()
            if item[0] == 'status':
                bot.status_str = item[1]
            if item[0] == 'speed':
                bot.loopspeed = int(item[1])
                bot.update.change_interval(seconds=int(item[1]))
                bot.update.restart()

    return render_template("manager.html", bot=bot, command_prefix=get_prefix())


@app.route("/commands", methods=["GET", "POST"])
def commands():
    """
    Commands webpage
    """

    cmddata = {}
    keys = []

    for cmd in bot.commands:
        if cmd.cog_name not in keys:
            keys.append(cmd.cog_name)
            cmddata[cmd.cog_name] = list()
        cmddata[cmd.cog_name].append(cmd)

    return render_template("commands.html", getsource=inspect.getsource, bot=bot,
                           command_prefix=get_prefix(), enabled_commands=cmddata, keys=keys)


@app.route("/shards", methods=["GET", "POST"])
def shards():
    """
    Webpage showing shard status
    """
    if request.method == "POST":
        return redirect(url_for("shards"))

    # get bot latencies if it is sharded, else get the bots only latency
    if hasattr(bot, "latencies"):
        latencies = bot.latencies
    else:
        latencies = [(0, bot.latency)]

    return render_template("shards.html", bot=bot, command_prefix=get_prefix(), latencies=latencies)
