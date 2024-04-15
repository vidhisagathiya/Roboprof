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
            dispatcher.utter_message(
                text=f"I have no knowledge of courses offered by {university}.")
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
            dispatcher.utter_message(
                text=f"No course covers the topic {topic}.")
        else:
            answer = f"The following courses cover the topic {topic}:\n"
            for course in courses:
                answer = answer + course['courseName'] + \
                    ": " + course['link'] + "\n"
            dispatcher.utter_message(text=f"{answer}")

        return []


# A1-3. Which [topics] are covered in [course] during [lecture number]?
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
            dispatcher.utter_message(
                text=f"No topics covered in {lectureNumber} or {lectureNumber} did not happen.")
        else:
            answer = f"The following topics were covered in the lecture {lectureNumber} of the course {csubject}{cnumber}:\n"
            for topic in topics:
                answer = answer + topic['topicName'] + \
                    ": " + topic['topic'] + "\n"
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
            courses.append({"courseLabel": courseLabelValue,
                           "title": courseTitleValue})
        return courses

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subject = tracker.slots['subject']

        courses = self.response_request(subject)

        if not courses:
            dispatcher.utter_message(
                text=f"{subject} does not offer any courses.")
        else:
            answer = f"The courses offered by the subject {subject} are:\n"
            for course in courses:
                answer = answer + course['courseLabel'] + \
                    ": " + course['title'] + "\n"
            dispatcher.utter_message(text=f"{answer}")

        return []

