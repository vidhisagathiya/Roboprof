import csv
import os
from os import path
# import spacy  # Added import for spaCy

import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF

# Define BASE_DATA_DIR
BASE_DATA_DIR = os.getcwd() + "/data"

CU = Namespace("http://is-concordia.io/")
DBR = Namespace("http://dbpedia.org/resource/")
DBP = Namespace("http://dbpedia.org/property/")
TEACH = Namespace("http://linkedscience.org/teach/ns#")

# Initialize spaCy language model
# nlp = spacy.load("en_core_web_lg")


special_courses = [URIRef("http://is-concordia.io/COMP6231"), URIRef("http://is-concordia.io/COMP6741")]
special_course_codes = ['6231', '6741']
# special_courses_websites = [URIRef("http://concordia.catalog.acalog.com/preview_course_nopop.php?catoid=1&coid=2703"),
#                             URIRef("http://concordia.catalog.acalog.com/preview_course_nopop.php?catoid=1&coid=2718")]

# All titles are dbpedia resources
lecture_titles_6231 = ['Construction_and_Analysis_of_Distributed_Processes', 'Virtual_machine', 'Programming_paradigm',
                      'Transition_(computer_science)', 'Message-oriented_middleware', 'Thread_(computing)',
                      'Category:Distributed_computing_architecture', 'Distributed_database', 'Fault_tolerance', 
                      'Consistency_(database_systems)', 'Replication_(computing)', 'Distributed_algorithm', 'Synchronization_(computer_science)', 'Domain_Name_System']

lecture_titles_6741 = ['Intelligent_system', 'Knowledge_graph', 'Ontology_(information_science)',
                      'SPARQL', 'Knowledge_base', 'Recommender_system', 'Machine_learning',
                      'Intelligent_agent', 'Text_mining']


comp6231_description = "Principles of distributed computing: scalability, transparency, concurrency, consistency, fault tolerance. \
    Client-server interaction technologies: interprocess communication, sockets, group communication, remote procedure call, remote method invocation, object request broker, CORBA, web services. \
    Distributed server design techniques: process replication, fault tolerance through passive replication, high availability through active replication, coordination and agreement transactions and concurrency control. \
    Designing software fault-tolerant highly available distributed systems using process replication. Laboratory: two hours per week."
comp6741_description = "(COMP 474): Rule-based expert systems, blackboard architecture, and agent-based. Knowledge \
    acquisition and representation. Uncertainty and conflict resolution. Reasoning and explanation. \
    Design of intelligent systems. Project. \
    (COMP 6741): Knowledge representation and reasoning. Uncertainty and conflict resolution. \
    Design of intelligent systems. Grammar-based, rule-based, and blackboard architectures. A \
    project is required."

resources_dir = ['Reading', 'Slide', 'Worksheet', 'Lab']
lecture_related_events = 'Lab'

def generateKnowledgeBase(roboProfKG):
    '''
    Creates general knowledge graph required for RoboProf.

    Parameters:
        roboProfKG (rdflib.Graph): Instance of the Graph which needs to be populated.

    Returns:
        roboProfKG (rdflib.Graph): Instance of the Graph with knowledge base for RoboProf.
    '''
    # Add our university to the KB using the pre-defined schema
    roboProfKG.add((CU.Concordia_University, RDF.type, CU.University))
    roboProfKG.add((CU.Concordia_University, FOAF.name, Literal("Concordia University")))
    roboProfKG.add((CU.Concordia_University, RDFS.seeAlso, DBR.Concordia_University))


    with open('CLEANED_DATA.csv', 'r') as data:
        r = csv.DictReader(data)
        for row in r:
            # Create the course
            course_num = str(row['Course number']).split()[0]
            # print(course_num)
            # print(course_num[0])
            cn = URIRef("http://is-concordia.io/" + row['Course code'] + course_num)
            roboProfKG.add((cn, RDF.type, CU.Course))

            # Add to list of offered courses at Concordia
            roboProfKG.add((CU.Concordia_University, CU.Offers, cn))
            
            # Add course details
            roboProfKG.add((cn, TEACH.courseTitle, Literal(row['Title'])))
            roboProfKG.add((cn, CU.HasSubject, Literal(row['Course code'])))
            roboProfKG.add((cn, CU.CourseNumber, Literal(row['Course number'])))
            roboProfKG.add((cn, CU.hasCredits, Literal(row['Class Units'])))
            if cn not in special_courses:
                roboProfKG.add((cn, TEACH.courseDescription, Literal(row['Description'])))
            if row['Website'] != "":
                roboProfKG.add((cn, RDFS.seeAlso, Literal(row['Website'])))
            
            if cn in special_courses:
                roboProfKG = addCoreCoursesKnowledge(roboProfKG, row, cn)

    roboProfKG.serialize(destination="kb.ttl", format="turtle")
    roboProfKG.serialize(destination="kb_ntriples.rdf", format="ntriples")           

