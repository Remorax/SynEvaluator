from scipy.spatial.distance import cosine
from re import finditer, split
from xml.dom import minidom
import validators, spacy
from inflection import camelize
from itertools import product
import numpy as np
from nltk.corpus import wordnet as wn

nlp = None
flatten = lambda l: [item for sublist in l for item in sublist]

def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0).lower() for m in matches])

def equality(ontology, a, b):
	if type(a) != type(b) or not a or not b:
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
	return np.transpose([np.tile(x, len(y)), np.repeat(y, len(x))])

def is_synonym(x,y):
	for syn in wn.synsets(x):
		for l in syn.lemmas():
			if camel_case_split(" ".join(l.name().lower().split("_"))) == camel_case_split(" ".join(y.lower().split("_"))):
				return True
	return False

def synonymy(ontology, a, b):
	if type(a) != type(b):
		return False
	if not a or not b:
		return True
	if type(a) == list:
		if type(a[0]) == minidom.Element:
			a = [camel_case_split(" ".join(ontology.extract_ID(elem_a).split("_"))) for elem_a in a]
		if type(b[0]) == minidom.Element:
			b = [camel_case_split(" ".join(ontology.extract_ID(elem_b).split("_"))) for elem_b in b]
		if type(a[0])!=str or type(b[0])!=str:
			return False
		for tup in cartesian_np(a, b):
			if is_synonym(*tup):
				return True
		return False
	if type(a) != str or type(b)!= str:
		return False
	return is_synonym(camel_case_split(" ".join(a.split("_"))), camel_case_split(" ".join(b.split("_"))))

def dissimilarity(ontology, a, b):
	if type(a) != type(b) or not a or not b:
		return True
	if type(a) == list:
		if type(a[0]) == minidom.Element:
			a = [camel_case_split(" ".join(ontology.extract_ID(elem_a).split("_"))) for elem_a in a]
		if type(b[0]) == minidom.Element:
			b = [camel_case_split(" ".join(ontology.extract_ID(elem_b).split("_"))) for elem_b in b]
		if type(a[0])!=str or type(b[0])!=str:
			return True
		for tup in cartesian_np(a, b):
			if is_synonym(*tup):
				return False
		return True
	if type(a) != str or type(b)!= str:
		return True
	return not is_synonym(camel_case_split(" ".join(a.split("_"))), camel_case_split(" ".join(b.split("_"))))

def inverse_checker(ontology, a, b):
	global nlp
	if not nlp:
		nlp = spacy.load("en_core_web_sm")
	a_nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(a.split("_")))) if elem.pos_ in ["NOUN", "PROPN"]]
	b_nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(b.split("_")))) if elem.pos_ in ["NOUN", "PROPN"]]
	return set(a_nouns) == set(b_nouns)

def inverse(ontology, a, b):
	if type(a) != type(b):
		return False
	if not a or not b:
		return True
	if type(a) == list:
		if type(a[0]) == minidom.Element:
			a = [camel_case_split(" ".join(ontology.extract_ID(elem_a).split("_"))) for elem_a in a]
		if type(b[0]) == minidom.Element:
			b = [camel_case_split(" ".join(ontology.extract_ID(elem_b).split("_"))) for elem_b in b]
		if type(a[0])!=str or type(b[0])!=str:
			return False
		for tup in product(a,b):
			if inverse_checker(ontology, *tup):
				return True
		return False
	if type(a) != str or type(b)!= str:
		return False
	return inverse_checker(ontology, *tup)

def text_validity(ontology, elements):
	global nlp
	if not nlp:
		nlp = spacy.load("en_core_web_sm")
	if not elements:
		return True
	if type(elements) == minidom.Element:
		elements = [elements]
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				if not element.firstChild:
					return False
				element_tokens = [token.lemma_.lower() for token in nlp(camel_case_split(" ".join(element.firstChild.nodeValue.split("_"))))]
				ID_tokens = [elem.lemma_.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element.parentNode).split("_"))))]
				if not set(element_tokens).intersection(set(ID_tokens)):
					return False
				# continue 

			elif type(element) == str:
				if element.startswith("http://") or element.startswith("https://") and not validators.url(element):
					return False
			else:
				print ("Exceptional type", type(element))
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
	if not elements:
		return True
	if type(elements) == minidom.Element:
		elements = [elements]
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

def text_symmetry(ontology, elements):
	global nlp
	if not elements:
		return True
	if not nlp:
		nlp = spacy.load("en_core_web_sm")
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_ in ["NOUN", "PROPN"]]
				if nouns[0]==nouns[-1]:
					return True
		return False
	elif type(elements) == str:
		nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(elements.split("_")))) if elem.pos_ in ["NOUN", "PROPN"]]
		return nouns[0]==nouns[-1]
	elif type(elements) == minidom.Element:
		nouns = [elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(elements).split("_")))) if elem.pos_ in ["NOUN", "PROPN"]]
		return nouns[0]==nouns[-1]
	return True

