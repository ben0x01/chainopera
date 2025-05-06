from loguru import logger
from datetime import datetime
import colorama
from colorama import Style
from typing import Optional

colorama.init(autoreset=True)

class CustomLogger:
    def __init__(self, id: int):
        self.id = id
        self.log_settings = {
            "success": {"symbol": "✅", "color": "#26FF5C"},
            "info": {"symbol": "🤖", "color": "#3C9DFF"},
            "debug": {"symbol": "✨", "color": "#00F7FF"},
            "warning": {"symbol": "⚠️", "color": "#FFC926"},
            "error": {"symbol": "×", "color": "#F55256"}
        }


        logger.remove()
        logger.add(lambda msg: print(self._format_message(msg.record["level"].name.lower(), msg)), format="{message}")

    def _hex_to_ansi(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        return f"\x1b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"

    def _format_message(self, level: str, message: str) -> str:
        symbol = self.log_settings[level]["symbol"]
        color = self._hex_to_ansi(self.log_settings[level]["color"])
        reset = Style.RESET_ALL
        return f"{color}{symbol} {self._log_prefix()} {message}{reset}"

    def _log_prefix(self) -> str:
        return f"{datetime.now().strftime('%H:%M:%S')} [ID: {self.id}] "

    def get_logger(self):
        return logger
