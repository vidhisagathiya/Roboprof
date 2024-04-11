import csv
import os
from os import path
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF

# Define BASE_DATA_DIR
BASE_DATA_DIR = os.getcwd()
current_directory = os.path.dirname(BASE_DATA_DIR)

CU = Namespace("http://is-concordia.io/")
DBR = Namespace("http://dbpedia.org/resource/")
DBP = Namespace("http://dbpedia.org/property/")
TEACH = Namespace("http://linkedscience.org/teach/ns#")

TOPIC_TITLES_6231 = [
    'Construction_and_Analysis_of_Distributed_Processes',
    'Virtual_machine',
    'Programming_paradigm',
    'Transition_(computer_science)',
    'Message-oriented_middleware',
    'Thread_(computing)',
    'Category:Distributed_computing_architecture',
    'Distributed_database',
    'Fault_tolerance',
    'Consistency_(database_systems)',
    'Replication_(computing)',
    'Distributed_algorithm',
    'Synchronization_(computer_science)',
    'Domain_Name_System',
    'Decentralization',
    'Parallel_computing',
    'Grid_computing',
    'Cloud_computing',
    'Scalability',
    'High_availability',
    'Load_balancing_(computing)',
    'Cluster_computing',
    'Peer-to-peer',
    'Message_queue',
    'Concurrency_control',
    'Distributed_lock_manager',
    'Distributed_transaction',
    'Distributed_file_system',
    'Distributed_shared_memory',
    'Network_topology',
    'Overlay_network',
    'Inter-process_communication',
    'Routing_protocol',
    'Wireless_sensor_network',
    'Fault-tolerant_design',
    'Consensus_algorithm',
    'Clock_synchronization',
    'Data_replication',
    'Replication_protocol',
    'Replica_placement',
    'State_machine_replication',
    'Recovery-oriented_computing',
    'Transaction_processing',
    'Transactional_memory',
    'Database_shard',
    'Sharding',
    'Partitioning_(database)',
    'Data_partitioning',
    'Horizontal_scaling',
    'Vertical_scaling',
    'Edge_computing',
    'Fog_computing',
    'Mobile_edge_computing',
    'Content_delivery_network',
    'Distributed_hash_table',
    'Consistent_hashing',
    'Content_addressable_network',
    'Distributed_resource_scheduler',
    'Service_oriented_architecture',
]


TOPIC_TITLES_6741 = [
    'Artificial_intelligence',
    'Machine_learning',
    'Expert_system',
    'Knowledge_representation',
    'Natural_language_processing',
    'Robotics',
    'Neural_network_software',
    'Genetic_algorithm',
    'Reinforcement_learning',
    'Cognitive_computing',
    'Deep_learning',
    'Pattern_recognition',
    'Data_mining',
    'Automated_decision_support',
    'Intelligent_agent',
    'Logic_programming',
    'Ontology_learning',
    'Swarm_robotics',
    'Semantic_web',
    'Knowledge_engineering',
    'Inference_engine',
    'Expert_system_shell',
    'Planning_algorithm',
    'Evolutionary_computation',
    'Bayesian_network',
    'Markov_decision_process',
    'Hierarchical_temporal_memory',
    'Automated_planning',
    'Swarm_intelligence',
    'Case-based_reasoning',
    'Reasoning_system',
    'Genetic_programming',
    'Machine_perception',
    'Cognitive_architecture',
    'Automated_reasoning',
    'Computational_intelligence',
    'Knowledge_graph',
    'Intelligent_control',
    'Probabilistic_reasoning',
    'Fuzzy_logic',
    'Cognitive_system',
    'Autonomous_robot',
    'Multi-agent_system',
    'Expert_system_development_tool',
    'Ontology_alignment',
    'Automated_planning_and_scheduling',
    'Neural_network_modeling',
    'Swarm_behaviour',
    'Neuroevolution',
    'Deep_belief_network'
]

CORE_COURSES = [URIRef("http://is-concordia.io/COMP6231"),
                   URIRef("http://is-concordia.io/COMP6741")]

