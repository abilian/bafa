import psutil
from devtools import debug


# Quick hack. What's the correct way to get the function class ?
function_type = type(lambda: None)


DENYLIST = [
    "test",
    "process_iter",
    "pids",
    "pid_exists",
    "wait_procs",
    # Needs a parameter
    "disk_usage",
    # Needs root access
    "net_connections",
    #
]
DENYLIST_MACOSX = DENYLIST + [
    "cpu_freq",
]

KEEP_MACOSX = [
    "boot_time",
    "cpu_count",
    "cpu_percent",
    "cpu_stats",
    "cpu_times",
    "cpu_times_percent",
    "disk_io_counters",
    "net_io_counters",
    "sensors_battery",
    "swap_memory",
    "users",
    "virtual_memory",
]

KEEP_LINUX = KEEP_MACOSX + [
    "sensors_fans",
    "sensors_temperatures",
]


def play():
    for key in KEEP_LINUX:
        value = getattr(psutil, key)

        print(key)

        function = value
        result = function()

        assert hasattr(result, "_fields")

        print(78 * "-")


def get_metrics():
    keys = sorted(dir(psutil))

    collected_metrics = {}

    for key in keys:
        if key in DENYLIST_MACOSX:
            continue
        if key.startswith("_"):
            continue
        if not key[0].islower():
            continue

        value = getattr(psutil, key)
        if not callable(value):
            continue
        if not isinstance(value, function_type):
            continue

        # debug(key, getattr(psutil, key))

        if not key in KEEP_LINUX:
            continue

        # print(key)

        function = value
        result = function()

        if hasattr(result, "_fields"):
            d = dict(result._asdict())
            for k, v in d.items():
                collected_metrics[f"{key}.{k}"] = v
        else:
            if isinstance(result, (float, int)):
                collected_metrics[key] = result

    return collected_metrics


def main():
    debug(get_metrics())


if __name__ == "__main__":
    main()
