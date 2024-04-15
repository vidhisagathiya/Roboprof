# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
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
# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import requests
import json
import re
# import inflect

from rdflib import Graph, Literal, RDF, URIRef, Namespace, Dataset  # basic RDF handling

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


SPARQL_ENDPOINT = "http://localhost:3030/testData"

# A1-1. List all courses offered by [university]
class TopicsCourseLecture(Action):

    def name(self) -> Text:
        return "action_courses_offered_by_university"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        university = tracker.slots['university']
        
        query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/> 

SELECT ?title
WHERE {{
    cu:Concordia_University cu:Offers ?course .
  	?course tc:courseTitle ?title .
}}
"""
        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})

        # # Use the json module to load CKAN's response into a dictionary.
        print(response.text)
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        courses_offered = []

        for result in results["bindings"]:
            courseName = result["title"]['value']
            courses_offered.append(courseName)

        if not courses_offered:
            dispatcher.utter_message(text=f"I have no knowledge of courses offered by {university}.")
        else:
            answer = "Course offered by " + university + ":\n"
            for course in courses_offered:
                answer = answer + course + "\n"
            dispatcher.utter_message(text=f"{answer}")

        return []

# A1-2. In which courses is [topic] discussed?
class WhichCourseHasTopic(Action):

    def name(self) -> Text:
        return "action_course_uni_topic"

    def response_request(self, topicName):
        query = f"""
        PREFIX dbp: <http://dbpedia.org/property/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cu: <http://is-concordia.io/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?courseName ?link
