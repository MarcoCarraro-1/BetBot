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

        # Save the updated data back to database.json
        with open('./data/data.json', 'w') as file:
            json.dump(data, file, indent=2)

        dispatcher.utter_message(f"Bet ticket number {new_ticket['number']} successfully placed!")

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