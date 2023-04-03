from __future__ import annotations

import mmap
import os
import struct
import time

import whisper


def mmap_file(filename):
    fd = os.open(filename, os.O_RDONLY)
    map = mmap.mmap(fd, os.fstat(fd).st_size, prot=mmap.PROT_READ)
    os.close(fd)
    return map


def read_header(map):
    try:
        (aggregationType, maxRetention, xFilesFactor, archiveCount) = struct.unpack(
            whisper.metadataFormat, map[: whisper.metadataSize]
        )
    except (struct.error, ValueError, TypeError):
        raise whisper.CorruptWhisperFile("Unable to unpack header")

    archives = []
    archiveOffset = whisper.metadataSize

    for i in range(archiveCount):
        try:
            (offset, secondsPerPoint, points) = struct.unpack(
                whisper.archiveInfoFormat,
                map[archiveOffset : archiveOffset + whisper.archiveInfoSize],
            )
        except (struct.error, ValueError, TypeError):
            raise whisper.CorruptWhisperFile("Unable to read archive %d metadata" % i)

        archiveInfo = {
            "offset": offset,
            "secondsPerPoint": secondsPerPoint,
            "points": points,
            "retention": secondsPerPoint * points,
            "size": points * whisper.pointSize,
        }
        archives.append(archiveInfo)
        archiveOffset += whisper.archiveInfoSize

    header = {
        "aggregationMethod": whisper.aggregationTypeToMethod.get(
            aggregationType, "average"
        ),
        "maxRetention": maxRetention,
        "xFilesFactor": xFilesFactor,
        "archives": archives,
    }
    return header


def dump_header(header):
    print("Meta data:")
    print("  aggregation method: %s" % header["aggregationMethod"])
    print("  max retention: %d" % header["maxRetention"])
    print("  xFilesFactor: %g" % header["xFilesFactor"])
    print("")
    dump_archive_headers(header["archives"])


def dump_archive_headers(archives):
    for i, archive in enumerate(archives):
        print("Archive %d info:" % i)
        print("  offset: %d" % archive["offset"])
        print("  seconds per point: %d" % archive["secondsPerPoint"])
        print("  points: %d" % archive["points"])
        print("  retention: %d" % archive["retention"])
        print("  size: %d" % archive["size"])
        print("")


def dump_archives(map, archives, options: Options):
    for i, archive in enumerate(archives):
        if not options.raw:
            print("Archive %d data:" % i)
        offset = archive["offset"]
        for point in range(archive["points"]):
            (timestamp, value) = struct.unpack(
                whisper.pointFormat, map[offset : offset + whisper.pointSize]
            )
            if timestamp == 0:
                continue
            if options.pretty:
                if options.time_format:
                    timestr = time.localtime(timestamp)
                    timestr = time.strftime(options.time_format, timestr)
                else:
                    timestr = time.ctime(timestamp)
            else:
                timestr = str(timestamp)
            if options.raw:
                print("%s:%.35g" % (timestamp, value))
            else:
                print("%d: %s, %10.35g" % (point, timestr, value))
            offset += whisper.pointSize
        print()


class Options:
    pretty = True
    raw = False
    time_format = None


def dump(path):
    if not os.path.exists(path):
        raise SystemExit('[ERROR] File "%s" does not exist!' % path)

    map = mmap_file(path)
    header = read_header(map)
    dump_header(header)
    options = Options()
    dump_archives(map, header["archives"], options)