# All titles are dbpedia resources
LEC_TITLES_6231 = ['Construction_and_Analysis_of_Distributed_Processes', 'Virtual_machine', 'Programming_paradigm',
                       'Transition_(computer_science)', 'Message-oriented_middleware', 'Thread_(computing)',
                       'Category:Distributed_computing_architecture', 'Distributed_database', 'Fault_tolerance',
                       'Consistency_(database_systems)', 'Replication_(computing)', 'Distributed_algorithm', 'Synchronization_(computer_science)', 'Domain_Name_System']

LEC_TITLES_6741 = ['Intelligent_system', 'Knowledge_graph', 'Ontology_(information_science)',
                       'SPARQL', 'Knowledge_base', 'Recommender_system', 'Machine_learning',
                       'Intelligent_agent', 'Text_mining']


COMP6231_DESC = "Principles of distributed computing: scalability, transparency, concurrency, consistency, fault tolerance. Client-server interaction technologies: interprocess communication, sockets, group communication, remote procedure call, remote method invocation, object request broker, CORBA, web services. Distributed server design techniques: process replication, fault tolerance through passive replication, high availability through active replication, coordination and agreement transactions and concurrency control. Designing software fault-tolerant highly available distributed systems using process replication. Laboratory: two hours per week."
COMP6741_DESC = "(COMP 474): Rule-based expert systems, blackboard architecture, and agent-based. Knowledge acquisition and representation. Uncertainty and conflict resolution. Reasoning and explanation. Design of intelligent systems. Project. (COMP 6741): Knowledge representation and reasoning. Uncertainty and conflict resolution. Design of intelligent systems. Grammar-based, rule-based, and blackboard architectures. A project is required."

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
    roboProfKG.add((CU.Concordia_University, FOAF.name,
                   Literal("Concordia University")))
    roboProfKG.add((CU.Concordia_University, RDFS.seeAlso,
                   DBR.Concordia_University))
    
    # Construct the path to the CSV file in the Dataset folder
    dataset_path = os.path.join(current_directory, "Dataset", "CLEANED_DATA.csv")

    with open(dataset_path, 'r') as data:
        r = csv.DictReader(data)
        for row in r:
            # Create the course
            course_num = str(row['Course number']).split()[0]
            cn = URIRef("http://is-concordia.io/" +
                        row['Course code'] + course_num)
            roboProfKG.add((cn, RDF.type, CU.Course))

            # Add to list of offered courses at Concordia
            roboProfKG.add((CU.Concordia_University, CU.Offers, cn))

            # Add course details
            roboProfKG.add((cn, TEACH.courseTitle, Literal(row['Title'])))
            roboProfKG.add((cn, CU.hasCourseSubject, Literal(row['Course code'])))
            roboProfKG.add((cn, CU.hasCourseNumber, Literal(row['Course number'])))
            roboProfKG.add((cn, CU.hasCredits, Literal(row['Class Units'])))
            if cn not in CORE_COURSES:
                roboProfKG.add((cn, TEACH.courseDescription,
                               Literal(row['Description'])))
            else:
                roboProfKG = addCoreCoursesKnowledge(roboProfKG, row, cn)

            if row['Website'] != "":
                roboProfKG.add((cn, RDFS.seeAlso, Literal(row['Website'])))
    roboProfKG = addStudentsToKnowledgeBase(roboProfKG)

    save_path_ttl = os.path.join(current_directory, "Knowledge Base", "kb.ttl")
    save_path_rdf = os.path.join(current_directory, "Knowledge Base", "kb_ntriples.rdf")
    roboProfKG.serialize(destination=save_path_ttl, format="turtle")
    roboProfKG.serialize(destination=save_path_rdf, format="ntriples")


