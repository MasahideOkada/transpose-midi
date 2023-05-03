import os, argparse
from pathlib import Path

from mido import MidiFile
from tqdm import tqdm

LOWEST_NOTE = 0
HIGHEST_NOTE = 127

def remove_ext(filepath: str) -> str:
    """
    removes file extension\n
    if no extension is found, returns the input `filepath`
    """

    dir, name = os.path.split(filepath)
    name_split = name.split(".")

    if len(name_split) == 1:
        return filepath
    
    name_without_ext = ".".join(name_split[:-1])
    return os.path.join(dir, name_without_ext)

def transpose_note(input_note: int, transposition: int) -> int:
    """
    transposes a midi note by the value `transposition`\n
    for simplicity, transposing beyond octave is not allowed
    """
    assert type(input_note) is int, "type of `input_note` must be `int`"
    assert type(transposition) is int, "type of `transposition` must be `int`"
    assert input_note >= LOWEST_NOTE and input_note <= HIGHEST_NOTE,\
        f"note value must be between {LOWEST_NOTE} and {HIGHEST_NOTE}"
    assert transposition >= -12 and transposition <= 12,\
        "the value for transposition must be between -12 and 12"

    transposed = input_note + transposition
    if transposed < LOWEST_NOTE:
        transposed += 12
    if transposed > HIGHEST_NOTE:
        transposed -= 12
    
    return transposed

def transpose_midi(midi_path: str, transposition: int) -> bool:
    """
    transposes all notes in a midi file by the value `transposition`\n
    returns `True` if the process is done successfully, `False` otherwise
    """
    
    is_ok = True
    try:
        midi = MidiFile(midi_path)
        for track in midi.tracks:
            for message in track:
                if message.type in {"note_on", "note_off"}:
                    message.note = transpose_note(message.note, transposition)

        basepath = remove_ext(midi_path)
        midi.save(f"{basepath}_tp{transposition}.mid")
    except:
        is_ok = False

    return is_ok

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transpose midi files to other 11 keys")
    parser.add_argument(
        "directory",
        metavar="MIDI_DIRECTORY",
        type=str,
        help="directory of midi files to transpose, midi files will be searched for recursively"
    )
    args = parser.parse_args()
    
    transposition_values = [i for i in range(-5, 7) if i != 0]

    dir = args.directory
    dir_path = Path(dir)
    midi_files = list(dir_path.rglob("*.mid"))
    error_files = []
    for midi_path in tqdm(midi_files):
        for transposition in transposition_values:
            ok = transpose_midi(str(midi_path), transposition)
            if not ok:
                error_files.append(str(midi_path))

    if len(error_files) > 0:
        print("error occured when transposing midi files below")
        for ef in error_files:
            print(ef)
