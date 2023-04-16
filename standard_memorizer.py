import re
from pprint import pprint
from typing import List
import random

from input import get_roots_help_message, verify_guess
from user_experience import pause_then_clear_screen, clear_screen, temporarily_show_text
import user_experience

"""
terminology:

    bar delimiter:
        the | characters, which indicate the passing of one cycle defined by the time
        signature, usually called bar lines, we denote them by bar delimiters as not to confuse
        with lines of music which we use throughout the code

    structural strings:
        any string which is used to explain the structure of the song
        but not the harmonic information, these characters are:
    
            decorated bar delimiter:
                describe how to move within the music
                    :| || |1. |2. |A |B |C
            
"""

DECORATED_BAR_LINES = [":|", "||", "|1.", "|2.", "|A", "|B", "|C"]

file = open("submission.chords", "r")


def get_song_files():
    from os import listdir
    from os.path import isfile, join
    mypath = "text_standards"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return onlyfiles


def get_song_names():
    return list(map(
        lambda s: s.replace(".chords", "").replace("_", " ").lower(), get_song_files()
    ))


def get_song_name_to_file_name():
    song_files = get_song_files()
    song_name_to_file_name = {}
    for song_file in song_files:
        song_name = song_file.replace(".chords", "").replace("_", " ").lower()
        song_name_to_file_name[song_name] = song_file

    return song_name_to_file_name


def get_start_to_first_ending_of_song(text_standard_filename):
    music = open(text_standard_filename, "r")
    music = "".join(music.readlines())
    pattern = re.compile(r"(.*)\|1\.", re.S)
    match = re.search(pattern, music)[0]
    return match


def get_first_ending(text_standard_filename):
    music = open(text_standard_filename, "r")
    music = "".join(music.readlines())
    pattern = re.compile(r"\|1\..*")
    match = re.search(pattern, music)


def get_second_ending(text_standard_filename):
    music = open(text_standard_filename, "r")
    music = "".join(music.readlines())
    pattern = re.compile(r"\|2\..*")
    match = re.search(pattern, music)
    return match.group()


def get_anchor_interval_representation_of_second_repeat(text_standard_filename):
    start_to_first_ending = get_start_to_first_ending_of_song(text_standard_filename)
    anchor_intervals_from_start_to_first_ending = []
    lines_from_start_to_first_ending = start_to_first_ending.split("\n")
    for inner_music_line in lines_from_start_to_first_ending:
        chords: List[List[int]] = get_chords_from_music_line(inner_music_line)
        anchor_intervals_from_start_to_first_ending.append(chords)

    second_ending = get_second_ending(text_standard_filename)
    second_ending_chords = get_chords_from_music_line(second_ending)
    second_ending_repeat = anchor_intervals_from_start_to_first_ending
    second_ending_repeat[-1].extend(second_ending_chords)

    return second_ending_repeat


def get_anchor_interval_representation_of_song(text_standard_filename):
    """
    terminology:
        anchor interval representation of song:
            turns a song (a series of chord changes written down), into an array of arrays
            where each inner array represents a line in the music, in which each of the lines contains
            chords which a represented by an array of integers where these integers are anchor intervals.

    """
    music = open(text_standard_filename, "r")

    anchor_interval_song: List[List[List[int]]] = []

    for music_line in music:
        if not music_line.isspace():
            if "|2." in music_line.strip():
                anchor_interval_song.extend(
                    get_anchor_interval_representation_of_second_repeat(
                        text_standard_filename
                    )
                )
            else:
                chords: List[List[int]] = get_chords_from_music_line(music_line)
                anchor_interval_song.append(chords)

    return anchor_interval_song


def replace_decorated_bar_lines_with_regular_bar_lines(music_line: str) -> str:
    """

    description:
        given a regular line of music, this function replaces all decorated bar lines with
        regular bar lines, this is done so that ing can be done easily.
    """

    for decorated_bar_line in DECORATED_BAR_LINES:
        music_line = music_line.replace(decorated_bar_line, "|")

    return music_line


