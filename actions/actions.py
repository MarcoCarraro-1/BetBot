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
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

class ActionAuthUser(Action):

    def name(self) -> Text:
        return "action_auth_user"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        predicted_intent = tracker.get_intent_of_latest_message()
        current_username = next(tracker.get_latest_entity_values("username"), None)

        if current_username is not None:
            possible_p_methods = ["your Paypal account ("+current_username+")", 
                            "your IBAN IT12345678900000",
                            "your VISA card with number 1234 5678 9000"]
            possible_c_methods = ["your Paypal account ("+current_username+")", 
                            "your IBAN IT12345678900000",
                            "your VISA card with number 1234 5678 9000"]
            if(predicted_intent == 'insert_username_login'):
                dispatcher.utter_message(text="Successfully logged in! Welcome back "+current_username+"!")
                balance = round(random.uniform(0.0, 150.0), 2)
                monthly_report = round(random.uniform(-150.0, 150.0), 2)
                weekly_report = round(random.uniform(-150.0, 150.0), 2)
                p_method_index = int(round(random.uniform(0, 2), 0))
                c_method_index = int(round(random.uniform(0, 2), 0))
                p_method = possible_p_methods[p_method_index]
                c_method = possible_c_methods[c_method_index]
            else:
                dispatcher.utter_message(text="Account created successfully! Welcome "+current_username+"!")
                balance = 0.0
                monthly_report = 0.0
                weekly_report = 0.0
                p_method = None
                c_method = None
            
            return [SlotSet("authenticated", True), 
                    SlotSet("balance", balance), 
                    SlotSet("weekly_report", weekly_report), 
                    SlotSet("monthly_report", monthly_report),
                    SlotSet("payment_method", p_method),
                    SlotSet("crediting_method", c_method)]
        else:
            dispatcher.utter_message(text="Authentication failed! You could try with default username: name@mail.com")
            return []
        
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

        current_balance = float(tracker.get_slot("balance"))
        #reload_amount = float(tracker.get_slot("reload_amount"))
        #reload_amount = next(tracker.get_latest_entity_values("reload_amount"))
        #reload_amount = round(float(reload_amount_str), 2)
        #reload_amount = round(float(next(tracker.get_latest_entity_values("reload_amount"), 0.0)), 2)
        #reload_amount = next(tracker.get_latest_entity_values("reload_amount"), None)
        try:
            reload_amount = float(tracker.get_slot("reload_amount"))
            #dispatcher.utter_message(text=f"I found this reload amount: {reload_amount}")
            dispatcher.utter_message(text="Your reload was successful!")
            new_balance = round((current_balance + reload_amount), 2)
            dispatcher.utter_message(text=f"Your new balance is {new_balance}€.")
            return [SlotSet("balance", new_balance)]
        except:
            dispatcher.utter_message(text="Something goes wrong, no transactions have been made on your account.")
            dispatcher.utter_message(text="Try again by entering the sum in numbers")
            return[SlotSet("reload_amount", None)]
        
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


class ActionSetSingle(Action):
    def name(self) -> Text:
        return "action_set_single_play"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Assuming your JSON file is named 'database.json'

        # Extract entities from the tracker
        user_entity = tracker.get_slot("username")
        event_entity = tracker.get_slot("event")
        sport_entity = tracker.get_slot("sport")
        outcome_entity = tracker.get_slot("outcome")

        # Debug prints
        print("Event Entity:", event_entity)
        print("Sport Entity:", sport_entity)
        print("Outcome Entity:", outcome_entity)

        winning_status = False
        ticket_number =  str(random.randint(100000, 999999))
        # TO-DO check if the random number created already exists, if so regenerate it

        # Create a new ticket
        new_ticket = {
            "number": ticket_number,
            "username": user_entity,
            "type": "single",
            "events": [event_entity],
            "outcomes": [outcome_entity],
            "bet_amount": 10,
            "potential_win": 16.5,
            "win": winning_status
        }

        with open('./data/data.json', 'r') as file:
            data = json.load(file)

        # Add a new ticket to the "ticket" entity
        data["ticket"].append(new_ticket)

        # Save the updated data back to database.json
        with open('./data/data.json', 'w') as file:
            json.dump(data, file, indent=2)

        dispatcher.utter_message(f"Bet ticket number {new_ticket['number']} successfully placed!")


        return []


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