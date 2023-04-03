from pathlib import Path

import whisper
from devtools import debug
from sanic import Sanic
from sanic.response import json

sanic = Sanic(__name__)

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

DATA = [
    [
        1566453600,
        1566453660,
        1566453720,
        1566453780,
        1566453840,
        1566453900,
        1566453960,
        1566454020,
        1566454080,
        1566454140,
        1566454200,
        1566454260,
        1566454320,
        1566454380,
        1566454440,
        1566454500,
        1566454560,
        1566454620,
        1566454680,
        1566454740,
        1566454800,
        1566454860,
        1566454920,
        1566454980,
        1566455040,
        1566455100,
        1566455160,
        1566455220,
        1566455280,
        1566455340,
        1566455400,
        1566455460,
        1566455520,
        1566455580,
        1566455640,
        1566455700,
        1566455760,
        1566455820,
        1566455880,
        1566455940,
        1566456000,
        1566456060,
        1566456120,
        1566456180
    ],
    [
        0.54,
        0.15,
        0.16,
        0.15,
        0.19,
        0.26,
        0.32,
        0.15,
        0.15,
        0.28,
        0.29,
        0.33,
        0.18,
        0.17,
        0.17,
        0.33,
        0.32,
        0.23,
        0.15,
        0.15,
        0.24,
        0.29,
        0.16,
        0.17,
        0.17,
        0.45,
        0.28,
        0.16,
        0.17,
        0.17,
        0.24,
        0.3,
        0.19,
        0.19,
        0.17,
        0.24,
        0.29,
        0.22,
        0.18,
        0.28,
        0.26,
        0.17,
        0.3,
        0.16
    ],
    [
        14.02,
        14.01,
        14.01,
        14.01,
        14.01,
        14.03,
        14.03,
        14.02,
        14.02,
        14.03,
        14.03,
        14.04,
        14.03,
        14.03,
        14.03,
        14.02,
        14.04,
        14.03,
        14.03,
        14.03,
        14.03,
        14.03,
        14.03,
        14.03,
        14.03,
        14.03,
        14.04,
        14.04,
        14.03,
        14.03,
        14.03,
        14.04,
        14.03,
        14.04,
        14.04,
        14.04,
        14.05,
        14.03,
        14.03,
        14.03,
        14.04,
        14.04,
        14.05,
        14.03
    ],
    [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0.01,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
    ]
]


def get_data(whisper_file):
    pass


@sanic.route("/data.json")
async def data(request):
    metrics_infos = []

    for whisper_file in Path("data").glob("*.wsp"):
        header = whisper.info(whisper_file)
        metric_name = whisper_file.stem
        print(metric_name)

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

    # # data = whisper.fetch()
    # return json({
    #     "opts": OPTS,
    #     "data": DATA,
    # })


sanic.static("/", Path(__file__).parent / "templates" / "index.html", name="index")
sanic.static("/static/", Path(__file__).parent / "static", name="static")

# Main
if __name__ == "__main__":
    sanic.run(host="0.0.0.0", port=5000, debug=True, auto_reload=True)
