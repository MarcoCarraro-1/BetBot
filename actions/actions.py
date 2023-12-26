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