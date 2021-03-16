"""
Discord bot flask webserver
"""
import inspect
import threading
from flask import Flask, request, url_for, redirect, render_template


app = Flask(__name__)

disabled_cogs = {}
disabled_commands = []

class Server:
    """
    Webserver Class
    """
    bot = None

    @staticmethod
    def get_prefix():
        """
        Gets the prefix for the bot

            Returns:

                prefix(function/str) prefix for bot
        """
        if inspect.isfunction(bot.command_prefix):
            return f"<Function> {bot.command_prefix.__name__}"
        return bot.command_prefix

    @staticmethod
    def start_ws(init_bot):
        """
        Runs the flask app on a seperate thread
        """

        global bot

        bot = init_bot

        # start on separate thread so it does not block bot
        threading.Thread(target=app.run).start()

    @staticmethod
    @app.route("/")
    def render_static():
        """
        Homepage
        """
        return redirect(url_for("commands"))

    @staticmethod
    @app.route("/cogs", methods=["GET", "POST"])
    def cogs():
        """
        Cog managment webpage
        """
        if request.method == "POST":
            checkbox_cogs = [item[0] for item in request.form.items()]

            # disable cog
            # copy to prevent size from changing during iteration
            for cog_name, cog in bot.cogs.copy().items():
                if cog_name not in checkbox_cogs:
                    # add cog's commands to disabled commands
                    for command in cog.__cog_commands__:
                        if command not in disabled_commands:
                            disabled_commands.append(command)

                    # remove cog and add to disabled
                    disabled_cogs[cog_name] = cog
                    bot.remove_cog(cog_name)

            # enable cog
            for cog in checkbox_cogs:
                if cog in disabled_cogs.keys():
                    # remove commands from disabled_commands
                    for cmd in disabled_cogs[cog].__cog_commands__:
                        if cmd in disabled_commands:
                            disabled_commands.remove(cmd)

                        # remove command if it already exists before the cog is added
                        if cmd.name in [command.name for command in bot.commands]:
                            bot.remove_command(cmd.name)

                    # search for cog and add if ticked on
                    # add cog back and remove from disabled
                    bot.add_cog(disabled_cogs[cog])
                    del disabled_cogs[cog]

            # clear form
            return redirect(url_for("cogs"))

        return render_template("cogs.html", bot=bot, command_prefix=cls.get_prefix(), getfile=inspect.getfile, enabled_cogs=bot.cogs.items(), disabled_cogs=disabled_cogs.items())

    @staticmethod
    @app.route("/commands", methods=["GET", "POST"])
    def commands():
        """
        Commands webpage
        """
        if request.method == "POST":
            # commands form
            if request.form["formName"] == "commands":

                checkbox_cmds = [item[0] for item in request.form.items()]

                # disable command
                for cmd in bot.commands:
                    if cmd.name not in checkbox_cmds:
                        # remove command and add to disabled
                        bot.remove_command(cmd.name)
                        disabled_commands.append(cmd)

                # enable command
                for cmd in checkbox_cmds:
                    # search for command and add if ticked on
                    for disabled_cmd in disabled_commands:
                        if cmd == disabled_cmd.name:
                            # add command back and remove from disabled
                            bot.add_command(disabled_cmd)
                            disabled_commands.remove(disabled_cmd)

            return redirect(url_for("commands"))

        cmddata = {}
        keys = []
        for cmd in bot.commands:
            if cmd.cog_name not in keys:
                keys.append(cmd.cog_name)
                cmddata[cmd.cog_name] = list()

        for cmd in bot.commands:
            cmddata[cmd.cog_name].append(cmd)

        return render_template("commands.html", getsource=inspect.getsource, bot=bot, command_prefix=get_prefix(), enabled_commands=cmddata, disabled_commands=disabled_commands, keys=keys)

    @staticmethod
    @app.route("/shards", methods=["GET", "POST"])
    def shards():
        """
        Webpage showing shard status
        """
        if request.method == "POST":
            return redirect(url_for("shards"))

        # get bot latencies if it is sharded, else get the bot's only latency
        latencies = None
        if hasattr(bot, "latencies"):
            latencies = bot.latencies
        else:
            latencies = [(0, bot.latency)]

        return render_template("shards.html", bot=bot, command_prefix=get_prefix(), latencies=latencies)
