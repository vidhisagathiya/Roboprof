import csv
import os
from os import path
import spacy  # Added import for spaCy

import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

# Define BASE_DATA_DIR
BASE_DATA_DIR = '/path/to/your/base/data/directory'  # Change this to your actual directory

DBR = Namespace("http://dbpedia.org/resource/")
DBP = Namespace("http://dbpedia.org/property/")
CU = Namespace("http://is-concordia.io/")
TEACH = Namespace("http://linkedscience.org/teach/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1")

# Initialize spaCy language model
nlp = spacy.load("en_core_web_lg")


special_courses = [URIRef("http://a1.io/data#SOEN6231"), URIRef("http://a1.io/data#COMP6741")]
special_course_codes = ['6231', '6741']
special_courses_websites = [URIRef("http://concordia.catalog.acalog.com/preview_course_nopop.php?catoid=1&coid=2703"),
                            URIRef("http://concordia.catalog.acalog.com/preview_course_nopop.php?catoid=1&coid=2718")]

# All titles are dbpedia resources
lecture_titles_6231 = ['Construction_and_Analysis_of_Distributed_Processes', 'Virtual_machine', 'Programming_paradigm',
                      'Transition_(computer_science)', 'Message-oriented_middleware', 'Thread_(computing)',
                      'Category:Distributed_computing_architecture', 'Distributed_database', 'Fault_tolerance', 
                      'Consistency_(database_systems)', 'Replication_(computing)', 'Distributed_algorithm', 'Synchronization_(computer_science)', 'Domain_Name_System']

lecture_titles_6741 = ['Intelligent_system', 'Knowledge_graph', 'Ontology_(information_science)',
                      'SPARQL', 'Knowledge_base', 'Recommender_system', 'Machine_learning',
                      'Intelligent_agent', 'Text_mining']

# This could be retrieved by web-crawling, but assignment description makes no mention of that
soen6231_description = "Introduction to database management systems. Conceptual database design: the " \
                      "entity‑relationship model. The relational data model and relational algebra: functional " \
                      "dependencies and normalization. The SQL language and its application in defining, querying, " \
                      "and updating databases; integrity constraints; triggers. Developing database applications. "
comp6741_description = "Rule‑based expert systems, blackboard architecture, and agent‑based. Knowledge acquisition and " \
                      "representation. Uncertainty and conflict resolution. Reasoning and explanation. Design of " \
                      "intelligent systems. "

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
            # if cn not in special_courses:
            #     g.add((cn, TEACH.courseDescription, Literal(row['Description'])))
            if row['Website'] != "":
                roboProfKG.add((cn, RDFS.seeAlso, Literal(row['Website'])))
            addCoreCoursesKnowledge(roboProfKG)

    roboProfKG.serialize(destination="kb.ttl", format="turtle")
    roboProfKG.serialize(destination="kb_ntriples.rdf", format="ntriples")           

