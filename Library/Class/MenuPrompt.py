class MenuPrompt:
    def __init__(self):
        self.choices = []
        return

    def addChoice(self, name:str, description:str):
        self.choices.append([name, description])
        return

    def prompt(self):

        # build prompt list
        chIdx = 1
        promptMenu = []
        prompt = ""
        for ch in self.choices:
            promptType = ch[0]
            promptText = f"{chIdx}. {ch[1]}"
            promptMenu.append(promptType)

            prompt = f"{prompt}\n{promptText}\n"
            chIdx += 1

        prompt = prompt.lstrip("\n")

        # display prompts
        sep = "=" * 50
        print(sep)
        print("SELECT A DESIRED FUNCTION:")
        print(sep)

        print(prompt)

        userChoice = 99
        while int(userChoice) > len(promptMenu) or int(userChoice) == 0:
            userChoice = input("Enter choice number: ")
            if not userChoice.isnumeric():
                print("Invalid choice")
                userChoice = 99
            elif int(userChoice) > len(promptMenu) or int(userChoice) == 0:
                print("Invalid choice")

        # parse choices
        choiceType = promptMenu[int(userChoice) - 1]

        return choiceType