def uniqueness(ontology, elements):
	if type(elements) == list:
		return len([elem for elem in elements if elem]) <= 1
	return True

def is_empty_str(word):
	if type(word)!=str:
		return False
	return word.strip()

def is_polyseme(word):
	return len(wn.synsets(word)) > 1

def contains_polysemes(ontology, elements):

	global nlp
	if not nlp:
		nlp = spacy.load("en_core_web_sm")	
	if type(elements) == list:

		for element in elements:
			if type(element) == minidom.Element:
				if is_polyseme(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))):
					return True
			elif type(element) == str:
				if is_polyseme(camel_case_split(" ".join(element.split("_")))):
					return True
		return False
	elif type(elements) == minidom.Element:
		return is_polyseme(camel_case_split(" ".join(ontology.extract_ID(elements).split("_"))))
	elif type(elements) == str:
		return is_polyseme(camel_case_split(" ".join(elements.split("_"))))
	return False

def has_multiple_elements(word):
	all_elems, curr_elems = [], []
	for elem in camel_case_split(" ".join(word.split("_"))).split():
		if elem in ["and", "or"]:
			if curr_elems:
				all_elems.append(" ".join(curr_elems))
			curr_elems = []
		else:
			curr_elems.append(elem)
	if curr_elems:
		all_elems.append(" ".join(curr_elems))
	return len(all_elems) > 1

def contains_conjunctions(ontology, elements):
	global nlp
	if not nlp:
		nlp = spacy.load("en_core_web_sm")
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				
				if has_multiple_elements(ontology.extract_ID(element)):
					return True
			elif type(element) == str:
				if has_multiple_elements(element):
					return True
		return False
	elif type(elements) == minidom.Element:
		return has_multiple_elements(ontology.extract_ID(elements))
	elif type(elements) == str:
		return has_multiple_elements(elements)
	return False

def contains_misc_items(ontology, elements):
	global nlp
	if not nlp:
		nlp = spacy.load("en_core_web_sm")
	if type(elements) == list:
		for element in elements:
			if type(element) == minidom.Element:
				return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(element).split("_")))) if elem.pos_ in ["NOUN", "PROPN"]])
			elif type(element) == str:
				return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(element.split("_")))) if elem.pos_ in ["NOUN", "PROPN"]])
	elif type(elements) == minidom.Element:
		return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(ontology.extract_ID(elements).split("_")))) if elem.pos_ in ["NOUN", "PROPN"]])
	elif type(elements) == str:
		return any(["misc" in elem.text.lower() for elem in nlp(camel_case_split(" ".join(elements.split("_")))) if elem.pos_ in ["NOUN", "PROPN"]])
	return False

def and_operator(a, b):
	return a and b

def or_operator(a, b):
	return a or b

def not_operator(a, b):
	return not b

def extract_related_element(ontology, parents, child_tag):
	if type(parents) != list:
		parents = [parents]
	return flatten([ontology.get_child_node(parent, child_tag["Elements"]) for parent in parents])

def extract_attribute(ontology, elements, attribute_tag):
	if type(elements) != list:
		elements = [elements]
	final_list = flatten([ontology.get_attribute(element, attribute_tag["Elements"]) for element in elements])
	if "Mappable" not in attribute_tag:
		return final_list
	return attribute_tag["Mappable"](final_list, attribute_tag["Arguments"])

def extract_extension(ontology, labels, allowed_extensions):
	if type(labels) != list:
		labels = [labels]
	final_list = []
	for label in labels:
		extension = label.split(".")[-1]
		if not allowed_extensions["Elements"] or extension in allowed_extensions["Elements"]:
			final_list.append(extension)
	return final_list

def extract_corresponding_element(ontology, elements, element_type):
	if type(elements) != list:
		elements = [elements]
	final_list = []
	for element in elements:
		for elem in ontology.get_elements(element_type):
			if ontology.extract_ID(elem) == ontology.extract_ID(element):
				final_list.append(elem)
	return final_list

def execute_comparative_operator(ontology, operator, lhs, rhs):
	return operator(ontology, lhs, rhs)

def execute_logical_operator(ontology, operator, lhs, rhs):
	return operator(lhs, rhs)

def execute_ontological_relation(ontology, elements, function):
	return function(ontology, elements)

def execute_linguistic_relation(ontology, elements, function):
	return function(ontology, elements)

