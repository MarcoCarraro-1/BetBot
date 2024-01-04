# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import (
    List,
    Text,
    Optional,
    Dict,
    Any,
    TYPE_CHECKING,
    Tuple,
    Set,
    cast,
)


from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random
import json
import random
import word2number
from word2number import w2n


class ActionAuthUser(Action):

    def name(self) -> Text:
        return "action_auth_user"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Open our database
        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        username_entity = tracker.get_slot('username')
        already_registred = False

        for user in data.get("user", []):
            if user["username"] == username_entity:
                already_registred = True

        if already_registred:
            dispatcher.utter_message(text="Successfully logged in! Welcome back "+username_entity+"!")
        else:
            dispatcher.utter_message(text="It seems that you're not registred yet. "+username_entity+"!")

        return [SlotSet("authenticated", already_registred)]


# This custom action allow a user to register
class ActionRegUser(Action):
    def name(self) -> Text:
        return "action_reg_user"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract entities from the tracker
        user_entity = tracker.get_slot("username")

        # Debug prints
        print("Username:", user_entity)

        # Create a new user
        
        new_user = {
            "name": "Nome",
            "surname": "Cognome",
            "fiscal_code": "FSCLCD",
            "username": user_entity,
            "password": "password",
            "balance": 0,
            "weekly_recap": 0,
            "monthly_recap": 0,
            "favorite_payment_method": "PayPal"
        }

        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        # Add a new user to the "user" entity
        data["user"].append(new_user)

        # Save the updated data back to database.json
        with open('./data/data.json', 'w') as file:
            json.dump(data, file, indent=2)

        dispatcher.utter_message(f"Welcome {user_entity}, you're now part of our family!")

        return [SlotSet("authenticated", True),
                SlotSet("username", user_entity)]


class ActionLogoutUser(Action):

    def name(self) -> Text:
        return "action_logout_user"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Goodbye! You successfully logged out.")
        return [SlotSet("authenticated", False)]


class ActionRefreshBalance(Action):

    def name(self) -> Text:
        return "action_refresh_balance"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        with open('./data/data.json', 'r') as file:
            data = json.load(file)
        username_entity = tracker.get_slot("username")

        try:
            reload_amount = float(tracker.get_slot("reload_amount"))
            dispatcher.utter_message(text="Your reload was successful!")
            for user in data.get("user", []):
                if user["username"] == username_entity:
                    new_balance = user["balance"] + reload_amount
                    user["balance"] = new_balance
                    # Write back to the JSON file
                    with open('your_file.json', 'w') as file:
                        json.dump(data, file, indent=2)
                    dispatcher.utter_message(text=f"Your new balance is {new_balance}€.")
                    break
        except:
            dispatcher.utter_message(text="Something goes wrong, no transactions have been made on your account.")
            dispatcher.utter_message(text="Try again by entering the sum in numbers")
        return[]


        
class ActionCheckAmount(Action):

    def name(self) -> Text:
        return "action_check_amount"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        reload_amount = tracker.get_slot("reload_amount")

        try:
            if reload_amount.isdigit():
                return[SlotSet("valid_amount", True)]
            else:
                try:
                    reload_amount = w2n.word_to_num(reload_amount)
                    dispatcher.utter_message("We inside the try")
                    return[SlotSet("valid_amount", True),
                        SlotSet("reload_amount", round(float(reload_amount),2))]
                except:
                    return[SlotSet("valid_amount", False)]
        except:
            return[SlotSet("valid_amount", False)]


# This custom action shows us all the events about a specified sport
class ActionFetchData(Action):
    def name(self) -> Text:
        return "action_fetch_events"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Open our database
        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        # Extract entities from the tracker
        sport_entity = tracker.get_slot("sport")

        # Debug prints
        print("Sport Entity:", sport_entity)

        # Fetch selected matches
        selected_matches = []
        for selected_match in data.get("sport_event", []):
            if selected_match["sport"] == sport_entity:
                selected_matches.append(selected_match)
        if selected_matches:
            dispatcher.utter_message(f"Matches {sport_entity} are the following:")
            for selected_match in selected_matches:
                dispatcher.utter_message(f"{selected_match['name']} on date: {selected_match['date']}")
        else:
            dispatcher.utter_message("No {sport_entity} matches found!")

        return []


# This custom action allow us to popolate an array slot [so we can manage variable number of bets]
class BetAction(Action):
    def name(self) -> Text:
        return "action_bet"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Extract bet information from user input
        event_entity = tracker.get_slot('event')
        outcome_entity = tracker.get_slot('outcome')

        # Retrieve the current list of bets from the user's slot
        # First time will be empty
        current_bets = tracker.get_slot("bets") or []
        exit_status = 'ok'

        for bet in current_bets:
            if event_entity == bet['event']:
                exit_status = []
                break
        
        if len(current_bets) >= 5:
            exit_status = 'too many'
        
        if exit_status == []:
            print('The user already bet on this game... It is not possible to bet twice')
            dispatcher.utter_message(f"You already placed a bet on {event_entity}. It's not possible to bet twice on the same event.")
        elif exit_status == 'too many':
            print('The user reached the maximum amount of events')
            dispatcher.utter_message(f"It isn't possible to bet on more than 5 events in the same ticket!")
            exit_status = []
        else:
            # Append the new bet to the list
            current_bets.append({"event": event_entity, "outcome": outcome_entity})

            # Debug message
            print(f"Bet {outcome_entity} on {event_entity} added successfully!")
            exit_status = [SlotSet("bets", current_bets)]

        # Set the updated list of bets in the slot
        return exit_status


