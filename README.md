# Roblox Ids Checker.
Simple Roblox Id checker

This script working with this [repo](https://github.com/Roblox-Thot/DecalUploader)

# Installation requirements
```
pip install pandas
pip install pyarrow
pip install requests
```
# Configuration Settings
> [!TIP]\
> You need change values in script

```
TIME_SET = 1  # The set value of the check time
WEBHOOK_URL = ""  # Insert the webhook link from Discord
OUT_PATH = ""  # Specify your path to the out.csv file
```
# How it works

Ids have 3 states

```
Blocked
InReview
Completed
```

![image](https://github.com/MilkKoun/Roblox-Ids-Checker/assets/69580854/67c671ad-5529-481d-9610-3ecab2d0e2f2)

When state is Completed as a result, you receive a message from a bot on Discord.

![image](https://github.com/MilkKoun/Roblox-Ids-Checker/assets/69580854/a75b8f4e-210e-4618-98a3-97e116191a78)

And the script will automatically close.
