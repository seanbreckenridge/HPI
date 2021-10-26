import sys

from textgenrnn import textgenrnn
import IPython

loc = "/tmp/discord.txt"


def main():
    epochs: int
    if len(sys.argv) > 1:
        epochs = int(sys.argv[1])
    else:
        epochs = 1
    print(f"Running with {epochs} epochs...")
    gen = textgenrnn()
    gen.train_from_file(str(loc), num_epochs=epochs)
    IPython.embed()


if __name__ == "__main__":
    main()
