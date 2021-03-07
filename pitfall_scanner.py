from ontology import *
from helper import *
from glob import glob
import os

def sort_compare(key):
	importance_dict = {"High": 3, "Medium": 2, "Low": 1 }
	return importance_dict[key[0]]

class PitfallScanner():
	"""docstring for PitfallScanner"""
	def __init__(self, ontology_path, pitfalls):
		self.ontology = Ontology(ontology_path)
		self.pitfalls = pitfalls
		
		self.subject_to_element = {
			"Ontology Header": {"Elements": ["rdf:RDF"]},
			"Ontology Metadata": {"Elements": ["owl:Ontology"]},
			"All Elements": {"Elements": ["owl:Class", "owl:NamedIndividual", "owl:Thing", "owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty", "rdfs:subclassOf"]},
			"Classes": {"Elements": ["owl:Class"]}, 
			"Instances": {"Elements": ["owl:NamedIndividual", "owl:Thing"]},
			"Relations": {"Elements": ["owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty", "rdfs:subclassOf"]},
			"Subclass Relations": {"Elements": ["rdfs:subclassOf"]},
			"Properties": {"Elements": ["owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty"]},
			"Object Properties": {"Elements": ["owl:ObjectProperty"]},
			"Datatype Properties": {"Elements": ["owl:DatatypeProperty"]},
			"Functional Properties": {"Elements": ["owl:ObjectProperty"]},
			"Inverse Functional Properties": {"Elements": ["owl:DatatypeProperty"]},
			"Symmetric Properties": {"Elements": ["owl:ObjectProperty"], "Mappable": self.ontology.check_child_attribute,  "Arguments": [("rdfs:type", "SymmetricProperty")]},
			"Transitive Properties": {"Elements": ["owl:ObjectProperty"], "Mappable": self.ontology.check_child_attribute,  "Arguments": [("rdfs:type", "TransitiveProperty")]}
		}

		self.predicate_to_function = {
			"Has Child Element": extract_child_element,
			"Has Attribute": extract_attribute,
			"Has File Extension": extract_extension,
			"Maps to Element of Type": extract_corresponding_element,
			"Uses Comparative Operator": execute_comparison,
			"Uses Conjunctive Operator": execute_conjunction,
			"Has Logical Property": execute_logical_relation,
			"Has Linguistic Property": execute_linguistic_relation 
		}

		self.object_to_element = {
			"License": {"Elements": ["terms:license"]},
			"Label": {"Elements": ["rdfs:label"]}, 
			"Type": {"Elements": ["rdf:type"]},
			"Domain": {"Elements": ["rdfs:domain"]},
			"Range": {"Elements": ["rdfs:range"]},
			"Subclass": {"Elements": ["rdfs:subclassOf"]},
			"Annotation": {"Elements": ["rdfs:label", "lemon:LexicalEntry", "skos:prefLabel", "skos:altLabel", "rdfs:comment", "dc:description"]},
			"Is Relation": {"Elements": ["is"]},
			"Inverse Relation": {"Elements": ["owl:inverseOf"]},
			"Equivalent Property": {"Elements": ["owl:equivalentProperty"]},
			"Equivalent Class": {"Elements": ["owl:equivalentClass"]},
			"Disjoint Class": {"Elements": ["owl:disjointWith"]},
			"Property Chain Axiom": {"Elements": ["owl:propertyChainAxiom"]},
			"Language": {"Elements": ["xml:lang"]},
			"ID": {"Elements": ["rdf:ID", "rdf:resource", "rdf:about"]},
			"Defined Namespace": {"Elements": ["xml:base"]},
			"Used Namespace": {"Elements": ["rdf:ID", "rdf:resource", "rdf:about"], "Mappable": self.ontology.extract_namespace, "Arguments": []},
			"Ontology(.owl/.rdf/.xml)": {"Elements": ["owl","rdf", "xml"]},
			"Element": {"Elements": ["owl:Class", "owl:NamedIndividual", "owl:Thing", "owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty", "rdfs:subclassOf"]},
			"Class": {"Elements": ["owl:Class"]}, 
			"Instance": {"Elements": ["owl:NamedIndividual", "owl:Thing"]},
			"Property": {"Elements": ["owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty", "rdfs:subclassOf"]},
			"Other": {"Elements": []}
		}

		self.operator_to_function = {
			"Equality": equality,
			"Inequality": inequality,
			"Synonymy": synonymy,
			"Inverse": inverse,
			"And": and_operator,
			"Or": or_operator
		}

		self.property_to_function = {
			"Text Validity": text_validity, 
			"ID Consistency": id_consistency,
			"Text Symmetry": text_symmetry,
			"Uniqueness": uniqueness,
			"Contains Polysemes": contains_polysemes, 
			"Contains Conjunctions": contains_conjunctions, 
			"Contains Misc items": contains_misc_items
		}

		self.criticality_to_element = {"Critical": "High", "Intermediate": "Medium", "Minor": "Low"}

	def parse(self, result, start, end):
		for i in range(start, end):
			curr_pred, curr_obj = self.pred_obj_list[i]
			if curr_obj in self.object_to_element:
				mapped_object, mapped_subject, statement_type = self.object_to_element.get(curr_obj, ""), result, "Extractive"
			elif curr_obj in self.operator_to_function:
				mapped_object, mapped_subject, statement_type = self.operator_to_function.get(curr_obj, ""), self.parse(result, start+1, end), "Comparative"
			elif curr_obj in self.property_to_function:
				mapped_object, mapped_subject, statement_type = self.property_to_function.get(curr_obj, ""), result, "Functional"
			else:
				print ("{} is not a recognised value for object.".format(curr_obj))
				continue

			mapped_pred = self.predicate_to_function.get(curr_pred, "")
			if not mapped_pred:
				print ("{} is not a recognised value for predicate.".format(curr_pred))
				continue

			if statement_type == "Comparative":
				result = mapped_pred()
			elif statement_type

			[mapped_pred(elem) if elem else False for elem in mapped_subject]


	def scan(self):
		results = []
		for pitfall in self.pitfalls:
			Subject, Predicate, Object, Criticality = pitfall
			mapped_subject = self.subject_to_element.get(Subject, "")
			if not mapped_subject:
				print ("{} is not a recognised value for subject.".format(Subject))
				continue
			self.subject_elements = self.ontology.get_elements(mapped_subject)
			self.pred_obj_list = list(zip(Predicate, Object))
			self.parse(0, len(self.pred_obj_list))
				mapped_object = self.object_to_element.get(obj, "")
				imp = self.criticality_to_element.get(crit, "")
				if not mapped_object:
					print ("{} is not a recognised value for object.".format(obj))
					continue
				if not imp:
					print ("{} is not a recognised value for criticality.".format(crit))
					continue
				if pred == "Has child":
					satisfied_elems = [self.ontology.get_child_node(elem, mapped_object) for elem in subject_elements]
					error_elements = [self.ontology.extract_ID(subject_elements[i]) for (i,elem) in enumerate(satisfied_elems) if not elem]
					subject_elements = [elem[0] for elem in satisfied_elems if elem]
					warning_msg = "{} does not have child {}"
				elif pred == "Has attribute":
					satisfied_elems = [self.ontology.get_attribute(elem, mapped_object) for elem in subject_elements]
					error_elements = [self.ontology.extract_ID(subject_elements[i]) for (i,elem) in enumerate(satisfied_elems) if not elem]
					subject_elements = [elem for elem in satisfied_elems if elem]
					warning_msg = "{} does not have attribute {}"
				print ([(imp, warning_msg.format(elem, obj)) for elem in error_elements])
				results.extend([(imp, warning_msg.format(elem, obj)) for elem in error_elements])

		results.sort(key=sort_compare, reverse=True)	 
		return results