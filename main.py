import csv
import os
from os import path

import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

# BASE_DATA_DIR = 

DBR = Namespace("http://dbpedia.org/resource/")
DBP = Namespace("http://dbpedia.org/property/")
CU = Namespace("http://is-concordia.io/")
TEACH = Namespace("http://linkedscience.org/teach/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1")

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

    roboProfKG.serialize(destination="kb.ttl", format="turtle")

def addCoreCoursesKnowledge(roboProfKG):
    '''
    Adds knowledge graph for specific courses for RoboProf.

    Parameters:
        roboProfKG (rdflib.Graph): Instance of the Graph which needs to be populated.

    Returns:
        roboProfKG (rdflib.Graph): Instance of the Graph with knowledge base for RoboProf.
    '''
    pass

if __name__ == '__main__':
    roboProfKG = Graph()
    generateKnowledgeBase(roboProfKG)