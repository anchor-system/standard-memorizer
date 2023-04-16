import time
import os

DEFAULT_PAUSE_TIME = 1
DEFAULT_TIME_UNTIL_FULLY_SHOWN_SECONDS = 1


def show_text_character_by_character(
        text_to_show: str,
        time_until_fully_shown_seconds: int = DEFAULT_TIME_UNTIL_FULLY_SHOWN_SECONDS
) -> None:

    # this doesn't work, so we'll just print for now
    # duration_for_each_char: float = time_until_fully_shown_seconds / len(text_to_show)
    # for char in text_to_show:
    #     print(char, end="")
    #     time.sleep(duration_for_each_char)

    print(text_to_show)


def clear_screen_and_show_text(text_to_show):
    clear_screen()
    show_text_character_by_character(text_to_show)


def show_text_with_pause_after_and_then_clear_screen(text_to_show: str, pause_time_seconds=DEFAULT_PAUSE_TIME):
    show_text_with_pause_after(text_to_show, pause_time_seconds)
    clear_screen()


def show_text_with_pause_after(text_to_show: str, pause_time_seconds=DEFAULT_PAUSE_TIME):
    show_text_character_by_character(text_to_show)
    time.sleep(pause_time_seconds)


def temporarily_show_text(text_to_show: str, duration_seconds=2) -> None:
    clear_screen_and_show_text(text_to_show)
    pause_then_clear_screen(duration_seconds)


def pause_then_clear_screen(pause_time_seconds=DEFAULT_PAUSE_TIME):
    time.sleep(pause_time_seconds)
    clear_screen()


def clear_screen():
    os.system('cls||clear')