def addCoreCoursesKnowledge(roboProfKG, row, cn):
    '''
    Adds knowledge graph for specific courses for RoboProf.

    Parameters:
        roboProfKG (rdflib.Graph): Instance of the Graph which needs to be populated.

    Returns:
        roboProfKG (rdflib.Graph): Instance of the Graph with knowledge base for RoboProf.
    '''
    if row['Course number'] == '6231':
        lecture_number = 11
        worksheets = 11
        outline_path = os.path.join(current_directory, "Dataset", "COMP6231", "course_outline.pdf")
    else:
        lecture_number = 9
        worksheets = 8
        outline_path = os.path.join(current_directory, "Dataset", "COMP6741", "course_outline.pdf")

    roboProfKG.add((cn, CU.hasCourseOutline, URIRef(outline_path)))
    # Add Lectures
    topic_index = 0
    num_topics_per_lecture = len(TOPIC_TITLES_6231) // lecture_number
    for i in range(1, lecture_number):
        lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], i)]
        # add lecture for course
        roboProfKG.add((cn, CU.hasLecture, lec_id))
        roboProfKG.add((lec_id, RDF.type, CU.Lecture))
        # add lecture number
        roboProfKG.add((lec_id, CU.hasLectureNumber, Literal(i)))
        # Add topics, Lecture Name, description
        if row['Course number'] == '6231':
            # add Lecture Name/Title
            roboProfKG.add((lec_id, FOAF.name, Literal(LEC_TITLES_6231[i - 1])))
            # add course description
            roboProfKG.add((cn, TEACH.courseDescription,Literal(COMP6231_DESC)))
            for topic in TOPIC_TITLES_6231[topic_index:topic_index+num_topics_per_lecture]:
                roboProfKG.add((lec_id, CU.topicsCovered, CU[topic]))
        else:
            # add Lecture Name/Title
            roboProfKG.add(
                (lec_id, FOAF.name, Literal(LEC_TITLES_6741[i - 1])))
            # add course description
            roboProfKG.add((cn, TEACH.courseDescription,
                           Literal(COMP6741_DESC)))
            for topic in TOPIC_TITLES_6741[topic_index:topic_index+num_topics_per_lecture]:
                roboProfKG.add((lec_id, CU.topicsCovered, CU[topic]))
        topic_index += num_topics_per_lecture

    if row['Course number'] == '6231':
        if topic_index < len(TOPIC_TITLES_6231):
                for topic in TOPIC_TITLES_6231[topic_index:]:
                    roboProfKG.add((lec_id, CU.topicsCovered, CU[topic]))
    # Add worksheets
    for worksheet in range(1, worksheets):
        if row['Course number'] == '6231':
            worksheet_path = os.path.join(current_directory, "Dataset", "Comp6231", "Worksheet", "worksheet{}.pdf".format(worksheet))
            worksheet_id = URIRef(worksheet_path)
            roboProfKG.add((worksheet_id, RDF.type, CU.Worksheet))
            lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], worksheet)]
            roboProfKG.add((lec_id, CU.hasLectureContent, worksheet_id))
        else:
            worksheet_path = os.path.join(current_directory, "Dataset", "Comp6231", "Worksheet", "worksheet{}.pdf".format(worksheet))
            worksheet_id = URIRef(worksheet_path)
            roboProfKG.add((worksheet_id, RDF.type, CU.Worksheet))
            lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], worksheet)]
            roboProfKG.add((lec_id, CU.hasLectureContent, worksheet_id))

        # add slides
    for slide in range(1, lecture_number):
        if row['Course number'] == '6231':
            slide_path = os.path.join(current_directory, "Dataset", "Comp6231", "Slide", "slide{}.pdf".format(slide))
            slide_id = URIRef(slide_path)
            roboProfKG.add((slide_id, RDF.type, CU.Slide))
            lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], slide)]
            roboProfKG.add((lec_id, CU.hasLectureContent, slide_id))

        else:
            slide_path = os.path.join(current_directory, "Dataset", "COMP6741",  "Slide", "slide{}.pdf".format(slide))
            slide_id = URIRef(slide_path)
            roboProfKG.add((slide_id, RDF.type, CU.Slide))
            lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], slide)]
            roboProfKG.add((lec_id, CU.hasLectureContent, slide_id))

    # add topics to courses
    if row['Course number'] == '6231':
        for topic in TOPIC_TITLES_6231:
            roboProfKG.add((CU[topic], RDF.type, CU.Topic))
            roboProfKG.add((CU[topic], FOAF.name, Literal(topic)))
            roboProfKG.add((CU[topic], RDFS.seeAlso, DBR[topic]))
            roboProfKG.add((cn, CU.hasTopic, CU[topic]))
            roboProfKG.add((CU[topic], CU.hasMaterials, Literal("https://www.mongodb.com/docs/manual/sharding/")))
    else:
        for topic in TOPIC_TITLES_6741:
            roboProfKG.add((CU[topic], RDF.type, CU.Topic))
            roboProfKG.add((CU[topic], FOAF.name, Literal(topic)))
            roboProfKG.add((CU[topic], RDFS.seeAlso, DBR[topic]))
            roboProfKG.add((cn, CU.hasTopic, CU[topic]))
            roboProfKG.add((CU[topic], CU.hasMaterials, Literal("https://www.ibm.com/topics/machine-learning")))

    return roboProfKG

