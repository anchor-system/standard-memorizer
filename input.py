from typing import List


def get_roots_help_message(ground_truth) -> str:
    hints = []
    if isinstance(ground_truth[0], List):
        for chord in ground_truth:
            hints.append(str(chord[0]))
    else:
        hints.append(str(ground_truth[0]))
    return "roots: " + " ".join(hints)


def verify_guess(chords_guess_raw, ground_truth) -> bool:
    if chords_guess_raw.strip() in ["%", ""]:
        succeeded = ground_truth == []
    else:  # we are workign with a real chord
        if "-" in chords_guess_raw:
            chords_guess = []
            sub_chords_guess = chords_guess_raw.split("-")
            for chord_guess in sub_chords_guess:
                anchor_intervals = list(map(int, chord_guess.strip().split(" ")))
                chords_guess.append(anchor_intervals)
        else:
            anchor_intervals = list(map(int, chords_guess_raw.strip().split(" ")))
            chords_guess = anchor_intervals

        succeeded = chords_guess == ground_truth

    return succeeded
