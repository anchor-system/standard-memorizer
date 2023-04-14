from typing import List

from input import get_roots_help_message, verify_guess

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
    """
    """

    simplified_line = replace_decorated_bar_lines_with_regular_bar_lines(music_line)

    bar_line_content = list(map(lambda s: s.strip(), simplified_line.split("|")))
    bar_line_content = list(filter(lambda s: s != "", bar_line_content))
    bar_line_content = list(map(lambda s: s.split("-") if "-" in s else s, bar_line_content))

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


def start_sequential_memorization_session(
        chord_selection=None
):
    if chord_selection is None:
        chord_selection = [True, False, True, False]  # root, third, fifth and seventh
        # make training where you go through all of the possibilities

    print("Welcome to the sequential memorizer!")
    print("Would you like to pick a song or let me choose a random one? (p)ick/(r)andom")

    song = get_anchor_interval_representation_of_song("text_standards/THERE_WILL_NEVER_BE_ANOTHER_YOU.chords")
    flattened_song = [chord for row in song for chord in row]

    index = 0
    errors = 0
    consecutive_errors = 0
    done = False

    while not done:
        bar = flattened_song[index]
        ground_truth = get_ground_truth(bar, chord_selection)

        raw_input = input("What is the next chord?: ")

        if raw_input.strip() == "h":
            print(get_roots_help_message(ground_truth))
        else:
            chords_guess_raw = raw_input

            got_it_right = verify_guess(chords_guess_raw, ground_truth)

            if got_it_right:
                print("success")
                index += 1
                consecutive_errors = 0
            else:
                print("incorrect")
                errors += 1
                consecutive_errors += 1

        if index == len(flattened_song):
            print("well done you've completed the song")
            return


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
    print("Hi, let's learn a new song!")

    song = get_anchor_interval_representation_of_song("text_standards/THERE_WILL_NEVER_BE_ANOTHER_YOU.chords")

    line_index = 0

    while line_index < len(song):

        memorized_line = False
        line = song[line_index]
        print("let's memorize this line: " + str(line))

        while not memorized_line:

            LINE_ITERATIONS_FOR_MEMORIZATION = 1

            print(f"Once you get it right {LINE_ITERATIONS_FOR_MEMORIZATION} times in a row, we can move to the next line.")

            bar_index = 0
            errors_made_in_line = 0
            consecutive_time_correct = 0

            while consecutive_time_correct < LINE_ITERATIONS_FOR_MEMORIZATION:

                while bar_index < 4:

                    bar = line[bar_index]
                    ground_truth = get_ground_truth(bar, [True, True, True, True])
                    raw_input = input("What is the next chord?: ")

                    chords_guess_raw = raw_input

                    got_it_right = verify_guess(chords_guess_raw, ground_truth)

                    if got_it_right:
                        print("success")
                        bar_index += 1
                    else:
                        errors_made_in_line += 1
                        print("incorrect")

                assert (bar_index == len(line))
                if errors_made_in_line > 0:
                    print(f"Good try, but you made {errors_made_in_line} errors")
                    consecutive_time_correct = 0
                else:
                    assert (errors_made_in_line == 0)
                    consecutive_time_correct += 1
                    print(
                        f"Well done, you got that line completely correct, do that {4 - consecutive_time_correct} more times.")

                bar_index = 0
                errors_made_in_line = 0

            assert (consecutive_time_correct == LINE_ITERATIONS_FOR_MEMORIZATION)
            print("Nice, you've got that line, let's try a new line.")
            memorized_line = True
            line_index += 1

            print("Before we continue, let's run through the lines we know, starting from the first: ")

            recap_song = song[:line_index]

            line_to_num_errors = {}

            line_recap_index: int = 0
            while line_recap_index < len(recap_song):
                recap_line = recap_song[line_recap_index]
                #bar recap_
                for recap_bar in recap_line:
                    ground_truth = get_ground_truth(recap_bar, [True, True, True, True])

                    raw_input = input("What is the next chord?: ")

                    chords_guess_raw = raw_input

                    got_it_right = verify_guess(chords_guess_raw, ground_truth)

                    if got_it_right:
                        print("success")
                        line_recap_index += 1
                    else:
                        print("incorrect")
                        if line_recap_index not in line_to_num_errors:
                            line_to_num_errors[line_recap_index] = 0
                        line_to_num_errors[line_recap_index] += 1

            made_any_errors = False
            feedback = ""


            for line, num_errors in line_to_num_errors.items():
                if num_errors > 0:
                    made_any_errors = True
                    feedback += f"you made {num_errors} on line {line} \n"


            if made_any_errors:
                earliest_mistake_line = min(line_to_num_errors.keys())
                print(feedback)
                answer = input(f"Your earliest mistake was on line {earliest_mistake_line}, would you like to recommence memorization from that line?")
                # TODO regex yes no on answer
                if answer == "yes":
                    line_index = earliest_mistake_line
                    print("Ok, we'll start from that line now.")
            else:
                print("Well done, you know everything up to including this line we just practiced!")


            # make a function which goes from lines 0 to n and do that.
            # get a sub song and just run the normal song thing.
            # if you can't get it, then we can figure out which line they have trouble on and then
            # ask if they want to work on it.




if __name__ == "__main__":
    start_sequential_memorization_session()
    #learn_new_song_session()