def addCompetencies(roboProfKG, course, student):
    """
    Add competencies based on completed courses for students.
    """
    if course == "COMP6231":
        for topic in TOPIC_TITLES_6231:
            roboProfKG.add((CU[student], CU.hasCompetency, CU[topic]))
    else:        
        for topic in TOPIC_TITLES_6741:
            roboProfKG.add((CU[student], CU.hasCompetency, CU[topic]))

    return roboProfKG

def addStudentsToKnowledgeBase(roboProfKG):
    roboProfKG.add((CU["Nilesh"], RDF.type, CU.Student))
    roboProfKG.add((CU["Nilesh"], FOAF.name, Literal("Nilesh")))
    roboProfKG.add((CU["Nilesh"], CU.hasStudentID, Literal("40229633")))
    roboProfKG.add((CU["Nilesh"], CU.hasStudentEmail, Literal(
        "nilesh.suryawanshi@mail.concordia.ca")))
    roboProfKG.add((CU["Nilesh"], CU.isEnrolledIn, CU.COMP6231))
    roboProfKG.add((CU["Nilesh"], CU.isEnrolledIn, CU.COMP6741))
    roboProfKG.add((CU["Nilesh"], CU.COMP6231, Literal("A")))
    for topic in TOPIC_TITLES_6231:
            roboProfKG.add((CU["Nilesh"], CU.hasCompetency, CU[topic]))
    roboProfKG.add((CU["Nilesh"], CU.COMP6741, Literal("C")))
    roboProfKG.add((CU["Nilesh"], CU.COMP6741, Literal("B")))
    

    roboProfKG.add((CU["John"], RDF.type, CU.Student))
    roboProfKG.add((CU["John"], FOAF.name, Literal("John")))
    roboProfKG.add((CU["John"], CU.isEnrolledIn, CU.COMP6741))
    roboProfKG.add((CU["John"], CU.COMP6741, Literal("A")))
    

    roboProfKG.add((CU["Vidhi"], RDF.type, CU.Student))
    roboProfKG.add((CU["Vidhi"], FOAF.name, Literal("Vidhi")))
    roboProfKG.add((CU["Vidhi"], CU.hasStudentID, Literal("40232374")))
    roboProfKG.add((CU["Vidhi"], CU.isEnrolledIn, CU.COMP6741))
    roboProfKG.add((CU["Vidhi"], CU.COMP6741, Literal("A")))

    roboProfKG.add((CU["Jane"], RDF.type, CU.Student))
    roboProfKG.add((CU["Jane"], FOAF.name, Literal("Jane")))
    roboProfKG.add((CU["Jane"], CU.isEnrolledIn, CU.COMP6741))

    return roboProfKG


if __name__ == '__main__':
    roboProfKG = Graph()
    generateKnowledgeBase(roboProfKG)