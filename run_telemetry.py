from src.logging import setup as setup_logging
from src.telemetry import run as run_telemetry

from src.telemetry.telemetry_command import Command


args = Command().parse_args()
setup_logging(args.log_level)
run_telemetry(None, None, {}, args.sheet_name, args.ip)
