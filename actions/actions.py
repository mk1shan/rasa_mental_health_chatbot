from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

class ActionStartDASS21(Action):
    def name(self) -> Text:
        return "action_start_dass21"
     
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("current_question", 0), FollowupAction("action_ask_dass21_question")]

class ActionCalculateDASS21Score(Action):
    def name(self) -> Text:
        return "action_calculate_dass21_score"
     
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        responses = tracker.get_slot("dass21_responses")
        
        depression_score = sum(responses[0:7]) * 2
        anxiety_score = sum(responses[7:14]) * 2
        stress_score = sum(responses[14:21]) * 2
        
        depression_level, anxiety_level, stress_level = self.interpret_dass21_scores(
            depression_score, anxiety_score, stress_score)
        
        response = self.generate_response(
            depression_level, anxiety_level, stress_level
        )
        
        dispatcher.utter_message(text=response)
        
        return [
            SlotSet("depression_score", depression_score),
            SlotSet("anxiety_score", anxiety_score),
            SlotSet("stress_score", stress_score),
            SlotSet("depression_level", depression_level),
            SlotSet("anxiety_level", anxiety_level),
            SlotSet("stress_level", stress_level),
        ]

    def interpret_dass21_scores(self, depression_score, anxiety_score, stress_score):
        depression_levels = {
            0: "Normal",
            1: "Mild",
            2: "Moderate",
            3: "Severe",
            4: "Extremely Severe"
        }
        
        anxiety_levels = {
            0: "Normal",
            1: "Mild",
            2: "Moderate",
            3: "Severe",
            4: "Extremely Severe"
        }
        
        stress_levels = {
            0: "Normal",
            1: "Mild",
            2: "Moderate",
            3: "Severe",
            4: "Extremely Severe"
        }
        
        depression_level = depression_levels.get(
            min(4, int(depression_score // 14)), "Invalid")
        anxiety_level = anxiety_levels.get(
            min(4, int(anxiety_score // 14)), "Invalid")
        stress_level = stress_levels.get(
            min(4, int(stress_score // 14)), "Invalid")
        
        return depression_level, anxiety_level, stress_level

    def generate_response(self, depression_level, anxiety_level, stress_level):
        if depression_level == "Extremely Severe" or anxiety_level == "Extremely Severe" or stress_level == "Extremely Severe":
            return self.get_extremely_severe_response()
        elif depression_level == "Severe" or anxiety_level == "Severe" or stress_level == "Severe":
            return self.get_severe_response()
        elif depression_level == "Moderate" or anxiety_level == "Moderate" or stress_level == "Moderate":
            return self.get_moderate_response()
        else:
            return self.get_normal_or_mild_response()

    def get_extremely_severe_response(self):
        return """
            I'm so sorry you're going through such a difficult time. It's clear that you're experiencing extremely severe symptoms, and I want you to know that I'm here to support you. Please don't hesitate to reach out to a mental health professional or call a crisis hotline. They can provide you with the specialized care and resources you need to start feeling better.
        """

    def get_severe_response(self):
        return """
            I understand this is a very challenging situation for you. The severity of your symptoms indicates that you may need additional support. I would recommend speaking with a therapist or counselor who can provide you with personalized care and treatment options. In the meantime, here are some helpful resources you can look into...
        """

    def get_moderate_response(self):
        return """
            I'm sorry to hear you're struggling with moderate symptoms. It's great that you're taking the time to assess your mental health. Some things that may help in the short term are practicing relaxation techniques, engaging in regular exercise, and reaching out to supportive friends or family members. Remember, you're not alone in this, and there are ways to manage these challenges.
        """

    def get_normal_or_mild_response(self):
        return """
            I'm glad to hear your symptoms are in the normal or mild range. It's important to continue taking care of your mental health, even when things aren't as severe. Remember to prioritize self-care, and don't hesitate to reach out if you ever need additional support. You've got this!
        """

class ActionAskDASS21Question(Action):
    def name(self) -> Text:
        return "action_ask_dass21_question"
     
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        questions = [
            "I found it hard to wind down",
            "I was aware of dryness of my mouth",
            "I couldn't seem to experience any positive feeling at all",
            "I experienced breathing difficulty (e.g. excessively rapid breathing, breathlessness in the absence of physical exertion)",
            "I found it difficult to work up the initiative to do things",
            "I tended to over-react to situations",
            "I experienced trembling (e.g. in the hands)",
            "I felt that I was using a lot of nervous energy",
            "I was worried about situations in which I might panic and make a fool of myself",
            "I felt that I had nothing to look forward to",
            "I found myself getting agitated",
            "I found it difficult to relax",
            "I felt down-hearted and blue",
            "I was intolerant of anything that kept me from getting on with what I was doing",
            "I felt I was close to panic",
            "I was unable to become enthusiastic about anything",
            "I felt I wasn't worth much as a person",
            "I felt that I was rather touchy",
            "I was aware of the action of my heart in the absence of physical exertion (e.g. sense of heart rate increase, heart missing a beat)",
            "I felt scared without any good reason",
            "I felt that life was meaningless"
        ]
        
        current_question = tracker.get_slot("current_question")
        if current_question is None:
            current_question = 0
                 
        if current_question < len(questions):
            dispatcher.utter_message(text=f"Question {current_question + 1}: {questions[current_question]}")
            return [SlotSet("current_question", current_question + 1)]
        else:
            return [FollowupAction("action_calculate_dass21_score")]

class ActionRecordDASS21Response(Action):
    def name(self) -> Text:
        return "action_record_dass21_response"
     
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        response = tracker.latest_message.get('text')
        
        try:
            response = int(response)
            if response < 0 or response > 3:
                dispatcher.utter_message(text="Please enter a number between 0 and 3.")
                return []
        except ValueError:
            dispatcher.utter_message(text="Please enter a valid number between 0 and 3.")
            return []
         
        responses = tracker.get_slot("dass21_responses") or []
        responses.append(response)
                 
        if len(responses) < 21:
            return [SlotSet("dass21_responses", responses), FollowupAction("action_ask_dass21_question")]     
        else:
            return [SlotSet("dass21_responses", responses), FollowupAction("action_calculate_dass21_score")]