# This custom action is similar to 'ActionFetchData' but for odds
class ActionFetchOdds(Action):
    def name(self) -> Text:
        return "action_fetch_odds"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Read our db
        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        # Extract entities from the tracker
        event_entity = tracker.get_slot("event")

        # Debug prints
        print("Event Entity:", event_entity)


        # Giving the odds of an event to the user

        selected_event = next((event for event in data.get("sport_event", []) if event["name"] == event_entity), None)
        if selected_event:
            dispatcher.utter_message(f"The odds for {event_entity} are the following:")
            if selected_event['sport'] == 'football':
                dispatcher.utter_message(f"Home: {selected_event['home']}\nDraw: {selected_event['draw']}\nAway: {selected_event['away']}")
            #elif selected_event['sport'] == 'tennis':
            else:
                dispatcher.utter_message(f"Home: {selected_event['home']}\nAway: {selected_event['away']}")
        else:
            dispatcher.utter_message("Event not found")

        return []


# This custom action allow us to place the bet [both single and multiple]
# Previous version was split in two: one for single play and one for multiple play
class ActionSetBet(Action):
    def name(self) -> Text:
        return "action_set_play"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract entities from the tracker
        user_entity = tracker.get_slot("username")
        bets_entity = tracker.get_slot("bets")
        amount_entity = tracker.get_slot("bet_amount")

        # Debug prints
        print("Username:", user_entity)
        print("His picks:", bets_entity)
        print(f"He bets {amount_entity} euros")

        winning_status = False
        
        play_type = 'single'
        if len(bets_entity) > 1:
            play_type = 'multiple'

        selected_events = []
        selected_outcomes = []
        for element in bets_entity:
            selected_events.append(element['event'])
            selected_outcomes.append(element['outcome'])

        ticket_number =  str(random.randint(100000, 999999))
        # TO-DO check if the random number created already exists, if so regenerate it

        # Create a new ticket
        new_ticket = {
            "number": ticket_number,
            "username": user_entity,
            "type": play_type,
            "events": selected_events,
            "outcomes": selected_outcomes,
            "bet_amount": amount_entity,
            "potential_win": 16.5,
            "win": winning_status
        }

        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        # Add a new ticket to the "ticket" entity
        data["ticket"].append(new_ticket)

        # Prepare the message with the ticket recap
        message = ""
        for i in range(len(selected_events)):
            message += f"{i+1}. {selected_events[i]}  [{selected_outcomes[i]}]\n"

        print('the message is: ', message)
        # Save the updated data back to database.json
        with open('./data/data.json', 'w') as file:
            json.dump(data, file, indent=2)

        dispatcher.utter_message(f"Bet ticket number {new_ticket['number']} successfully placed!\n"+
                                 f"Ticket recap:\n{message}")

        return [SlotSet("bets", [])]


# This custom action is used for checking if a bet is won by the user
class ActionCheckTicket(Action):
    def name(self) -> Text:
        return "action_check_ticket"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Read our db
        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        try:
            ticket_id_entity = int(tracker.get_slot("ticket_id"))
        except (ValueError, TypeError):
            dispatcher.utter_message(f"The ticket id you provided is incorrect (has to be a number)")
            ticket_id_entity = None  # You can set a default value or handle it accordingly
            return []

        # Debug prints
        print("Ticket id is ", ticket_id_entity)

        #ticket_id_entity = int(ticket_id_entity)

        # Checking if a ticket is winner or not
        selected_ticket = next((ticket for ticket in data.get("ticket", []) if ticket["number"] == ticket_id_entity), None)
        if selected_ticket:
            if selected_ticket['win'] == True:
                dispatcher.utter_message(f"Congratulations! The ticket number {ticket_id_entity} made you win {selected_ticket['potential_win']}")
            else:
                dispatcher.utter_message(f"I'm sorry, you did not win this time. (you lost {selected_ticket['bet_amount']})")
        else:
            dispatcher.utter_message("Ticket not found")

        return []
    
class ActionActivateReloadContext(Action):

    def name(self) -> Text:
        return "action_activate_reload_context"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        reload_context = tracker.get_slot("reload_context")

        return[SlotSet("reload_context", True)]
    
class ActionDeactivateReloadContext(Action):

    def name(self) -> Text:
        return "action_deactivate_reload_context"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        reload_context = tracker.get_slot("reload_context")

        return[SlotSet("reload_context", False)]
    
class ActionSetBetInProgress(Action):

    def name(self) -> Text:
        return "action_set_bet_in_progress"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return[SlotSet("bet_in_progress", True)]
    
class ActionRemoveBetInProgress(Action):

    def name(self) -> Text:
        return "action_remove_bet_in_progress"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return[SlotSet("bet_in_progress", False)]