from ontology import *
from helper import *
from glob import glob
import os

def sort_compare(key):
	importance_dict = {"Critical": 3, "Intermediate": 2, "Minor": 1 }
	print (key)
	return importance_dict[key[0]]

class PitfallScanner():
	"""docstring for PitfallScanner"""
	def __init__(self, ontology_path, pitfalls):
		self.ontology = Ontology(ontology_path)
		self.pitfalls = pitfalls
		
		self.subject_to_element = {
			"Ontology Header": {"Elements": ["rdf:RDF"]},
			"Ontology Metadata": {"Elements": ["owl:Ontology"]},
			"All Elements": {"Elements": ["owl:Class", "owl:NamedIndividual", "owl:Thing", "owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty"]},
			"Classes": {"Elements": ["owl:Class"]}, 
			"Instances": {"Elements": ["owl:NamedIndividual", "owl:Thing"]},
			"Properties": {"Elements": ["owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty"]},
			"Object Properties": {"Elements": ["owl:ObjectProperty"]},
			"Datatype Properties": {"Elements": ["owl:DatatypeProperty"]},
			"Functional Properties": {"Elements": ["owl:ObjectProperty"]},
			"Inverse Functional Properties": {"Elements": ["owl:DatatypeProperty"]},
			"Symmetric Properties": {"Elements": ["owl:ObjectProperty"], "Mappable": self.ontology.check_child_attribute,  "Arguments": [("rdf:type", "SymmetricProperty")]},
			"Transitive Properties": {"Elements": ["owl:ObjectProperty"], "Mappable": self.ontology.check_child_attribute,  "Arguments": [("rdf:type", "TransitiveProperty")]}
		}

		self.predicate_to_function = {
			"Has Related Element": extract_related_element,
			"Has Descriptive Element": extract_related_element,
			"Has Attribute": extract_attribute,
			"Has File Extension": extract_extension,
			"Maps to Element of Type": extract_corresponding_element,
			"Uses Comparative Operator": execute_comparative_operator,
			"Uses Logical Operator": execute_logical_operator,
			"Has Ontological Property": execute_ontological_relation,
			"Has Linguistic Property": execute_linguistic_relation 
		}

		self.object_to_element = {
			"License": {"Elements": ["terms:license"]},
			"Label": {"Elements": ["rdfs:label"]}, 
			"Comment": {"Elements": ["rdfs:Comment"]}, 
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
			"Property": {"Elements": ["owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty"]},
			"Relation": {"Elements": ["owl:ObjectProperty", "owl:DatatypeProperty", "owl:FunctionalProperty", "owl:InverseFunctionalProperty", "rdfs:subclassOf"]},
			"Other": {"Elements": []}
		}

		self.operator_to_function = {
			"Equality": equality,
			"Inequality": inequality,
			"Synonymy": synonymy,
			"Inverse": inverse,
			"And": and_operator,
			"Or": or_operator,
			"Not": not_operator
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

	def parse(self, start, end, results):
		subject = results
		for i in range(start, end):
			curr_pred, curr_obj = self.pred_obj_list[i]
			if curr_obj in self.object_to_element:
				mapped_object, statement_type = self.object_to_element.get(curr_obj, ""), "Extractive"
			elif curr_obj in self.operator_to_function:
				mapped_object, statement_type = self.operator_to_function.get(curr_obj, ""), "Comparative"
			elif curr_obj in self.property_to_function:
				mapped_object, statement_type = self.property_to_function.get(curr_obj, ""), "Functional"
			else:
				print ("{} is not a recognised value for object.".format(curr_obj))
				continue

			mapped_pred = self.predicate_to_function.get(curr_pred, "")
			if not mapped_pred:
				print ("{} is not a recognised value for predicate.".format(curr_pred))
				continue

			if statement_type == "Comparative":
				results = mapped_pred(self.ontology, mapped_object, results, self.parse(start+1, end, subject))
			else:
				results = mapped_pred(self.ontology, results, mapped_object)
		return results

	def scan(self):
		results = []
		for (idx,pitfall) in enumerate(self.pitfalls):
			Subject, Predicate, Object, Criticality = pitfall
			mapped_subject = self.subject_to_element.get(Subject, "")
			if not mapped_subject:
				print ("{} is not a recognised value for subject.".format(Subject))
				continue
			self.subject_elements = self.ontology.get_elements(mapped_subject)
			self.pred_obj_list = list(zip(Predicate, Object))
			curr_results = [self.parse(0, len(self.pred_obj_list), [subject]) for subject in self.subject_elements]
			error_elements = [self.ontology.extract_ID(self.subject_elements[i]) for i,elem in enumerate(curr_results) if not elem]
			results.append((Criticality, error_elements))
			print (Criticality)
		results.sort(key=sort_compare, reverse=True)	 
		return results