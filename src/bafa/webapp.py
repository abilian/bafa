from pathlib import Path

import whisper
from sanic import Sanic
from sanic.response import json

sanic = Sanic(__name__)

# Not used, kept for reference.
OPTS = {
    "title": "Server Events",
    "width": 1200,
    "height": 400,
    "series": [
        {},
        {
            "label": "CPU",
            "scale": "%",
            "stroke": "red",
            "width": 0.5
        },
        {
            "label": "RAM",
            "scale": "%",
            "stroke": "blue",
            "width": 0.5
        },
        {
            "label": "TCP Out",
            "scale": "mb",
            "stroke": "green",
            "width": 0.5
        }
    ],
    "axes": [
        {},
        {
            "scale": "%"
        },
        {
            "side": 1,
            "scale": "mb",
            "size": 60,
            "grid": {
                "show": False
            }
        }
    ]
}

def get_data(whisper_file):
    pass


@sanic.route("/data.json")
async def data(request):
    metrics_infos = []

    for whisper_file in Path("data").glob("*.wsp"):
        metric_name = whisper_file.stem

        # data = get_data(whisper_file)
        # header = whisper.info(whisper_file)
        # debug(header)

        (timeInfo, valueList) = whisper.fetch(whisper_file, 0)
        (fromTime, untilTime, step) = timeInfo

        data = [
            list(range(fromTime, untilTime, step)),
            valueList,
        ]
        assert len(data[0]) == len(data[1])

        opts = {
            "title": metric_name,
            "width": 1200,
            "height": 400,
            "series": [
                {},
                {
                    "label": metric_name,
                    "stroke": "red",
                    "width": 0.5
                },
            ],
            "axes": [
                {},
                {},
            ]
        }
        metrics_infos.append(
            {
                "name": metric_name,
                "data": data,
                "opts": opts,
            }
        )

    return json(metrics_infos)


sanic.static("/", Path(__file__).parent / "templates" / "index.html", name="index")
sanic.static("/static/", Path(__file__).parent / "static", name="static")

# Main
if __name__ == "__main__":
    sanic.run(host="0.0.0.0", port=5000, debug=True, auto_reload=True)
