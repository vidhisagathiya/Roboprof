import csv
import os
from os import path
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF
from tika import parser
import spacy

nlp = spacy.load('en_core_web_lg')
# add the pipeline stage
nlp.add_pipe('dbpedia_spotlight', config={'dbpedia_rest_endpoint': 'http://localhost:2222/rest'})

# Define BASE_DATA_DIR
os.chdir("../Dataset")
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
            roboProfKG.add((cn, RDFS.label, Literal(row['Course code']+row['Course number'])))
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

def generateTopics(roboProfKG, cn, row, resource):
    dir_name = os.path.join(BASE_DATA_DIR, "{}{}").format(row['Course code'],row['Course number'])
    dir_name_txt = os.path.join(BASE_DATA_DIR, "{}{}_TXT").format(row['Course code'],row['Course number'])
    dir_path = os.path.join(dir_name, resource)
    dir_path_txt = os.path.join(dir_name_txt, resource)
    if os.path.isdir(dir_path):
        for idf, file in enumerate(sorted(os.listdir(dir_path))):
            id = CU["{}{}_{}#{}".format(row['Course code'], row['Course number'], resource, idf+1)]
            print(id)
            filePath = os.path.join(dir_path, file)
            filePathTxt = os.path.join(dir_path_txt, file.split('.')[0] + ".txt")
            # print(filePathTxt)
    #            if sub_dir in ['Lab', 'Worksheet']:
    #                course_event_id = CU["{}{}{}{}".format(row['Course code'], row['Course number'], sub_dir, idf + 1)]
    #            else:
    #                course_event_id = CU["{}{}Lec{}".format(row['Course code'], row['Course number'], idf + 1)]
    #            roboProfKG.add((f_uri, RDF.type, CU[sub_dir]))
    #            roboProfKG.add((course_event_id, CU.HasMaterial, f_uri))
    #            # Extract entities of file with spotlight
            with open(filePathTxt, 'r') as f:
                data = f.read()
                result = generate_dbpedia_entities(data)
                for entity, entLabel in result:
                   roboProfKG.add((URIRef(entity), RDF.type, CU.Topic))
                   roboProfKG.add((URIRef(entity), CU.hasProvenance, CU[id]))
                   roboProfKG.add((URIRef(entity), CU.hasMaterials, CU[filePath]))
                   roboProfKG.add((URIRef(entity), DBP.subject, URIRef(entity)))
                   roboProfKG.add((URIRef(entity), RDFS.label, Literal(entLabel)))
                   roboProfKG.add((URIRef(entity), FOAF.name, Literal(entLabel)))
                   roboProfKG.add((cn, CU.hasTopic, URIRef(entity)))
                   if resource == "Slide":
                        lec_id = CU["{}{}_{}#{}".format(row['Course code'], row['Course number'], "Lecture", idf+1)]
                        roboProfKG.add((lec_id, CU.topicsCovered, URIRef(entity))) # Lecture has these topics covered
                   if resource == "Lab":
                       lab_id = CU["{}{}_{}#{}".format(row['Course code'], row['Course number'], "Lab", idf+1)]
                       roboProfKG.add((lab_id, CU.topicsCovered, URIRef(entity))) # Lab has these topics covered
                    



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
        labs = 11
        outline_path = os.path.join(current_directory, "Dataset", "COMP6231", "course_outline.pdf")
    else:
        lecture_number = 9
        worksheets = 8
        labs = 11
        outline_path = os.path.join(current_directory, "Dataset", "COMP6741", "course_outline.pdf")

    roboProfKG.add((cn, CU.hasCourseOutline, URIRef(outline_path)))
    # Add Lectures
    # topic_index = 0
    # num_topics_per_lecture = len(TOPIC_TITLES_6231) // lecture_number
    for i in range(1, lecture_number):
        lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], i)]
        # add lecture for course
        roboProfKG.add((lec_id, RDF.type, CU.Lecture))
        # add lecture number
        roboProfKG.add((lec_id, CU.hasLectureNumber, Literal(i)))
        roboProfKG.add((cn, CU.hasLecture, lec_id))
        # Add topics, Lecture Name, description
        if row['Course number'] == '6231':
            # add Lecture Name/Title
            # roboProfKG.add((lec_id, FOAF.name, Literal(LEC_TITLES_6231[i - 1])))
            # add course description
            roboProfKG.add((cn, TEACH.courseDescription, Literal(COMP6231_DESC)))
            # for topic in TOPIC_TITLES_6231[topic_index:topic_index+num_topics_per_lecture]:
            #     roboProfKG.add((lec_id, CU.topicsCovered, CU[topic]))
        else:
            # add Lecture Name/Title
            # roboProfKG.add(
            #     (lec_id, FOAF.name, Literal(LEC_TITLES_6741[i - 1])))
            # add course description
            roboProfKG.add((cn, TEACH.courseDescription,
                           Literal(COMP6741_DESC)))
            # for topic in TOPIC_TITLES_6741[topic_index:topic_index+num_topics_per_lecture]:
            #     roboProfKG.add((lec_id, CU.topicsCovered, CU[topic]))
        # topic_index += num_topics_per_lecture
    generateTopics(roboProfKG, cn, row, "Lecture")
    roboProfKG.add((cn, CU.hasCourseEvent, Literal("Lecture")))
    # if row['Course number'] == '6231':
    #     if topic_index < len(TOPIC_TITLES_6231):
    #             for topic in TOPIC_TITLES_6231[topic_index:]:
    #                 roboProfKG.add((lec_id, CU.topicsCovered, CU[topic]))
    # Add worksheets
    for worksheet in range(1, worksheets):
        worksheet_id = CU["{}{}_Worksheet#{}".format(row['Course code'], row['Course number'], worksheet)]
        worksheet_path = os.path.join(current_directory, "Dataset", row['Course code']+row['Course number'], "Worksheet", "worksheet{}.pdf".format(worksheet))
        roboProfKG.add((worksheet_id, RDF.type, CU.Worksheet))
        roboProfKG.add((worksheet_id, RDFS.seeAlso, URIRef(worksheet_path)))
        lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], worksheet)]
        roboProfKG.add((lec_id, CU.hasLectureContent, worksheet_id))        
    generateTopics(roboProfKG, cn, row, "Worksheet")

    # add slides
    for slide in range(1, lecture_number):
        slide_id = CU["{}{}_Slide#{}".format(row['Course code'], row['Course number'], slide)]
        slide_path = os.path.join(current_directory, "Dataset", row['Course code']+row['Course number'], "Slide", "slide{}.pdf".format(slide))
        roboProfKG.add((slide_id, RDF.type, CU.Slide))
        roboProfKG.add((slide_id, RDFS.seeAlso, URIRef(slide_path)))
        lec_id = CU["{}{}_Lecture#{}".format(row['Course code'], row['Course number'], slide)]
        roboProfKG.add((lec_id, CU.hasLectureContent, slide_id))
    generateTopics(roboProfKG, cn, row, "Slide")

    # add labs
    for lab in range(1, labs):
        lab_id = CU["{}{}_Lab#{}".format(row['Course code'], row['Course number'], lab)]
        lab_path = os.path.join(current_directory, "Dataset", row['Course code']+row['Course number'],  "Lab", "Lab{}.pdf".format(lab))
        roboProfKG.add((lab_id, RDF.type, CU.Lab))
        roboProfKG.add((cn, CU.hasLab, lab_id))
        roboProfKG.add((lab_id, CU.hasLabNumber, Literal(lab)))
        roboProfKG.add((lab_id, RDFS.seeAlso, URIRef(lab_path)))
    generateTopics(roboProfKG, cn, row, "Lab")
    roboProfKG.add((cn, CU.hasCourseEvent, Literal("Lab")))
    
        # open the .txt file -> get all the topics linked to dbpedia -> add it to triple. Add the provenence as the worksheet
    # add topics to courses
    # if row['Course number'] == '6231':
    #     for topic in TOPIC_TITLES_6231:
    #         roboProfKG.add((CU[topic], RDF.type, CU.Topic))
    #         roboProfKG.add((CU[topic], FOAF.name, Literal(topic)))
    #         roboProfKG.add((CU[topic], RDFS.seeAlso, DBR[topic]))
    #         roboProfKG.add((CU[topic], RDFS.label, Literal(" ".join(topic.split("_")))))
    #         roboProfKG.add((cn, CU.hasTopic, CU[topic]))
    #         roboProfKG.add((CU[topic], CU.hasMaterials, Literal("https://www.mongodb.com/docs/manual/sharding/")))
    # else:
    #     for topic in TOPIC_TITLES_6741:
    #         roboProfKG.add((CU[topic], RDF.type, CU.Topic))
    #         roboProfKG.add((CU[topic], FOAF.name, Literal(topic)))
    #         roboProfKG.add((CU[topic], RDFS.seeAlso, DBR[topic]))
    #         roboProfKG.add((CU[topic], RDFS.label, Literal(" ".join(topic.split("_")))))
    #         roboProfKG.add((cn, CU.hasTopic, CU[topic]))
    #         roboProfKG.add((CU[topic], CU.hasMaterials, Literal("https://www.ibm.com/topics/machine-learning")))

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

