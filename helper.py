import tensorflow_hub as hub
from scipy.spatial.distance import cosine
from re import finditer
from xml.dom import minidom
import validators, spacy
from inflection import camelize
from itertools import product
import numpy as np
from nltk.corpus import wordnet as wn

model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
nlp = spacy.load("en_core_web_sm")
flatten = lambda l: [item for sublist in l for item in sublist]

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0).lower() for m in matches])

def USE_embeddings(words):
	return model(words)

def equality(ontology, a, b):
	if type(a) != type(b):
		return False
	if type(a) == list:
		if type(a[0]) == minidom.Element or type(b[0]) == minidom.Element:
			return set([ontology.extract_ID(elem_a) for elem_a in a]) == set([ontology.extract_ID(elem_b) for elem_b in b])
		else:
			return set(a) == set(b)
	elif type(a) == minidom.Element:
		return ontology.extract_ID(a) == ontology.extract_ID(b)
	return a == b

def inequality(ontology, a, b):
	return not equality(ontology, a,b)

def cartesian_np(x,y):
	return numpy.transpose([numpy.tile(x, len(y)), numpy.repeat(y, len(x))])

def synonymy(ontology, a, b):
	if type(a) != type(b):
		return False
	if type(a) == list:
		if type(a[0]) == minidom.Element:
			a = [camel_case_split(" ".join(ontology.extract_ID(elem_a).split("_"))) for elem_a in a]
		if type(b[0]) == minidom.Element:
			b = [camel_case_split(" ".join(ontology.extract_ID(elem_b).split("_"))) for elem_b in b]
		if type(a[0])!=str or type(b[0])!=str:
			return False
		for tup in cartesian_np(USE_embeddings(a), USE_embeddings(b)):
			if cosine_similarity(*tup) > 0.6:
				return True
		return False
	if type(a) != str or type(b)!= str:
		return False
	return cosine_similarity(*USE_embeddings([a,b])) > 0.6

def inverse_checker(a, b):
	a_nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(a).split("_")))) if elem.pos_[:2] == "NN"]
	b_nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(b).split("_")))) if elem.pos_[:2] == "NN"]
	return set(a_nouns) == set(b_nouns)

def inverse(ontology, a, b):
	if type(a) != type(b):
		return False
	if type(a) == list:
		if type(a[0]) == minidom.Element:
			a = [camel_case_split(" ".join(ontology.extract_ID(elem_a).split("_"))) for elem_a in a]
		if type(b[0]) == minidom.Element:
			b = [camel_case_split(" ".join(ontology.extract_ID(elem_b).split("_"))) for elem_b in b]
		if type(a[0])!=str or type(b[0])!=str:
			return False
		for tup in itertools.product(a,b):
			if inverse_checker(*tup):
				return True
		return False
	if type(a) != str or type(b)!= str:
		return False
	return inverse_checker(*tup)

def text_validity(ontology, elements):
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				element_tokens = [token.lower() for token in nlp(element.firstChild.nodeValue)]
				ID_tokens = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"]
				if not set(element_tokens).intersection(set(ID_tokens)):
					return False
				continue 
			if element.startswith("http://") or element.startswith("https://"):
				if not validators.url(element):
					return False
		return True
	elif type(elements) == str:
		if elements.startswith("http://") or elements.startswith("https://"):
			return validators.url(elements)
	return True

def is_camel_case(s):
	return camelize(s) == s or camelize(s, False) == s

def is_underscored_string(s):
	return len([char for char in s.split("_") if char]) > 1

def id_consistency(ontology, elements):
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				element_id = ontology.extract_ID(element)
				if is_underscored_string(element_id):
					all_elems = ontology.get_elements({"Elements": element.tagName})
					for elem in all_elems:
						elem_id = ontology.extract_ID(elem)
						if not is_underscored_string(elem_id) and is_camel_case(elem_id):
							return False
				elif is_camel_case(element_id):
					all_elems = ontology.get_elements({"Elements": element.tagName})
					for elem in all_elems:
						elem_id = ontology.extract_ID(elem)
						if is_underscored_string(elem_id):
							return False
		return True
	elif type(elements) == minidom.Element:
		element_id = ontology.extract_ID(elements)
		if is_underscored_string(element_id):
			all_elems = ontology.get_elements({"Elements": elements.tagName})
			for elem in all_elems:
				elem_id = ontology.extract_ID(elem)
				if not is_underscored_string(elem_id) and is_camel_case(elem_id):
					return False
		elif is_camel_case(element_id):
			all_elems = ontology.get_elements({"Elements": elements.tagName})
			for elem in all_elems:
				elem_id = ontology.extract_ID(elem)
				if is_underscored_string(elem_id):
					return False
	return True

def text_symmetry(ontology, elements):
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"]
				if nouns[0]==nouns[-1]:
					return True
		return False
	elif type(elements) == str:
		nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(elements.split("_")))) if elem.pos_[:2] == "NN"]
		return nouns[0]==nouns[-1]
	elif type(elements) == minidom.Element:
		nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(elements).split("_")))) if elem.pos_[:2] == "NN"]
		return nouns[0]==nouns[-1]
	return True

def uniqueness(ontology, elements):
	if type(elements) == list:
		return len([elem for elem in elements if elem]) == 1
	return True

def is_polyseme(word):
	return len(wn.synsets(word)) > 1

def contains_polysemes(ontology, elements):
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				return any([is_polyseme(elem.text.lower()) for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"])
			elif type(element) == str:
				return any([is_polyseme(elem.text.lower()) for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_[:2] == "NN"])
	elif type(element) == minidom.Element:
		return any([is_polyseme(elem.text.lower()) for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"])
	elif type(element) == str:
		return any([is_polyseme(elem.text.lower()) for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_[:2] == "NN"])
	return False

def contains_conjunctions(ontology, elements):
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				return any([elem.text.lower() in ["and", "or"] for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"])
			elif type(element) == str:
				return any([elem.text.lower() in ["and", "or"] for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_[:2] == "NN"])
	elif type(element) == minidom.Element:
		return any([elem.text.lower() in ["and", "or"] for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"])
	elif type(element) == str:
		return any([elem.text.lower() in ["and", "or"] for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_[:2] == "NN"])
	return False

def contains_conjunctions(ontology, elements):
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"])
			elif type(element) == str:
				return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_[:2] == "NN"])
	elif type(element) == minidom.Element:
		return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_[:2] == "NN"])
	elif type(element) == str:
		return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_[:2] == "NN"])
	return False

def and_operator(a, b):
	return a and b

def or_operator(a, b):
	return a or b

def extract_child_element(ontology, parents, child_tag):
	return flatten([ontology.get_child_node(parent, child_tag["Elements"]) for parent in parents])

def extract_attribute(ontology, elements, attribute_tag):
	return flatten([ontology.get_attribute(element, attribute_tag["Elements"]) for element in elements])

def extract_extension(ontology, labels, allowed_extensions):
	final_list = []
	for label in labels:
		extension = label.split(".")[-1]
		if not allowed_extensions["Elements"] or extension in allowed_extensions["Elements"]:
			return True
	return False

def extract_corresponding_element(ontology, elements, element_type):
	final_list = []
	for element in elements:
		for elem in ontology.get_elements(element_type):
			if ontology.extract_ID(elem) == ontology.extract_ID(element):
				final_list.extend(elem)
	return final_list

def execute_comparison(ontology, operator, lhs, rhs):
	return operator(ontology, lhs, rhs)

def execute_conjunction(operator, lhs, rhs):
	return operator(lhs, rhs)

def execute_logical_relation(ontology, elements, function):
	return function(ontology, elements["Elements"])

