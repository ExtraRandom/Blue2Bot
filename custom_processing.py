import json

# TODO finish

async def process_custom(message):
    cmds_raw = read_file()
    cmds = json.loads(cmds_raw)
    if str(message.content) in cmds:
        print("yeet")


def read_file():
    try:
        with open("customs.json", "r") as f:
            rl = f.readlines()
            data = "".join(rl)

    except Exception as e:
        print("Error reading file: {}".format(type(e).__name__))







