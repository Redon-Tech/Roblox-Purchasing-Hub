# ToDo: Finish and test at home not in school

from quart import request

with open("./BOT/lib/bot/config.json") as config_file:
    config = json.load(config_file)

def requires_api_key(view):
    # Makes it so I dont repeat if apikey in every website base.
    @function.wraps(view)
    def wrapper(*args, **kwargs):
        apikey = request.headers["apikey"]
        if apikey == config["apikey"]:
            return view(*args, **kwargs)
        return {"errors": [{"message": "Improper API key passed"}]}