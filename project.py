import random, os, sys
from typing import Dict, List, Tuple

TOTAL_DISTANCE = 850
MAX_HEALTH = 100
DAY_RESOURCE_DECAY = {"food": 5, "water": 8, "health": 5}
KNAPSACK_CAPACITY = 500

# This is the main class for the player
class Player:
    def __init__(self, food: int, water: int, spare: int, opal: int):
        self.health = MAX_HEALTH
        self.food = food
        self.water = water
        self.spare = spare
        self.opal = opal
        self.distance_left = TOTAL_DISTANCE
        self.day = 1
        self.cause_of_death = ""

    # ---------------------------------- player status ----------------------------------
    def is_alive(self) -> bool:
        return self.health > 0

    def status_report(self):
        print(f"\n-------------------------------- Day {self.day} --------------------------------")
        print(
            f"Health: {self.health:3d} | Food: {self.food:3d} | Water: {self.water:3d} | "
            f"Spare parts: {self.spare:3d} | opal: {self.opal:3d}"
        )
        print(f"Distance left: {self.distance_left} km")
        print("-----------------------------------------------------------------------\n")

    # ---------------------------------- action choices ---------------------------------
    def travel_day(self):
        km = random.randint(20, 50)
        self.distance_left = max(0, self.distance_left - km)
        self.consume(DAY_RESOURCE_DECAY)
        self.day += 1
        return km

    def rest_day(self):
        self.health = min(MAX_HEALTH, self.health + 10)
        self.consume({"food": 3, "water": 4})
        self.day += 1

    # ---------------------------------- handle resources -------------------------------
    def consume(self, decay: Dict[str, int]):
        for res, amt in decay.items():
            setattr(self, res, max(0, getattr(self, res) - amt))
        # If travel-day health depletion reaches zero, mark exhaustion death
        if self.health == 0 and self.cause_of_death == "":
            self.die("exhaustion")
        self.check_starve_thirst()

    def check_starve_thirst(self):
        if self.food == 0:
            self.die("starvation")
        if self.water == 0 and self.is_alive():
            self.die("dehydration")

    def die(self, cause: str):
        if self.is_alive():
            self.health = 0
            self.cause_of_death = cause


# --------------------------- all events -------------------------------
EVENTS: List[Dict] = [
    {"name": "Snake Bite", "message": "A desert taipan snake sinks its fangs into your leg!", "effect": {"health": -25}, "prob": 0.10},
    {"name": "Dust Storm", "message": "A huge storm blows up sand and dust, blowing away a few of your supplies.", "effect": {"water": -12, "food": -6}, "prob": 0.12},
    {"name": "Bushfire", "message": "Flames close in, forcing you to detour.", "effect": {"health": -10, "distance": +30}, "prob": 0.05},
    {"name": "Caravan Breakdown", "message": "Your caravan axle snaps on a rocky outcrop!", "effect": {}, "prob": 0.08},
    {"name": "Travelling Merchant", "message": "A travelling merchant appears in your path, offering you a trade.", "effect": {}, "prob": 0.15},
    {"name": "Found Resources", "message": "You discover something useful along the trail.", "effect": {}, "prob": 0.15},
]

RESOURCE_NAMES = {
    "food": "food",
    "water": "water",
    "spare": "spare parts",
    "opal": "opal gems",
}

HELP_TEXT = (
    "\n================= GAME INFORMATION ========================\n"
    "GOAL: Travel 1000 km across the outback without dying.\n\n"
    "RESOURCES\n"
    "  Food     : consumed daily (5 when travelling, 3 when resting).\n"
    "  Water    : consumed daily (8 when travelling, 4 when resting).\n"
    "  Spare parts : used to fix caravan breakdowns and they are tradeable.\n"
    "  opal     : used in trades; no daily decay.\n"
    "  Health   : decays by 5 each travel day, lost from events; rest restores 10.\n\n"
    "ACTIONS\n"
    "  Travel (T)  : move 20 to 50 km, consume daily food & water, random event possible.\n"
    "  Rest (R)    : +10 health, lesser food & water loss.\n"
    "  Save (S)    : save game progress.\n"
    "  Quit (Q)    : save and exit.\n"
    "  Info/Help (I/H) : show this help screen.\n\n"
    "EVENTS\n"
    "  Snake Bite / Bushfire  : lose health.\n"
    "  Dust Storm             : lose food & water.\n"
    "  Caravan Breakdown      : costs 1 to 3 spare parts or death.\n"
    "  Travelling Merchant    : random trades involving any resource.\n"
    "  Found Resources        : randomly gain supplies or health.\n"
    "===============================================================\n"
)


def choose_event():
    r = random.random()
    cum = 0.0
    for ev in EVENTS:
        cum += ev["prob"]
        if r < cum:
            return ev
    return None


def handle_event(player: "Player", event: Dict):
    print(f"\n!! {event['name']} !!")
    print(event["message"])
    for attr, delta in event.get("effect", {}).items():
        if attr == "distance":
            player.distance_left = max(0, player.distance_left + delta)
        else:
            setattr(player, attr, max(0, getattr(player, attr) + delta))
    if event["name"] == "Travelling Merchant":
        trade(player)
    elif event["name"] == "Caravan Breakdown":
        breakdown(player)
    elif event["name"] == "Found Resources":
        found_resources(player)
    player.check_starve_thirst()