def addCoreCoursesKnowledge(roboProfKG):
    '''
    Adds knowledge graph for specific courses for RoboProf.

    Parameters:
        roboProfKG (rdflib.Graph): Instance of the Graph which needs to be populated.

    Returns:
        roboProfKG (rdflib.Graph): Instance of the Graph with knowledge base for RoboProf.
    '''
    with open('CLEANED_DATA.csv', 'r') as data:  # Open CSV file
        r = csv.DictReader(data)
        for row in r:
            course_num = str(row['Course number']).split()[0]
            # print(course_num)
            # print(course_num[0])
            cn = URIRef("http://is-concordia.io/" + row['Course code'] + course_num)
            if cn in special_courses:
                if row['Course number'] == '6231':
                    lecture_number = 11
                else:
                    lecture_number = 7

                for i in range(1, lecture_number):
                    # Add Lectures
                    lec_id = CU["{}{}Lec{}".format(row['Course code'], row['Course number'], i)]
                    roboProfKG.add((cn, CU.HasLecture, lec_id))
                    roboProfKG.add((lec_id, RDF.type, CU.Lecture))
                    roboProfKG.add((lec_id, CU.LectureNumber, Literal(i)))
                    roboProfKG.add((cn, CU.HasCourseEvent, lec_id))

                    # Add topics, Lecture Name, description
                    if row['Course number'] == '353':
                        roboProfKG.add((lec_id, TEACH.hasTitle, Literal(lecture_titles_6231[i - 1])))
                        roboProfKG.add((cn, TEACH.courseDescription, Literal(soen6231_description)))
                    else:
                        roboProfKG.add((lec_id, TEACH.hasTitle, Literal(lecture_titles_6741[i - 1])))
                        roboProfKG.add((cn, TEACH.courseDescription, Literal(comp6741_description)))

                    # Add Labs
                    lab_id = CU["{}{}Lab{}".format(row['Course code'], row['Course number'], i)]
                    roboProfKG.add((lab_id, RDF.type, CU.Lab))
                    roboProfKG.add((lab_id, CU.RelatedToLecture, lec_id))
                    roboProfKG.add((cn, CU.HasCourseEvent, lab_id))

                # Add Outline
                dir_name = os.path.join(BASE_DATA_DIR, "c{}content").format(row['Course number'])
                dir_name_txt = os.path.join(BASE_DATA_DIR, "c{}content_txt").format(row['Course number'])
                outline_path = os.path.join(dir_name, 'Outline.pdf')
                if os.path.isfile(outline_path):
                    roboProfKG.add((cn, CU.Outline, CU[outline_path]))

                # Add website (Neither special courses have one in CATALOG.csv)
                roboProfKG.add((cn, RDFS.seeAlso, URIRef("http://example.com/" + row['Course code'] + row['Course number'])))

                # Add content
                for sub_dir in resources_dir:
                    dir_path = os.path.join(dir_name, sub_dir)
                    dir_path_txt = os.path.join(dir_name_txt, sub_dir)
                    if os.path.isdir(dir_path):
                        for idf, f in enumerate(sorted(os.listdir(dir_path))):
                            f_path = os.path.join(dir_path, f)
                            f_path_txt = os.path.join(dir_path_txt, f.split('.')[0] + ".txt")
                            f_uri = CU[f_path]
                            if sub_dir in lecture_related_events:
                                course_event_id = CU["{}{}{}{}".format(row['Course code'], row['Course number'], sub_dir, idf + 1)]
                            else:
                                course_event_id = CU["{}{}Lec{}".format(row['Course code'], row['Course number'], idf + 1)]
                            roboProfKG.add((f_uri, RDF.type, CU[sub_dir]))
                            roboProfKG.add((course_event_id, CU.HasMaterial, f_uri))

                            # Extract entities of file with spotlight
                            with open(f_path_txt, 'r') as f:
                                data = f.read()
                                result = generate_dbpedia_entities(data)
                            for entity in result:
                                roboProfKG.add((f_uri, DBP.subject, URIRef(entity)))

def generate_dbpedia_entities(file_txt):
    '''
    This function generates and returns the dbpedia entities linked by spotlight of a single file.
    Warning! Requires the spacy en_core_web_lg model. If you do not have it, run
    python -m spacy download en_core_web_lg on your venv (~750 mb)

    !! We will definitely need to setup a local server of spotlight. Bad HTTP responses for many access in a row !!

    :param file_txt: txt version of a file as rendered by Apache Tika.
    :return: List of dbpedia URIs entities
    '''
    doc = nlp(file_txt)
    entities = []
    for ent in doc.ents:
        similarity_score = float(ent._.dbpedia_raw_result['@similarityScore'])
        if similarity_score >= 0.75:
            entities.append(ent.kb_id_)
    return set(entities)

if __name__ == '__main__':
    roboProfKG = Graph()
    generateKnowledgeBase(roboProfKG)