def addCoreCoursesKnowledge(roboProfKG, row, cn):
    '''
    Adds knowledge graph for specific courses for RoboProf.

    Parameters:
        roboProfKG (rdflib.Graph): Instance of the Graph which needs to be populated.

    Returns:
        roboProfKG (rdflib.Graph): Instance of the Graph with knowledge base for RoboProf.
    '''
            
    if cn in special_courses:
        if row['Course number'] == '6231':
            lecture_number = 11
            worksheets = 11
            roboProfKG.add((cn, CU.hasCourseOutline, CU["Users/nilesh/Work/COMP-474-IS/Roboprof/data/Soen6231/course_outline.pdf"]))
        else:
            lecture_number = 9
            worksheets = 8
            roboProfKG.add((cn, CU.hasCourseOutline, CU["Users/nilesh/Work/COMP-474-IS/Roboprof/data/Comp6741/course_outline.pdf"]))
        # Add Lectures
        for i in range(1, lecture_number):
            lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], i)]
            # add lecture for course
            roboProfKG.add((cn, CU.HasLecture, lec_id))
            roboProfKG.add((lec_id, RDF.type, CU.Lecture))

            # add lecture number
            roboProfKG.add((lec_id, CU.hasLectureNumber, Literal(i)))
            # roboProfKG.add((cn, CU.HasCourseEvent, lec_id))
            # Add topics, Lecture Name, description
            if row['Course number'] == '6231':
                # add Lecture Name/Title
                roboProfKG.add((lec_id, FOAF.name, Literal(lecture_titles_6231[i - 1])))
                # add course description
                roboProfKG.add((cn, TEACH.courseDescription, Literal(comp6231_description)))
            else:
                # add Lecture Name/Title
                roboProfKG.add((lec_id, FOAF.name, Literal(lecture_titles_6741[i - 1])))
                # add course description
                roboProfKG.add((cn, TEACH.courseDescription, Literal(comp6741_description)))
        
        # Add worksheets
        for worksheet in range(1, worksheets):
            if row['Course number'] == '6231':
                worksheet_id = CU[BASE_DATA_DIR+"/{}{}/Worksheet/worksheet{}.pdf".format(row['Course code'], row['Course number'], worksheet)]
                roboProfKG.add((worksheet_id, RDF.type, CU.Worksheet))
                lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], worksheet)]
                roboProfKG.add((lec_id, CU.hasLectureContent, worksheet_id))
                # roboProfKG.add((cn, CU.HasCourseEvent, lab_id))
            else:
                worksheet_id = CU[BASE_DATA_DIR+"/{}{}/Worksheet/worksheet{}.pdf".format(row['Course code'], row['Course number'], worksheet)]
                roboProfKG.add((worksheet_id, RDF.type, CU.Worksheet))
                lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], worksheet+1)]
                roboProfKG.add((lec_id, CU.hasLectureContent, worksheet_id))
        
        # add slides
        for slide in range(1, lecture_number):
            if row['Course number'] == '6231':
                slide_id = CU[BASE_DATA_DIR+"/{}{}/Slide/slide{}.pdf".format(row['Course code'], row['Course number'], slide)]
                roboProfKG.add((slide_id, RDF.type, CU.Slide))
                lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], slide)]
                roboProfKG.add((lec_id, CU.hasLectureContent, slide_id))
                # roboProfKG.add((cn, CU.HasCourseEvent, lab_id))
            else:
                slide_id = CU[BASE_DATA_DIR+"/{}{}/Slide/slide{}.pdf".format(row['Course code'], row['Course number'], slide)]
                roboProfKG.add((worksheet_id, RDF.type, CU.Worksheet))
                lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], slide)]
                roboProfKG.add((lec_id, CU.hasLectureContent, slide_id))
        # Add Outline
        # dir_name = os.path.join(BASE_DATA_DIR, "c{}content").format(row['Course number'])
        # dir_name_txt = os.path.join(BASE_DATA_DIR, "c{}content_txt").format(row['Course number'])
        # outline_path = os.path.join(dir_name, 'course_outline.pdf')
        # if os.path.isfile(outline_path):
            
        
        # Add website (Neither special courses have one in CATALOG.csv)
        # roboProfKG.add((cn, RDFS.seeAlso, URIRef("http://example.com/" + row['Course code'] + row['Course number'])))
        # Add content
        # for sub_dir in resources_dir:
        #     dir_path = os.path.join(dir_name, sub_dir)
        #     dir_path_txt = os.path.join(dir_name_txt, sub_dir)
        #     if os.path.isdir(dir_path):
        #         for idf, f in enumerate(sorted(os.listdir(dir_path))):
        #             f_path = os.path.join(dir_path, f)
        #             f_path_txt = os.path.join(dir_path_txt, f.split('.')[0] + ".txt")
        #             f_uri = CU[f_path]
        #             if sub_dir in lecture_related_events:
        #                 course_event_id = CU["{}{}{}{}".format(row['Course code'], row['Course number'], sub_dir, idf + 1)]
        #             else:
        #                 course_event_id = CU["{}{}Lec{}".format(row['Course code'], row['Course number'], idf + 1)]
        #             roboProfKG.add((f_uri, RDF.type, CU[sub_dir]))
        #             roboProfKG.add((course_event_id, CU.HasMaterial, f_uri))
                    # Extract entities of file with spotlight
                    # with open(f_path_txt, 'r') as f:
                    #     data = f.read()
                    #     result = generate_dbpedia_entities(data)
                    # for entity in result:
                    #     roboProfKG.add((f_uri, DBP.subject, URIRef(entity)))

    return roboProfKG
# def generate_dbpedia_entities(file_txt):
#     '''
#     This function generates and returns the dbpedia entities linked by spotlight of a single file.
#     Warning! Requires the spacy en_core_web_lg model. If you do not have it, run
#     python -m spacy download en_core_web_lg on your venv (~750 mb)

#     !! We will definitely need to setup a local server of spotlight. Bad HTTP responses for many access in a row !!

#     :param file_txt: txt version of a file as rendered by Apache Tika.
#     :return: List of dbpedia URIs entities
#     '''
#     doc = nlp(file_txt)
#     entities = []
#     for ent in doc.ents:
#         similarity_score = float(ent._.dbpedia_raw_result['@similarityScore'])
#         if similarity_score >= 0.75:
#             entities.append(ent.kb_id_)
#     return set(entities)

if __name__ == '__main__':
    roboProfKG = Graph()
    generateKnowledgeBase(roboProfKG)