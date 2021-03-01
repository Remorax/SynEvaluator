from onto_app.ontology import *
from glob import glob
import os
import onto_app.pitfalls

def sort_compare(key):
	importance_dict = {"High": 3, "Medium": 2, "Low": 1 }
	return importance_dict[key[0]]

class PitfallScanner():
	"""docstring for PitfallScanner"""
	def __init__(self, ontology_path, pitfalls_dir, created_pitfalls):
		self.ontology = Ontology(ontology_path)
		self.pitfalls_dir = os.path.abspath(pitfalls_dir)
		self.created_pitfalls = created_pitfalls
		
		self.subject_to_element = {
		"Classes": ["owl:Class"], 
		"Instances": ["owl:NamedIndividual", "owl:Thing"],
		"Properties": ["owl:ObjectProperty", "owl:DatatypeProperty",\
		 "owl:FunctionalProperty", "owl:InverseFunctionalProperty"]}

		self.object_to_element = {
		"Label": ["rdfs:label"], 
		"Type": ["rdf:type"],
		"Domain": ["rdfs:domain"],
		"Range": ["rdfs:range"],
		"Subclass": ["rdfs:subclassOf"],
		"Language": ["xml:lang"],
		"ID": ["rdf:ID", "rdf:resource", "rdf:about"]}

		self.criticality_to_element = {"Critical": "High", "Intermediate": "Medium", "Minor": "Low"}

	def scan(self):
		results = []
		for pitfall_module in pitfalls.__init__.__load_all__():
			results.extend(pitfall_module.scan(self.ontology))
		
		for custom_pitfall in self.created_pitfalls:
			Subject, Predicate, Object, Criticality = custom_pitfall
			mapped_subject = self.subject_to_element.get(Subject, "")
			if not mapped_subject:
				print ("{} is not a recognised value for subject.".format(Subject))
				continue
			subject_elements = self.ontology.get_elements(mapped_subject)
			for (pred, obj, crit) in list(zip(Predicate, Object, Criticality)):
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