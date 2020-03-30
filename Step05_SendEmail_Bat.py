import sys

sys.path.append(r"C:\Workspace\Personal\Secret")
from secrets import gmail
import tools_v2

if __name__ == "__main__":
    email = gmail["email"]
    password = gmail["password"]

scriptName = "Step05_SendEmail_Bat"
tools_v2.SendFinishedGmail(email, password, scriptName)