def generateTXTFromPDF():
    for course in ["COMP6231", "COMP6741"]:
        base_dir = os.path.join(BASE_DATA_DIR, f"{course}")
        txt_dir = os.path.join(BASE_DATA_DIR, f"{course}" + "_TXT")

        base_outline = os.path.join(base_dir, 'course_outline.pdf')
        txt_outline = os.path.join(txt_dir, 'course_outline.txt')

        if os.path.isfile(base_outline) and not os.path.isfile(txt_outline) :
            file_data = parser.from_file(base_outline)

            # get the content of the pdf file
            output = file_data['content'].strip().replace('\n', '')

            # convert it to utf-8
            output = output.encode('utf-8', errors='ignore')
            # save it
            with open(txt_outline, 'w') as f:
                f.write(str(output))

        # Add content
        for sub_dir in ["Slide", "Worksheet", "Lab", "Reading"]:
            base_subdir = os.path.join(base_dir, sub_dir)
            if not os.path.exists(base_subdir):
                continue
            txt_subdir = os.path.join(txt_dir, sub_dir)
            for idf, f in enumerate(sorted(os.listdir(base_subdir))):
                output_path = os.path.join(txt_subdir, f.split(".")[0] + ".txt")
                # if we have already generated that file, continue
                if os.path.isfile(output_path):
                    continue

                file_data = parser.from_file(os.path.join(base_subdir, f))
                # get the content of the pdf file
                output = file_data['content'].strip().replace('\n', '')

                # convert it to utf-8
                # output = output.encode('utf-8', errors='ignore')
                # save it
                with open(os.path.join(txt_subdir, f.split(".")[0] + ".txt"), 'w') as f:
                    f.write(str(output))

