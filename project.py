"""
Entry point for the Tomba Maltego transforms.

    python3 project.py local <transform> <value> [properties]   run one transform (what Maltego calls)
    python3 project.py list                                     list the transforms
    python3 project.py runserver                                run them as a transform server
    python3 project.py build [options]                          write tomba_transforms.mtz and the CSV configs
"""

import argparse
import logging
import os
import sys

import transforms
from extensions import registry
from maltego_trx.handler import handle_run
from maltego_trx.registry import register_transform_classes
from maltego_trx.server import app as application

# maltego_trx.server enables DEBUG logging for everything on import, so the registry
# would log 'Ignoring File: "base"' (shared code, not a transform) on every run.
logging.getLogger("maltego_trx.registry").setLevel(logging.WARNING)

register_transform_classes(transforms)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def build(argv):
    parser = argparse.ArgumentParser(
        prog="project.py build",
        description="Write the Maltego import file (.mtz) and the transforms/settings CSV configs.",
    )
    parser.add_argument("--mtz", default=os.path.join(PROJECT_DIR, "tomba_transforms.mtz"),
                        help="output .mtz path (default: tomba_transforms.mtz in the project)")
    parser.add_argument("--working-dir", default=PROJECT_DIR,
                        help="directory Maltego runs the transforms from (default: this project)")
    parser.add_argument("--python", default=sys.executable or "python3",
                        help="Python command Maltego runs (default: the Python running this build)")
    parser.add_argument("--version", default=None, help="override the version in extensions.py")
    parser.add_argument("--no-debug", action="store_true",
                        help="don't show transform output in Maltego's output window")
    parser.add_argument("--no-csv", action="store_true", help="only write the .mtz")
    args = parser.parse_args(argv)

    if args.version:
        registry.version = args.version.lstrip("v")

    if not args.no_csv:
        registry.write_transforms_config(
            config_path=os.path.join(PROJECT_DIR, "transforms.csv"), include_output_entities=True)
        registry.write_settings_config(config_path=os.path.join(PROJECT_DIR, "settings.csv"))

    registry.write_local_mtz(
        mtz_path=args.mtz,
        working_dir=args.working_dir,
        command=args.python,
        params="project.py",
        debug=not args.no_debug,
    )

    print(f"Wrote {args.mtz} with {len(registry.transform_metas)} transforms (version {registry.version})")
    print(f"  working directory: {os.path.abspath(args.working_dir)}")
    print(f"  command:           {args.python} project.py local <transform>")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "build":
        build(sys.argv[2:])
    else:
        handle_run(__name__, sys.argv, application)