# A1-5. What [materials] (slides, readings) are recommended for [topic] in [course] [number]?
class MaterialForCourse(Action):

    def name(self) -> Text:
        return "action_about_materials"

    def response_request(self, csubject, cnumber, topic):
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/>
SELECT ?material
WHERE {{
?course cu:hasTopic ?topics ;
cu:hasCourseSubject ?courseSubject; cu:hasCourseNumber ?courseNumber .
?topics foaf:name ?topicName ;
cu:hasMaterials ?material .
FILTER(?courseSubject = "{csubject}")
filter(?courseNumber = "{cnumber}")
filter(?topicName= "{topic}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        materials = []
        bindings = results["bindings"]

        for material in bindings:
            materialValue = material['material']['value']
            materials.append({'material': materialValue})

        return materials

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()
        topic = tracker.slots['topic'].strip()
        materials = self.response_request(csubject, cnumber, topic)
        if not materials:
            dispatcher.utter_message(
                text=f"The course {course} does not exist or is not offered by {university}.")
        else:
            answer = f"The course {course} has the following material:\n"
            for material in materials:
                answer = answer + material['material'] + "\n"
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
        return {'courseLabel': courseLabelValue, 'credits': creditsValue}

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
            dispatcher.utter_message(
                text=f"The course {course} does not exist or is not offered by {university}.")
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


# 7. For [course] [number], what additional resources (links to web pages) are available?
class AdditionalResources(Action):

    def name(self) -> Text:
        return "action_about_additional_resources"

    def response_request(self, csubject, cnumber):
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/> 

SELECT ?links
WHERE {{
  	?course rdfs:seeAlso ?links;
           cu:hasCourseSubject ?courseSubject;
           cu:hasCourseNumber ?courseNumber .
  
  FILTER(?courseSubject = "EDUC")
  FILTER(?courseNumber = "301")
}}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        resources = []
        bindings = results["bindings"]

        for resource in bindings:
            resourceValue = resource['links']['value']
            resources.append({'link': resourceValue})

        return resources

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()

        resources = self.response_request(csubject, cnumber)
        if not resources:
            dispatcher.utter_message(
                text=f"The course {course} does not exist.")
        else:
            answer = f"The course {course} has the following additional resources:\n"
            for resource in resources:
                answer = answer + resource['link'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []


# A1 - 8. Detail the content (slides, worksheets, readings) available for [lecture number] in [course] [number].
class DetailContentForCourse(Action):

    def name(self) -> Text:
        return "action_about_detail_content"

    def response_request(self, csubject, cnumber, lnumber):
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/>

SELECT ?contentURI
WHERE {{
  cu:Concordia_University cu:Offers ?course .
  	?course cu:hasCourseSubject ?subject ;
           cu:hasCourseNumber ?number ;
           cu:hasLecture ?lecture .
  	?lecture cu:hasLectureContent ?content ;
            cu:hasLectureNumber ?lecNumber.
  ?content rdfs:seeAlso ?contentURI .
  FILTER(?subject = "{csubject}")
  FILTER(?number = "{cnumber}")
  FILTER(?lecNumber = {lnumber})
}}

        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        contents = []
        bindings = results["bindings"]

        for content in bindings:
            contentValue = content['contentURI']['value']
            contents.append({'content': contentValue})

        return contents

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()

        courseEvent = tracker.slots['lecture'].strip()
        courseEventValues = re.split(
            r'([^\d]*)(\d.*)', courseEvent, maxsplit=1)
        eventNumber = courseEventValues[2]

        contents = self.response_request(csubject, cnumber, eventNumber)
        if not contents:
            dispatcher.utter_message(
                text=f"The course {course} does not exist.")
        else:
            answer = f"The course {course} has the following contents:\n"
            for content in contents:
                answer = answer + content['content'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []


# A1-9. What reading materials are recommended for studying [topic] in [course]?
class ReadingMaterialForStudying(Action):

    def name(self) -> Text:
        return "action_about_reading_material"

    def response_request(self, csubject, topic):
        query = f"""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX tc: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/>
SELECT distinct ?materials
WHERE {{
?course cu:hasTopic ?topics ;
cu:hasCourseSubject ?courseSubject; cu:hasCourseNumber ?courseNumber .
?topics foaf:name ?topicName ;
cu:hasMaterials ?materials .
FILTER(?courseSubject = "{csubject}")
filter(?topicName= "{topic}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        materials = []
        bindings = results["bindings"]

        for material in bindings:
            materialValue = material['materials']['value']
            materials.append({'material': materialValue})

        return materials

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()

        topic = tracker.slots['topic'].strip()

        materials = self.response_request(csubject, topic)
        if not materials:
            dispatcher.utter_message(
                text=f"The course {course} does not exist.")
        else:
            answer = f"The course {course} has the following maaterials to study:\n"
            for material in materials:
                answer = answer + material['material'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []

# A1- 10. What competencies [topics] does a student gain after completing [course] [number]?
class CompetenciesOfStudent(Action):

    def name(self) -> Text:
        return "action_about_competencies_of_student"

    def response_request(self, csubject, cnumber):
        query = f"""
        PREFIX dbp: <http://dbpedia.org/property/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cu: <http://is-concordia.io/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?topicName ?topicLink
WHERE {{
  ?course a cu:Course .
  ?course cu:hasTopic ?topic .
  ?topic foaf:name ?topicName;
         dbp:subject ?topicLink .
  ?course cu:hasCourseSubject ?subject .
  ?course cu:hasCourseNumber ?number .
  FILTER(?subject = "{csubject}")
  FILTER(?number = "{cnumber}")
}}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        competencies = []
        bindings = results["bindings"]

        for competency in bindings:
            competencyValue = competency['topicName']['value']
            linkValue = competency['topicLink']['value']
            competencies.append({'topicName': competencyValue, "topicLink": linkValue})

        return competencies

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()

        competencies = self.response_request(csubject, cnumber)
        if not competencies:
            dispatcher.utter_message(
                text=f"The course {course} does not exist.")
        else:
            answer = f"The student will gain the following competencies by completing the {course} course:\n"
            for competency in competencies:
                answer = answer + competency['topicName'] + ": "+ competency['topicLink'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []

# 11. What grades did [student] achieve in [course] [number]?
class GradesOfStudent(Action):

    def name(self) -> Text:
        return "action_about_student_grades"

    def response_request(self, csubject, cnumber, student):
        query = f"""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cu: <http://is-concordia.io/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?studentName ?gradeValue
        WHERE {{
          ?student cu:isEnrolledIn ?course;
                 foaf:name ?studentName  ;
                 cu:hasStudentID ?studentID .
          ?course cu:hasCourseSubject ?subject ;
  					cu:hasCourseNumber ?number .
  ?student ?course ?gradeValue
  FILTER(?subject = "{csubject}")
  FILTER(?number = "{cnumber}")
  filter(?studentID = "{student}")
        }}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        grades = []
        bindings = results["bindings"]

        for grade in bindings:
            studentName = grade['studentName']['value']
            grade = grade['gradeValue']['value']
            grades.append({'studentName': studentName, "gradeValue": grade})

        return grades

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print(tracker.slots)
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()

        student = tracker.slots['student'].strip()

        grades = self.response_request(csubject, cnumber, student)
        if not grades:
            dispatcher.utter_message(
                text=f"The course {course} does not exist.")
        else:
            answer = f"The student with ID {student} has the following grades in {course} course:\n"
            for grade in grades:
                answer = answer + grade['studentName'] + ": "+ grade['gradeValue'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []

# 12. Which [students] have completed [course] [number]?
class StudentCourseCompleted(Action):

    def name(self) -> Text:
        return "action_about_student_courses_completed"

    def response_request(self, csubject, cnumber):
        query = f"""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cu: <http://is-concordia.io/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT distinct ?id ?studentName 
        WHERE {{
          ?student cu:isEnrolledIn ?course;
                 foaf:name ?studentName  ;
                 cu:hasStudentID ?id .
          ?course cu:hasCourseSubject ?subject ;
  					cu:hasCourseNumber ?number .
  ?student ?course ?gradeValue
  FILTER(?subject = "{csubject}")
  FILTER(?number = "{cnumber}")
        }}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        students = []
        bindings = results["bindings"]

        for student in bindings:
            studentName = student['studentName']['value']
            studentId= student['id']['value']
            
            students.append({'studentId': studentId, "studentName": studentName})

        return students

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course']
        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)
        csubject = values[1].upper().strip()
        cnumber = values[2].strip()

        students = self.response_request(csubject, cnumber)
        if not students:
            dispatcher.utter_message(
                text=f"The course {course} does not exist.")
        else:
            answer = f"The following students have completed the {course} course:\n"
            for student in students:
                answer = answer + student['studentName'] + ": "+ student['studentId'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []

# A1 -13. Print a transcript for a [student], listing all the course taken with their grades.
class StudentTranscript(Action):

    def name(self) -> Text:
        return "action_about_student_transcript"

    def response_request(self, student):
        query = f"""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX teach: <http://linkedscience.org/teach/ns#>
PREFIX cu: <http://is-concordia.io/>

SELECT ?name ?id ?courseTitle ?grade
        WHERE {{
          ?student cu:isEnrolledIn ?course .
  ?course teach:courseTitle ?courseTitle .
  		?student foaf:name ?name .
  		?student cu:hasStudentID ?id .
  		?student ?course ?grade
  FILTER(?id = "{student}")
        }}
        """
        response = requests.post(SPARQL_ENDPOINT, data={'query': query})
        # Use the json module to load CKAN's response into a dictionary.
        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]
        grades = []
        bindings = results["bindings"]

        for grade in bindings:
            studentName = grade['studentName']['value']
            studentId = grade['id']['value']
            courseTitle = grade['courseTitle']['value']
            grade = grade['gradeValue']['value']
            grades.append({'studentId': studentId, 'studentName': studentName,"courseTitle":courseTitle, "gradeValue": grade})

        return grades

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.slots)
        student = tracker.slots['student']

        grades = self.response_request(student)
        if not grades:
            dispatcher.utter_message(
                text=f"The student {student} does not exist.")
        else:
            answer = f"The transcript for the student with ID {student} \n"
            for grade in grades:
                answer = answer + grade['id'] + "\t" + grade['studentName'] + "\t" + grade['courseTitle'] + "\t" + grade['gradeValue'] + "\n"
            dispatcher.utter_message(text=f"{answer}")
        return []

# #Need this
# #A2-Q3 - Which topics are covered in <course event>?"
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

        courseEvent = tracker.slots['courseEvent'].strip()
        courseEventValues = re.split(
            r'([^\d]*)(\d.*)', courseEvent, maxsplit=1)
        eventNumber = courseEventValues[2]

        query = ""

        if "lec" in courseEvent.lower() or "lecture" in courseEvent.lower():
            courseEvent = "Lecture"
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
  FILTER(?courseSubject = "{csubject}")
  FILTER(?courseNumber = "{cnumber}")
  FILTER(?lectureNumber = {eventNumber})
}}
"""
        if "lab" in courseEvent.lower() or "laboratory" in courseEvent.lower():
            courseEvent = "Laboratory"
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
  		cu:hasLab ?lab ;
    cu:hasCourseSubject ?courseSubject ;
    cu:hasCourseNumber ?courseNumber .
  ?lab cu:topicsCovered ?topics ;
           cu:hasLabNumber ?labNumber .
  ?topics foaf:name ?topicName .
  FILTER(?courseSubject = "{csubject}")
  FILTER(?courseNumber = "{cnumber}")
  FILTER(?labNumber = {eventNumber})
}}
"""

        response = requests.post(SPARQL_ENDPOINT,
                                 data={'query': query})

        y = json.loads(response.text)

        results = y["results"]
        bindings = results["bindings"]
        if not bindings:
            dispatcher.utter_message(
                text=f"Sorry, {csubject} {cnumber} doesn't have a {courseEvent}\n")
            return

        dispatcher.utter_message(
            text=f"{courseEvent} {eventNumber} of {csubject} {cnumber} covers:\n")

        for result in bindings:
            dispatcher.utter_message(
                text=f"\t--> {result['topicName']['value']} || URI: {result['topics']['value']}\n")

        return []

# Need this
# A2-Q2 What is course [course] about?


class CourseDescription(Action):

    def name(self) -> Text:
        return "action_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.slots['course'].replace(" ", "")

        values = re.split(r'([^\d]*)(\d.*)', course, maxsplit=1)

        csubject = values[1].upper()
        cnumber = values[2]

        data = {'query': f"""
PREFIX cu: <http://is-concordia.io/>
PREFIX teach: <http://linkedscience.org/teach/ns#>
SELECT ?courseName ?courseDescription
WHERE {{
   cu:Concordia_University cu:Offers ?course .
	?course teach:courseDescription ?courseDescription ;
         teach:courseTitle ?courseName ;
         cu:hasCourseSubject ?courseSubject ;
         cu:hasCourseNumber ?courseNumber .
  filter(?courseSubject = "{csubject}")
    filter(?courseNumber = "{cnumber}")
}}
"""}
        response = requests.post(SPARQL_ENDPOINT,
                                 data=data)

        # # Use the json module to load CKAN's response into a dictionary.

        y = json.loads(response.text)

        # the result is a Python dictionary:
        results = y["results"]

        if not results or not results["bindings"]:
            dispatcher.utter_message(
                text="Course is not found or does not have a description.")
        else:
            bindings = results["bindings"][0]
            description = bindings["courseDescription"]
            vdescription = description["value"]
            dispatcher.utter_message(
                text=f"Description of course {csubject} {cnumber}: {vdescription}")

        return []