def get_chords_from_music_line(music_line: str) -> List[List[int]]:
    simplified_line = replace_decorated_bar_lines_with_regular_bar_lines(music_line)

    bar_line_content = list(map(lambda s: s.strip(), simplified_line.split("|")))
    bar_line_content = list(map(lambda s: s.split("/")[0] if "/" in s else s, bar_line_content))  # remove slash chords
    bar_line_content = list(filter(lambda s: s != "", bar_line_content))
    bar_line_content = list(map(lambda s: s.split("-") if "-" in s else s, bar_line_content))  # handle multi chords

    chords: List[List[int]] = []  # rows where each bar can have multiple chords

    for bar in bar_line_content:
        def convert_single_bar_to_anchor_intervals(bar: str) -> List[int]:
            split_bar = bar.split()
            content_no_extensions = list(filter(lambda s: s.isdigit(), split_bar))
            chord = list(map(int, content_no_extensions))
            return chord

        if isinstance(bar, List):
            sub_chords = []
            for sub_bar in bar:
                sub_chords.append(convert_single_bar_to_anchor_intervals(sub_bar))
            chords.append(sub_chords)
        else:
            assert (type(bar) is str)
            chords.append(convert_single_bar_to_anchor_intervals(bar))

    return chords


def select_song():
    choice = input("Would you like to pick a song or let me choose a random one? (p)ick/(r)andom: ")
    song_file = ""
    if choice == "p":
        requested_song = ""
        song_name_input = input("Ok, go ahead and choose a song: ")
        while requested_song == "":
            for song_name in get_song_names():
                if song_name_input in song_name:
                    requested_song = song_name
            if song_name_input == "":
                song_name_input = input("Sorry we don't have that song, try again: ")

        assert (requested_song != "" and requested_song in get_song_names())

        temporarily_show_text(f"Ok, we'll load up {requested_song}")

        song_file = get_song_name_to_file_name()[requested_song]

    elif choice == "r":
        random_song = random.choice(get_song_names())
        print(f"We randomly selected {random_song} for you.")
        song_file = get_song_name_to_file_name()[random_song]

    return song_file


def start_sequential_memorization_session(
        chord_selection=None
):
    if chord_selection is None:
        chord_selection = [True, True, True, True]  # root, third, fifth and seventh
        # make training where you go through all of the possibilities

    print("Welcome to the sequential memorizer!")

    song = get_anchor_interval_representation_of_song("text_standards/" + select_song())
    flattened_song = [chord for row in song for chord in row]

    index = 0
    errors = 0
    consecutive_errors = 0
    done = False
    first_chord = True

    while not done:
        bar = flattened_song[index]
        ground_truth = get_ground_truth(bar, chord_selection)

        raw_input = input(f"What is the {'first' if first_chord else 'next'} chord?: ")

        if raw_input.strip() == "h":
            print(get_roots_help_message(ground_truth))
        else:
            chords_guess_raw = raw_input

            got_it_right = verify_guess(chords_guess_raw, ground_truth)

            if got_it_right:
                print("success")
                index += 1
                consecutive_errors = 0
                first_chord = False
            else:
                print("incorrect")
                errors += 1
                consecutive_errors += 1

        if index == len(flattened_song):
            print("well done you've completed the song")
            return

    first_iteration = False


def get_ground_truth(bar, chord_selection):
    ground_truth = []

    def get_selection(chord):
        return [g for i, g in enumerate(chord) if chord_selection[i]]

    if bar != []:
        if isinstance(bar[0], List):
            temp = []
            for chord in bar:
                temp.append(get_selection(chord))
            ground_truth = temp
        else:
            chord = bar
            ground_truth = get_selection(chord)

    return ground_truth


