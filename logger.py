from datetime import datetime


def info(*text):

    print(

        f"[{datetime.now().strftime('%H:%M:%S')}]",

        *text

    )


def ok(*text):

    print(

        f"[{datetime.now().strftime('%H:%M:%S')}]",

        "[OK]",

        *text

    )


def warn(*text):

    print(

        f"[{datetime.now().strftime('%H:%M:%S')}]",

        "[WARN]",

        *text

    )


def error(*text):

    print(

        f"[{datetime.now().strftime('%H:%M:%S')}]",

        "[ERROR]",

        *text

    )