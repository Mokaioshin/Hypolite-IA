from brain import ask_hipolite
from memory import init_memory


def main():

    init_memory()

    print("================================")
    print("        HIPOLITE V0.1")
    print("================================")
    print("Écris 'quit' pour quitter.\n")

    while True:

        user_message = input("Toi > ")

        if user_message.lower() in ["quit", "exit", "q"]:
            print("Hipolite > Bon, enfin. À plus.")
            break

        try:
            answer = ask_hipolite(user_message)
            print(f"Hipolite > {answer}\n")

        except Exception as error:
            print(f"[ERREUR] {error}")


if __name__ == "__main__":
    main()