WHERE {{
  ?course a cu:Course .
  ?course rdfs:label ?courseName.
  ?course cu:hasTopic ?topic .
	?topic foaf:name ?name .
  	?topic dbp:subject ?link.
  FILTER(?name = "{topicName}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.

        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]

        courses = []

        for result in results["bindings"]:
            course = result["courseName"]
            topicLink = result['link']
            
            courseValue = course['value']
            topicLinkValue = topicLink['value']
            
            row = {"courseName": courseValue, "link": topicLinkValue}
            courses.append(row)

        return courses

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = tracker.slots['topic'].replace(" ", "")

        courses = self.response_request(topic)
        
        if not courses:
            dispatcher.utter_message(text=f"No course covers the topic {topic}.")
        else:
            answer = f"The following courses cover the topic {topic}:\n"
            for course in courses:
                answer = answer + course['courseName'] + ": " + course['link'] + "\n"
            dispatcher.utter_message(text=f"{answer}")

        return []


# # A1-3. Which [topics] are covered in [course] during [lecture number]?
class WhichTopicInCourseDuringLecture(Action):

    def name(self) -> Text:
        return "action_course_lecture_topics"

    def response_request(self, courseSubject, courseNumber, lectureNumber):
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/> 

SELECT ?topicName ?topics
WHERE {{
  	cu:Concordia_University cu:Offers ?course .
  	?course tc:courseTitle ?title ;
  		cu:hasLecture ?lecture ;
    cu:hasCourseSubject ?courseSubject ;
    cu:hasCourseNumber ?courseNumber .
  ?lecture cu:topicsCovered ?topics ;
           cu:hasLectureNumber ?lectureNumber .
  ?topics foaf:name ?topicName .
  FILTER(?courseSubject = "{courseSubject}")
  FILTER(?lectureNumber = {lectureNumber})
  FILTER(?courseNumber = "{courseNumber}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.

        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]

        topics = []

        for result in results["bindings"]:
            topicName = result["topicName"]
            topic = result["topics"]
            
            topicNameValue = topicName["value"]
            topicValue = topic["value"]
            
            row = {"topicName": topicNameValue, "topic": topicValue}
            topics.append(row)

        return topics

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course'].replace(" ", "")

        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)

        csubject = values[1].upper()
        cnumber = values[2]

        lecture = tracker.slots['lecture'].strip()
        lectureValues = re.split(
            r'([^\d]*)(\d.*)', lecture, maxsplit=1)
        lectureNumber = lectureValues[2]

        topics = self.response_request(csubject, cnumber, lectureNumber)
        
        if not topics:
            dispatcher.utter_message(text=f"No topics covered in {lectureNumber} or {lectureNumber} did not happen.")
        else:
            answer = f"The following topics were covered in the lecture {lectureNumber} of the course {csubject}{cnumber}:\n"
            for topic in topics:
                answer = answer + topic['topicName'] + ": " + topic['topic'] + "\n"
            dispatcher.utter_message(text=f"{answer}")

        return []


# A1-4. List all [courses] offered by [university] within the [subject] (e.g., “COMP”, “SOEN”).
class WhichCourseWithinSubject(Action):

    def name(self) -> Text:
        return "action_courses_within_subject"

    def response_request(self, csubject):
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/> 

SELECT ?courseLabel ?title
WHERE {{
    cu:Concordia_University cu:Offers ?course .
  	?course tc:courseTitle ?title ;
           rdfs:label ?courseLabel .
  	?course cu:hasCourseSubject ?subject.
  FILTER(?subject = "{csubject}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.

        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]

        courses = []

        for result in results["bindings"]:
            courseLabel = result["courseLabel"]
            courseTitle = result['title']
            
            courseLabelValue = courseLabel["value"]
            courseTitleValue = courseTitle["value"]
            courses.append({"courseLabel": courseLabelValue,"title": courseTitleValue})
        return courses

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subject = tracker.slots['subject']

        courses = self.response_request(subject)

        if not courses:
            dispatcher.utter_message(text=f"{subject} does not offer any courses.")
        else:
            answer = f"The courses offered by the subject {subject} are:\n"
            for course in courses:
                answer = answer + course['courseLabel'] + ": " + course['title'] + "\n"
            dispatcher.utter_message(text=f"{answer}")

        return []


#  A1-6. How many credits is [course] [number] worth?
class ContentCourseLecture(Action):

    def name(self) -> Text:
        return "action_about_credits"

    def response_request(self, csubject, cnumber):
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/>

SELECT ?courseLabel ?credits
WHERE {{
    ?course cu:hasCredits ?credits ;
            cu:hasCourseSubject ?subject;
            cu:hasCourseNumber ?number ;
            rdfs:label ?courseLabel .  
  FILTER(?subject = "{csubject}")
  FILTER(?number = "{cnumber}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        courseLabel = results["bindings"][0]['courseLabel']
        credits = results["bindings"][0]['credits']
        courseLabelValue = courseLabel['value']
        creditsValue = credits['value']
        return {'courseLabel':courseLabelValue, 'credits': creditsValue}

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.slots['course'].replace(" ", "")
        university = tracker.slots['university']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)

        csubject = values[1].upper()
        cnumber = values[2]

        content = self.response_request(csubject, cnumber)

        if not content:
            dispatcher.utter_message(text=f"The course {course} does not exist or is not offered by {university}.")
        else:
            answer = f"The course {course} is of {content['credits']} credits."
            dispatcher.utter_message(text=f"{answer}")

        return []


# # Q6) What components does the course [course] have?
# class ActionCourseComponents(Action):

#     def name(self) -> Text:
#         return "action_course_components"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         course = tracker.slots['course']

#         values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
#         csubject = values[1].upper().replace(" ", "")
#         cnumber = values[2]

#         if csubject != "COMP" or (cnumber != "346" and cnumber != "474"):
#             dispatcher.utter_message(text="Sorry, we currently only support finding components of COMP 474 and COMP 346.")
#             return

#         response = requests.post(SPARQL_ENDPOINT,
#                                  data={'query': """
#                             PREFIX vivo: <http://vivoweb.org/ontology/core#>
#                             PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#                             PREFIX DC: <http://purl.org/dc/terms/>
#                             PREFIX acad: <http://acad.io/schema#>
#                             PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#                             PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#                             PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#                             PREFIX acaddata: <http://acad.io/data#>

#                             SELECT ?cname ?component ?componentLabel
#                             WHERE{
#                                 ?course a vivo:Course.
#                                 ?course foaf:name ?cname.
#                                 ?course acad:courseNumber "%s"^^xsd:int.
#                                 ?course acad:courseSubject "%s"^^xsd:string.
#                                 ?course acad:courseHas ?component.
#                                 ?component rdfs:label ?componentLabel.
#                             }
#                             """ % (cnumber, csubject)
#                                        })

#         y = json.loads(response.text)

#         results = y["results"]
#         bindings = results["bindings"]

#         dispatcher.utter_message(text=f"{csubject} {cnumber} has:\n")

#         for component in bindings:
#             dispatcher.utter_message(text=f"\t-->{component['componentLabel']['value']}\n")

#         return []


# # Q7) Does [course] have labs?
# class ActionCourseLabs(Action):

#     def name(self) -> Text:
#         return "action_course_labs"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         course = tracker.slots['course']

#         values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
#         csubject = values[1].upper().replace(" ", "")
#         cnumber = values[2]

#         if csubject != "COMP" or (cnumber != "346" and cnumber != "474"):
#             dispatcher.utter_message(text="Sorry, we currently only support finding whether or not COMP 474 or COMP 346 have labs.")
#             return

#         response = requests.post(SPARQL_ENDPOINT,
#                                  data={'query': """
#                                     PREFIX vivo: <http://vivoweb.org/ontology/core#>
#                                     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#                                     PREFIX DC: <http://purl.org/dc/terms/>
#                                     PREFIX acad: <http://acad.io/schema#>
#                                     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#                                     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#                                     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#                                     PREFIX acaddata: <http://acad.io/data#>

#                                     ASK{
#                                     ?course a vivo:Course.
#                                     ?course acad:courseNumber "%s"^^xsd:int.
#                                     ?course acad:courseSubject "%s"^^xsd:string.
#                                     ?course acad:courseHas acad:Lab.
#                                     }
#                                     """ % (cnumber, csubject)
#                                        })

#         y = json.loads(response.text)

#         result = y["boolean"]

#         if result:
#             dispatcher.utter_message(text=f"YES, {csubject} {cnumber} has labs.")
#         else:
#             dispatcher.utter_message(text=f"NO, {csubject} {cnumber} does not have labs.")

#         return []


# # Q8) What courses does the [department] department offer?
# class ActionDepartmentCourses(Action):

#     def name(self) -> Text:
#         return "action_department_courses"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         department = tracker.slots['department'].strip()

#         if department.lower() == "csse" or department.lower() == "computer science and software engineering" or \
#                 department.lower() == "computer science" or department.lower() == "software engineering":
#             department = "Computer Science and Software Engineering (CSSE)"
#         elif department.lower() == "bcce" or \
#                 department.lower() == "building, civil and environmental engineering" or \
#                 department.lower() == "building engineering" or department.lower() == "civil engineering" or \
#                 department.lower() == "environmental engineering":
#             department = "Building, Civil and Environmental Engineering (BCEE)"
#         elif department.lower() == "ece" or department.lower() == "electrical engineering" \
#                 or department.lower() == "computer engineering":
#             department = "Electrical and Computer Engineering (ECE)"

#         response = requests.post(SPARQL_ENDPOINT,
#                                  data={'query': """
#                                             PREFIX vivo: <http://vivoweb.org/ontology/core#>
#                                             PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#                                             PREFIX DC: <http://purl.org/dc/terms/>
#                                             PREFIX acad: <http://acad.io/schema#>
#                                             PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#                                             PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#                                             PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#                                             PREFIX acaddata: <http://acad.io/data#>

#                                             SELECT  ?csubject ?cnumber ?cname
#                                             WHERE{
#                                                 ?course a vivo:Course;
#                                                 foaf:name ?cname;
#                                                 acad:courseNumber ?cnumber;
#                                                 acad:courseSubject ?csubject;
#                                                 vivo:AcademicDepartment "%s"^^xsd:string.
#                                             }
#                                             """ % department
#                                        })

#         y = json.loads(response.text)

#         results = y["results"]
#         bindings = results["bindings"]

#         course = ""
#         courses_offered = []

#         for result in bindings:
#             for key in result:
#                 if key == "csubject":
#                     for subKey in result[key]:
#                         if subKey == "value":
#                             course = result[key][subKey]
#                 if key == "cnumber":
#                     for subKey in result[key]:
#                         if subKey == "value":
#                             course = course + " " + result[key][subKey]
#             courses_offered.append(course)

#         dispatcher.utter_message(text=f"\n{department} offers:\n")

#         for course in courses_offered:
#             dispatcher.utter_message(text=f" - {course}\n")

#         return []


# # Q9) How many courses does the university [university] offer?
# class ActionNumberOfUniCourses(Action):

#     def name(self) -> Text:
#         return "action_number_of_uni_courses"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         university = tracker.slots['university']

#         if "concordia" in university.lower() or "university" in university.lower():
#             university = "Concordia_University"

#         response = requests.post(SPARQL_ENDPOINT,
#                                  data={'query': """
#                                                     PREFIX vivo: <http://vivoweb.org/ontology/core#>
#                                                     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#                                                     PREFIX DC: <http://purl.org/dc/terms/>
#                                                     PREFIX acad: <http://acad.io/schema#>
#                                                     PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#                                                     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#                                                     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#                                                     PREFIX acaddata: <http://acad.io/data#>

#                                                     SELECT  (COUNT(?course) AS ?coursesNum)
#                                                     WHERE{
#                                                        acaddata:%s a acad:University.
#                                                        acaddata:%s acad:offers ?course.
#                                                     } GROUP BY ?uni
#                                                     """ % (university, university)
#                                        })

#         y = json.loads(response.text)

#         results = y["results"]
#         bindings = results["bindings"]

#         numberOfCourses = 0

#         for result in bindings:
#             for key in result:
#                 if key == "coursesNum":
#                     for subKey in result[key]:
#                         if subKey == "value":
#                             numberOfCourses = result[key][subKey]

#         university = university.replace("_", " ")

#         dispatcher.utter_message(text=f"\n {university} offers a total of {numberOfCourses} courses")


# # Q10) How many topics are covered in [course]?
# class ActionNumTopicsInCourse(Action):

#     def name(self) -> Text:
#         return "action_num_topics_in_course"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         course = tracker.slots['course']

#         values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
#         csubject = values[1].upper().replace(" ", "")
#         cnumber = values[2]

#         response = requests.post(SPARQL_ENDPOINT,
#                                  data={'query': """
#                                                 PREFIX vivo: <http://vivoweb.org/ontology/core#>
#                                                 PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#                                                 PREFIX DC: <http://purl.org/dc/terms/>
#                                                 PREFIX acad: <http://acad.io/schema#>
#                                                 PREFIX foaf: <http://xmlns.com/foaf/0.1/>
#                                                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#                                                 PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
#                                                 PREFIX acaddata: <http://acad.io/data#>

#                                                 SELECT (COUNT(?topic) AS ?topicNum)
#                                                 WHERE {
#                                                     ?course a vivo:Course.
#                                                     ?course foaf:name ?courseName.
#                                                     ?course acad:courseNumber "%s"^^xsd:int.
#                                                     ?course acad:courseSubject "%s"^^xsd:string.
#                                                     ?course acad:coversTopic ?topic.
#                                                 } GROUP BY ?course ?courseName
#                                                 """ % (cnumber, csubject)
#                                        })

#         y = json.loads(response.text)

#         results = y["results"]
#         bindings = results["bindings"]

#         dispatcher.utter_message(text=f"{csubject} {cnumber} covers {bindings[0]['topicNum']['value']} topics")

# Need this
    
# A2-Q1. For a course c, list all covered topics t, printing out their English labels and their DBpedia/Wikidata URI, 
# together with the course event URI (e.g., ’lab3’) and resource URI (e.g., ’slides10’) where they appeared. Filter out duplicates.
class ActionTopicsCovered(Action):

    def name(self) -> Text:
        return "action_topics_covered"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()

        query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX tc: <http://linkedscience.org/teach/ns#>
            PREFIX cu: <http://is-concordia.io/> 

            SELECT DISTINCT ?topicName ?topic ?courseEvent ?resource
            WHERE {{
                ?course a cu:Course .
                ?course tc:courseTitle ?title ;
                        cu:hasCourseSubject ?courseSubject ;
                        cu:hasCourseNumber ?courseNumber .
                ?courseEvent ?eventPredicate ?event ;
                            cu:partOfCourse ?course .
                ?event cu:hasTopic ?topic ;
                        cu:hasResource ?resource .
                ?topic foaf:name ?topicName ;
                       rdf:type ?topicType .
                FILTER(?courseSubject = "{csubject}")
                FILTER(?courseNumber = "{cnumber}")
                FILTER(?topicType = tc:Topic)
            }}
        """

        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})

        y = json.loads(response.text)

        results = y["results"]
        bindings = results["bindings"]
        if not bindings:
            dispatcher.utter_message(
                text=f"Sorry, no topics covered for {csubject} {cnumber}.")
            return

        dispatcher.utter_message(
            text=f"Topics covered in {csubject} {cnumber}:\n")

        for result in bindings:
            topic_name = result.get("topicName", {}).get("value", "")
            topic_uri = result.get("topic", {}).get("value", "")
            course_event_uri = result.get("courseEvent", {}).get("value", "")
            resource_uri = result.get("resource", {}).get("value", "")

            dispatcher.utter_message(
                text=f"Topic: {topic_name}\nTopic URI: {topic_uri}\nCourse Event URI: {course_event_uri}\nResource URI: {resource_uri}\n")

        return []


# A2-Q2. For a given topic t (DBpedia or Wikidata URI), list all courses c and their events e where the given topic t appears, 
# along with the count of occurrences, with the results sorted by this count in descending order.
class ActionCoursesForTopic(Action):

    def name(self) -> Text:
        return "action_courses_for_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic_uri = tracker.slots['topic_uri']

        query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX tc: <http://linkedscience.org/teach/ns#>
            PREFIX cu: <http://is-concordia.io/>

            SELECT ?course ?event (COUNT(?event) AS ?eventCount)
            WHERE {{
                ?course a cu:Course ;
                        tc:partOfEvent ?event .
                ?event cu:hasTopic <{topic_uri}> .
            }}
            GROUP BY ?course ?event
            ORDER BY DESC(?eventCount)
        """

        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})

        y = json.loads(response.text)

        results = y["results"]
        bindings = results["bindings"]
        if not bindings:
            dispatcher.utter_message(
                text=f"No courses found for the given topic URI: {topic_uri}")
            return

        dispatcher.utter_message(text=f"Courses and their events where the topic {topic_uri} appears:\n")

        for result in bindings:
            course_uri = result.get("course", {}).get("value", "")
            event_uri = result.get("event", {}).get("value", "")
            event_count = result.get("eventCount", {}).get("value", "")

            dispatcher.utter_message(
                text=f"Course URI: {course_uri}\nEvent URI: {event_uri}\nNumber of occurrences: {event_count}\n")

        return []
    
# A2-Q3. For a given topic t, list the precise course URI, course event URI, and corresponding resource URI where the topic is covered.
class ActionCourseEventResourceForTopic(Action):

    def name(self) -> Text:
        return "action_course_event_resource_for_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        topic_uri = tracker.slots['topic_uri']

        query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX tc: <http://linkedscience.org/teach/ns#>
            PREFIX cu: <http://is-concordia.io/>

            SELECT ?course ?event ?resource
            WHERE {{
                ?course a cu:Course ;
                        tc:partOfEvent ?event .
                ?event cu:hasTopic <{topic_uri}> .
                ?event tc:hasResource ?resource .
            }}
        """

        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})

        y = json.loads(response.text)

        results = y["results"]
        bindings = results["bindings"]
        if not bindings:
            dispatcher.utter_message(
                text=f"No course events found for the given topic URI: {topic_uri}")
            return

        dispatcher.utter_message(text=f"Course events and corresponding resources where the topic {topic_uri} is covered:\n")

        for result in bindings:
            course_uri = result.get("course", {}).get("value", "")
            event_uri = result.get("event", {}).get("value", "")
            resource_uri = result.get("resource", {}).get("value", "")

            dispatcher.utter_message(
                text=f"Course URI: {course_uri}\nEvent URI: {event_uri}\nResource URI: {resource_uri}\n")

        return []
