import pandas as pd
import uuid




def main():
    word ="Property Type (L/O)"

    new_word= word.replace(" ", "_").replace("/", "_").replace('-', '_').replace('(','_').replace(')','_')

    print(word)
    print(new_word)
if __name__ == "__main__":
    main()