def breakdown(player: "Player"):
    needed = random.randint(1, 3)
    print(f"You need {needed} spare part(s) to repair the caravan.")
    if player.spare >= needed:
        player.spare -= needed
        print("You repair the caravan and continue.")
    else:
        print("Not enough spare parts: you are stranded and perish.")
        player.die("caravan breakdown")

def trade(player: "Player"):
    resources = ["food", "water", "spare", "opal"]
    give, receive = random.sample(resources, 2)
    give_amt = random.randint(10, 50) if give == "opal" else (
        random.randint(2, 10) if give == "spare" else random.randint(5, 20)
    )
    receive_amt = int(round(give_amt * random.uniform(1.2, 1.6)))

    print(f"He wants to sell you {receive_amt} {RESOURCE_NAMES[receive]} in exchange for {give_amt} {RESOURCE_NAMES[give]}. Accept? (y/n)")
    if not input("> ").strip().lower().startswith("y"):
        print("You decline the offer and move on.")
        return
    if getattr(player, give) < give_amt:
        print(f"You don’t have enough {RESOURCE_NAMES[give]}.")
        return
    setattr(player, give, getattr(player, give) - give_amt)
    setattr(player, receive, getattr(player, receive) + receive_amt)
    print("Trade complete.")
    player.check_starve_thirst()


def found_resources(player: "Player"):
    options = [
        ("an opal mine", "opal", random.randint(10, 30)),
        ("a bag of canned food", "food", random.randint(15, 40)),
        ("a freshwater well", "water", random.randint(20, 40)),
        ("a crate of beer", "health", random.randint(10, 30)),
        ("a broken-down caravan stocked with parts", "spare", random.randint(1, 5)),
    ]
    desc, attr, amt = random.choice(options)
    if attr == "health":
        player.health = min(MAX_HEALTH, player.health + amt)
    else:
        setattr(player, attr, getattr(player, attr) + amt)
    label = RESOURCE_NAMES.get(attr, "health")
    print(f"You found {desc}! +{amt} {label}.")









def plan_knapsack():
    print(f"You have a knapsack that can carry {KNAPSACK_CAPACITY} total units of supplies.")
    print("Resources available: Food, Water, Spare parts, opal gems.\n")
    while True:
        try:
            food = int(input("Enter units of FOOD to pack: "))
            water = int(input("Enter units of WATER to pack: "))
            spare = int(input("Enter number of SPARE PARTS to pack: "))
            opal = int(input("Enter number of OPAL GEMS to pack: "))
        except ValueError:
            print("Please enter whole numbers only.\n")
            continue
        if min(food, water, spare, opal) < 0:
            print("Values cannot be negative.\n")
            continue
        if food + water + spare + opal > KNAPSACK_CAPACITY:
            print("That exceeds your knapsack capacity. Try again.\n")
            continue
        return food, water, spare, opal


def save_game(p: "Player", fn: str):
    with open(fn, "w") as fp:
        fp.write(f"{p.health},{p.food},{p.water},{p.spare},{p.opal},{p.distance_left},{p.day}\n")
    print("[Game saved]")


def load_game(fn: str):
    with open(fn) as fp:
        h, f, w, s, m, d, day = map(int, fp.readline().strip().split(","))
    p = Player(f, w, s, m)
    p.health, p.distance_left, p.day = h, d, day
    p.check_starve_thirst()
    print("[Game loaded]")
    return p






# -------------------------------- main game loop ----------------------------------

def prompt_username():
    while True:
        u = input("Enter your adventurer name: ").strip()
        if u and u.isalnum():
            return u
        print("Name must be non-empty and alphanumeric (no spaces). Try again.")


def main():
    print("================= Aussie Trail =================")
    username = prompt_username()
    save_file = f"{username}.txt"

    if os.path.exists(save_file):
        player = load_game(save_file)
    else:
        print(f"New adventurer detected – welcome, {username}!")
        food, water, spare, opal = plan_knapsack()
        player = Player(food, water, spare, opal)
        save_game(player, save_file)

    while player.is_alive() and player.distance_left > 0:
        player.status_report()
        print("Choose action: [T]ravel, [R]est, [S]ave, [I]nfo, [Q]uit")
        choice = input("> ").strip().lower()

        # Player Actions
        if choice == "t":
            km = player.travel_day()
            print(f"You travelled {km} km today.")
            ev = choose_event()
            if ev:
                handle_event(player, ev)
        elif choice == "r":
            player.rest_day()
            print("You took a rest day.")
        elif choice == "s":
            save_game(player, save_file)
            continue
        elif choice in {"h", "i"}:
            print(HELP_TEXT)
            continue
        elif choice == "q":
            save_game(player, save_file)
            print("Progress saved. Goodbye.")
            sys.exit()
        else:
            print("Invalid choice.")
            continue



        if player.distance_left == 0:
            print("*" * 61)
            print("-------------------------------------------------------------")
            print("🏁 Congratulations!!! You reached the end of the trail alive!")
            print("-------------------------------------------------------------")
            print("*" * 61)
            break
        if not player.is_alive():
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("💀 You died of " + (player.cause_of_death or "your injuries") + ".")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            break

    save_game(player, save_file)


if __name__ == "__main__":
    main()