def generate_dbpedia_entities(fileData):
    '''
    This function generates and returns the dbpedia entities linked by spotlight of a single file.
    Warning! Requires the spacy en_core_web_lg model. If you do not have it, run
    python -m spacy download en_core_web_lg on your venv (~750 mb)

    !! We will definitely need to setup a local server of spotlight. Bad HTTP responses for many access in a row !!

    :param file_txt: txt version of a file as rendered by Apache Tika.
    :return: List of dbpedia URIs entities
    '''
    # ner_categories = ["PERSON", "ORG", "GPE", "PRODUCT" ]
    doc = nlp(fileData)
    entities = []
    for ent in doc.ents:
        if eval(ent._.dbpedia_raw_result['@similarityScore']) >= 0.75:# and (ent. label_ in ner_categories):
            entities.append((ent.kb_id_, ent))
    # print(set(entities))
    return set(entities)


def generate_directories():
    '''
    Generates a directory structure that mirrors all the course content directories with as txt files.
    :return: None
    '''
    for course in ["COMP6231", "COMP6741"]:
        dir_name = os.path.join(BASE_DATA_DIR, f"{course}")
        if os.path.exists(dir_name) and not os.path.exists(dir_name + "_TXT"):
            txt_dir = dir_name + "_TXT"
            os.mkdir(txt_dir)
        else:
            continue

        for sub_dir in ["Slide", "Worksheet", "Lab", "Reading"]:
            dir_path = os.path.join(dir_name, sub_dir)
            if os.path.exists(dir_path) and not os.path.exists(os.path.join(txt_dir, sub_dir)):
                txt_subdir = os.path.join(txt_dir, sub_dir)
                os.mkdir(txt_subdir)
            else:
                continue


if __name__ == '__main__':
    roboProfKG = Graph()
    # generate_directories()
    # generateTXTFromPDF()
    generateKnowledgeBase(roboProfKG)