def learn_new_song_session():

    song = get_anchor_interval_representation_of_song("text_standards/" + select_song())

    line_index = 0

    while line_index < len(song):

        memorized_line = False
        line = song[line_index]

        user_requested_skip = False

        user_experience.show_text_with_pause_after("let's memorize this line: " + str(line))

        while not memorized_line:

            LINE_ITERATIONS_FOR_MEMORIZATION = 4

            user_experience.show_text_with_pause_after( f"Once you get it right {LINE_ITERATIONS_FOR_MEMORIZATION} times in a row, we can move to the next line.", 3)

            user_experience.show_text_with_pause_after(f"Don't, forget if you can't remember the chord, type 'h' to "
                                                       f"get help.", 2)
            user_experience.show_text_with_pause_after(f"If you're confident you already know this line, type 's' to "
                                                       f"skip it", 2)

            bar_index = 0
            errors_made_in_line = 0
            consecutive_time_correct = 0

            while consecutive_time_correct < LINE_ITERATIONS_FOR_MEMORIZATION:

                while bar_index < 4:

                    bar = line[bar_index]
                    ground_truth = get_ground_truth(bar, [True, True, True, True])
                    raw_input = input(f"What is the {'first' if bar_index == 0 else 'next'} chord?: ")

                    if raw_input.strip() == "h":
                        print(get_roots_help_message(ground_truth))
                    elif raw_input.strip() == "s":
                        user_experience.show_text_with_pause_after_and_then_clear_screen(
                            "Looks like you already know this line, let's continue."
                        )
                        user_requested_skip = True
                        line_index += 1
                        break
                    else:
                        chords_guess_raw = raw_input
                        got_it_right = verify_guess(chords_guess_raw, ground_truth)

                        if got_it_right:
                            print("success")
                            bar_index += 1
                        else:
                            errors_made_in_line += 1
                            print("incorrect")

                if user_requested_skip:
                    break

                assert (bar_index == len(line))
                if errors_made_in_line > 0:
                    print(f"Good try, but you made {errors_made_in_line} errors")
                    consecutive_time_correct = 0
                else:
                    assert (errors_made_in_line == 0)
                    consecutive_time_correct += 1
                    user_experience.show_text_with_pause_after_and_then_clear_screen(
                        f"Well done, you got that line completely correct, do that {LINE_ITERATIONS_FOR_MEMORIZATION - consecutive_time_correct} more times.",
                        3
                    )


                if user_requested_skip:
                    break

                bar_index = 0
                errors_made_in_line = 0

            if user_requested_skip:
                break

            assert (consecutive_time_correct == LINE_ITERATIONS_FOR_MEMORIZATION)
            user_experience.show_text_with_pause_after("Nice, you've grasped that line well.")
            memorized_line = True
            just_memorized_first_line = line_index == 0

            line_index += 1

            if not just_memorized_first_line:

                print("Before we continue, let's run through the lines we know, starting from the first: ")

                recap_song = song[:line_index]

                line_to_num_errors = {}

                line_recap_index: int = 0
                while line_recap_index < len(recap_song):
                    recap_line = recap_song[line_recap_index]
                    recap_bar_index = 0
                    while recap_bar_index < len(recap_line):
                        recap_bar = recap_line[recap_bar_index]

                        ground_truth = get_ground_truth(recap_bar, [True, True, True, True])

                        raw_input = input("What is the next chord?: ")

                        chords_guess_raw = raw_input

                        got_it_right = verify_guess(chords_guess_raw, ground_truth)

                        if got_it_right:
                            print("success")
                            recap_bar_index += 1
                        else:
                            print("incorrect, try again")
                            if line_recap_index not in line_to_num_errors:
                                line_to_num_errors[line_recap_index] = 0
                            line_to_num_errors[line_recap_index] += 1

                    line_recap_index += 1

                made_any_errors = False
                feedback = ""

                for line, num_errors in line_to_num_errors.items():
                    if num_errors > 0:
                        made_any_errors = True
                        feedback += f"you made {num_errors} errors on line {line + 1} \n"

                if made_any_errors:
                    earliest_mistake_line = min(line_to_num_errors.keys())
                    print(feedback)
                    answer = input(
                        f"Your earliest mistake was on line {earliest_mistake_line + 1}, would you like to recommence memorization from that line?")
                    # TODO regex yes no on answer
                    if answer == "yes":
                        line_index = earliest_mistake_line
                        print("Ok, we'll start from that line now.")
                else:
                    user_experience.clear_screen_and_show_text("Well done, you know everything up to including this line we just practiced!")

            if user_requested_skip:
                continue


            # make a function which goes from lines 0 to n and do that.
            # get a sub song and just run the normal song thing.
            # if you can't get it, then we can figure out which line they have trouble on and then
            # ask if they want to work on it.



def query_user_for_practice_session_mode():
    user_experience.clear_screen()
    print("Hey there, let's memorize some songs.")
    answer = input("Do you want to (p)ractice a song you already know or (l)earn a new one?: ")
    if answer.strip() == "p":
        start_sequential_memorization_session()
    elif answer.strip() == "l":
        learn_new_song_session()


if __name__ == "__main__":
    query_user_for_practice_session_mode()
