# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright 2022 The NiPreps Developers <nipreps@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
"""Nipype settings file."""
import os
import sys
from pathlib import Path

_nipype_home = Path(
    os.getenv("NIPYPE_CONFIG_DIR", str(Path.home() / ".nipype"))
).absolute()
(_nipype_home / "log").mkdir(exist_ok=True, parents=True)


class _Config:
    """An abstract class forbidding instantiation."""

    _paths = tuple()

    def __init__(self):
        """Avert instantiation."""
        raise RuntimeError("Configuration type is not instantiable.")

    @classmethod
    def load(cls, settings, init=True):
        """Store settings from a dictionary."""
        for k, v in settings.items():
            if v is None:
                continue
            if k in cls._paths:
                setattr(cls, k, Path(v).absolute())
                continue
            if hasattr(cls, k):
                setattr(cls, k, v)

        if init:
            try:
                cls.init()
            except AttributeError:
                pass

    @classmethod
    def get(cls):
        """Return defined settings."""
        out = {}
        for k, v in cls.__dict__.items():
            if k.startswith("_") or v is None:
                continue
            if callable(getattr(cls, k)):
                continue
            if k in cls._paths:
                v = str(v)
            out[k] = v
        return out


class logging(_Config):
    """The logging section."""

    interface_level = "INFO"
    log_directory = str(_nipype_home / "log")
    log_rotate = 4
    log_size = 16384000
    log_to_file = False
    utils_level = "INFO"
    workflow_level = "INFO"


class execution(_Config):
    """The execution section."""

    check_version = True
    crashdump_dir = str(_nipype_home / "log")
    crashfile_format = "pklz"
    create_report = True
    hash_method = "timestamp"
    job_finished_timeout = 5
    keep_inputs = False
    local_hash_check = True
    matplotlib_backend = "Agg"
    parameterize_dirs = True
    plugin = "Linear"
    poll_sleep_duration = 2
    remove_node_directories = False
    remove_unnecessary_outputs = True
    single_thread_matlab = True
    stop_on_first_crash = False
    stop_on_first_rerun = False
    stop_on_unknown_version = False
    try_hard_link_datasink = True
    use_relative_paths = False
    write_provenance = False
    xvfb_max_wait = 10
    _cwd = Path.cwd().absolute()


class monitoring(_Config):
    """The monitoring section."""

    enabled = False
    sample_frequency = 1
    summary_append = True


class check(_Config):
    """The check section."""

    interval = 1209600


if (_nipype_home / "nipype.cfg").exists():
    from toml import loads

    for sectionname, settings in loads(
        (_nipype_home / "nipype.cfg").read_text()
    ).items():
        section = getattr(sys.modules[__name__], sectionname)
        for key, value in settings.items():
            setattr(section, key, value)


def __str__():
    from toml import dumps

    return dumps({
        sectionname: getattr(sys.modules[__name__], sectionname).get()
        for sectionname in ("logging", "execution", "monitoring", "check")
    })


def update():
    """Setup logging configuration."""
    import logging as _logging

    _logging.captureWarnings(True)
    _logging.basicConfig(
        level=_logging.INFO,
        stream=sys.stdout,
        force=True,
        format="%(asctime)s,%(msecs)d %(name)-2s %(levelname)-2s:\n  %(message)s",
        datefmt="%y%m%d-%H:%M:%S",
    )
    _logging.getLogger("nipype.workflow").setLevel(
        _logging.getLevelName(logging.workflow_level)
    )
    _logging.getLogger("nipype.utils").setLevel(
        _logging.getLevelName(logging.utils_level)
    )
    _logging.getLogger("nipype.interface").setLevel(
        _logging.getLevelName(logging.interface_level)
    )

    if logging.log_to_file:
        from logging.handlers import RotatingFileHandler as RFHandler

        _handler = RFHandler(
            str(Path(logging.log_directory) / "nipype.log"),
            maxBytes=logging.log_size,
            backupCount=logging.log_rotate,
        )
        _handler.setFormatter(_logging.Formatter(
            fmt="%(asctime)s,%(msecs)d %(name)-2s %(levelname)-2s:\n  %(message)s",
            datefmt="%y%m%d-%H:%M:%S",
        ))
        _logging.getLogger().addHandler(_handler)


update()
