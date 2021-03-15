from xml.dom import minidom
from urllib.request import urlopen
from re import finditer

flatten = lambda l: [item for sublist in l for item in sublist]

def split_by_camel_case(identifier):
    # Split string by camel-case
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])

# Define class to parse ontology
class Ontology():
    def __init__(self, ontology):
        '''
        Instantiates an Ontology object. 
        Args:
            ontology: Path to ontology file
        Returns:
            Parsed Ontology object
        '''
        self.ontology = ontology
        if ontology.startswith("https://") or ontology.startswith("http://"):
            self.ontology_obj = minidom.parse(urlopen(ontology + "/"))
        else:
            self.ontology_obj = minidom.parse(ontology)
        self.root = self.ontology_obj.documentElement # root node

        self.construct_mapping_dict()
        
        self.subclasses = self.parse_subclasses()
        self.object_properties = self.parse_object_properties()
        self.data_properties = self.parse_data_properties()
        self.classes = self.parse_classes()        
        self.instances = self.parse_instances()

    def construct_mapping_dict(self):
        '''
        Constructs ID to label mapping dict for ontologies where 
        entities are identified by IDs.
        '''
        elements = self.root.getElementsByTagName("owl:Class") + self.root.getElementsByTagName("owl:NamedIndividual") + self.root.getElementsByTagName("owl:Thing")
        mapping_dict = {self.extract_ID(el, False): self.return_label(el) for el in elements if self.get_child_node(el, "rdfs:label")}
        self.mapping_dict = {elem: mapping_dict[elem] for elem in mapping_dict if mapping_dict[elem]}
        self.mapping_dict_inv = {self.mapping_dict[key]: key for key in self.mapping_dict}
        return

    def parse_classes(self):
        '''
        Parse only classes
        '''
        entities = [self.extract_ID(el) for el in self.root.getElementsByTagName("owl:Class")]
        return list(set(self.filter_null(entities)))

    def parse_instances(self):
        '''
        Parses ontology to obtain (instance, concept) tuples
        Returns:
            list of instance-concept 2-tuples of the form (a,b)
        '''
        instances = self.root.getElementsByTagName("owl:NamedIndividual") + self.root.getElementsByTagName("owl:Thing")
        instance_pairs = []
        for instance in instances:
            concept = self.get_child_node(instance, "rdf:type")
            if concept:
                instance_pairs.append((self.extract_ID(concept[-1]), self.extract_ID(instance)))
        return list(set(self.filter_null(instance_pairs)))

    def return_label(self, el):
        '''
        Returns label of an element, and also detects language of the label
        '''
        label_element = [l for l in self.get_child_node(el, "rdfs:label") if not l.getAttribute("xml:lang") or l.getAttribute("xml:lang") == "en"]
        if not label_element:
            return ''
        label_element = label_element[0]
        return label_element.firstChild.nodeValue

    def get_attribute(self, element, attribute):
        '''
        Returns attribute with a specific tag name given DOM element 
        Args:
            element: DOM element
            attribute: Name of attribute tag
        Returns:
            DOM attribute
        '''
        if type(attribute) == list:
            ret = [element.attributes.get(attrib, "") for attrib in attribute]
            return [el.firstChild.nodeValue for el in ret if el]
        return [element.attributes.get(attribute, "").firstChild.nodeValue]

    def check_child_attribute(self, all_elements, restrictions):
        for restriction in restrictions:
            filtered_elements = []
            for elem in all_elements:
                children = self.get_child_node(elem, restriction[0])
                if any([self.extract_ID(child) == restriction[1] for child in children]):
                    filtered_elements.append(elem)
            all_elements = filtered_elements
        return all_elements

    def get_elements(self, elements):
        '''
        Returns elements with a specific tag name from the parsed ontology
        Args:
            elements: List of element names to fetch
        Returns:
            List of DOM elements
        '''
        final_list = []
        for element in elements["Elements"]:
            curr_elements = self.root.getElementsByTagName(element)
            if "Mappable" in elements:
                curr_elements = elements["Mappable"](curr_elements, elements["Arguments"])
            final_list.extend(curr_elements)
        return final_list

    def extract_namespace(self, all_elements, arguments=[]):
        if type(all_elements) != list:
            return all_elements.split("#")[0]
        return [element.split("#")[0] for element in all_elements]

    def get_child_node(self, element, tag):
        '''
        Returns child node with a specific tag name given DOM element 
        Args:
            element: DOM parent element
            tag: Name of tag of child/List of name tags
        Returns:
            DOM Related Element 
        '''
        if type(tag) == list:
            return [e for e in element._get_childNodes() if type(e)==minidom.Element and e._get_tagName() in tag]
        return [e for e in element._get_childNodes() if type(e)==minidom.Element and e._get_tagName() == tag]

    def parse_subclasses(self):
        '''
        Parses ontology to obtain subclass 2-tuples
        Returns:
            list of subclass 2-tuples of the form (a,b)
        '''
        subclasses = self.root.getElementsByTagName("rdfs:subClassOf")
        subclass_pairs = []
        for el in subclasses:
            inline_subclasses = self.extract_ID(el)
            if inline_subclasses:
                # Subclass of with inline IDs
                subclass_pairs.append((el, el.parentNode))
            else:
                level1_class = self.get_child_node(el, "owl:Class")
                if level1_class:
                    if self.extract_ID(level1_class[0]):
                        # Subclass label under a level 1 tag
                        subclass_pairs.append((level1_class[0], el.parentNode))
                    else:
                        continue
        subclasses = [(self.extract_ID(a), self.extract_ID(b)) for (a,b) in subclass_pairs]
        subclasses = [elem for elem in subclasses if elem[0]!="Thing" and elem[1]!="Thing"]
        return subclasses

    def filter_null(self, data):
        return [el for el in data if el]

    def extract_ID(self, element, extract_label=True):
        '''
        Returns ID for a parsed DOM element. In ontologies where classes are represented by 
        numerical IDs, it returns the label (stored in mapping_dict)
        '''
        if not element:
            return ""
        element_id = element.getAttribute("rdf:ID") or element.getAttribute("rdf:resource") or element.getAttribute("rdf:about")
        element_id = element_id.split("#")[-1].split(";")[-1]
        # print (element_id)
        if extract_label and element_id in self.mapping_dict:
            return self.mapping_dict[element_id]
        if not element_id:
            return element.firstChild.nodeValue
        return element_id.replace("UNDEFINED_", "").replace("DO_", "")

    def extract_IDname(self, elements, arguments):
        return [element.split("#")[1] for element in elements]

    def create_new_class_for_range(self, url, range_iri, range_label):
        '''
        Creates new class for range if it does not exist.
        '''
        all_classes = self.root.getElementsByTagName("owl:Class")
        range_search = [elem for elem in all_classes if split_by_camel_case(self.extract_ID(elem)).lower() == range_label.lower()]
        if not range_search:
            newrange = self.ontology_obj.createElement("owl:Class")
            newrange.setAttribute("rdf:about", url + "#" + range_iri)

            newrangelabel = self.ontology_obj.createElement("rdfs:label")
            newrangelabel.setAttribute("xml:lang","en")
            text = self.ontology_obj.createTextNode(range_label)
            newrangelabel.appendChild(text)

            newrange.appendChild(newrangelabel)

            self.memberify_created_classes(url, [range_iri], newrange)

    def add_subclass_to_existing_class(self, url, class_label, subclass_iri, subclass_label):
        '''
        Adds subclass to pre-existing class.
        '''
        all_classes = self.root.getElementsByTagName("owl:Class")
        relevant_class = [elem for elem in all_classes if split_by_camel_case(self.extract_ID(elem)).lower() == class_label.lower()][0]

        newElementSubClass = self.ontology_obj.createElement("rdfs:subClassOf")
        newElementSubClass.setAttribute("rdf:resource", url + "#" + subclass_iri)

        relevant_class.appendChild(newElementSubClass)

        self.create_new_class_for_range(url, subclass_iri, subclass_label)

    def create_class_with_subclass(self, url, class_iri, subclass_iri, class_label, subclass_label):
        '''
        Creates new class with subclass and label
        '''
        newElementClass = self.ontology_obj.createElement("owl:Class")
        newElementClass.setAttribute("rdf:about", url + "#" + class_iri)

        newElementSubClass = self.ontology_obj.createElement("rdfs:subClassOf")
        newElementSubClass.setAttribute("rdf:resource", url + "#" + subclass_iri)

        newelementclasslabel = self.ontology_obj.createElement("rdfs:label")
        newelementclasslabel.setAttribute("xml:lang","en")
        text = self.ontology_obj.createTextNode(class_label)
        newelementclasslabel.appendChild(text)

        newElementClass.appendChild(newElementSubClass)
        newElementClass.appendChild(newelementclasslabel)

        self.create_new_class_for_range(url, subclass_iri, subclass_label)

        self.memberify_created_classes(url, [class_iri], newElementClass)

    def create_instance(self, url, class_iri, instance_iri, class_label, instance_label):
        '''
        Creates instance of type class
        '''
        newInstance = self.ontology_obj.createElement("owl:NamedIndividual")
        newInstance.setAttribute("rdf:about", url + "#" + instance_iri)

        newInstanceType = self.ontology_obj.createElement("rdf:type")
        newInstanceType.setAttribute("rdf:resource", url + "#" + class_iri)

        newelementclasslabel = self.ontology_obj.createElement("rdfs:label")
        newelementclasslabel.setAttribute("xml:lang","en")
        text = self.ontology_obj.createTextNode(instance_label)
        newelementclasslabel.appendChild(text)

        newInstance.appendChild(newelementclasslabel)
        newInstance.appendChild(newInstanceType)

        self.create_new_class_for_range(url, class_iri, class_label)

        self.memberify_created_classes(url, [instance_iri], newInstance, True)

    def add_property_to_existing_class(self, url, iri2, relation_iri, class_label, subclass_label):
        '''
        Finds existing class and adds property to it
        '''
        all_classes = self.root.getElementsByTagName("owl:Class")
        relevant_class = [elem for elem in all_classes if split_by_camel_case(self.extract_ID(elem)).lower() == class_label.lower()][0]

        newElementSubClass = self.ontology_obj.createElement("rdfs:subClassOf")

        newElementRestriction = self.ontology_obj.createElement("owl:Restriction")
        newElementProperty = self.ontology_obj.createElement("owl:onProperty")
        newElementProperty.setAttribute("rdf:resource", url + "#" + relation_iri)
        newElementsomeValuesFrom = self.ontology_obj.createElement("owl:someValuesFrom")
        newElementsomeValuesFrom.setAttribute("rdf:resource", url + "#" + iri2)

        newElementRestriction.appendChild(newElementProperty)
        newElementRestriction.appendChild(newElementsomeValuesFrom)
        newElementSubClass.appendChild(newElementRestriction)

        relevant_class.appendChild(newElementSubClass)

        self.create_new_class_for_range(url, iri2, subclass_label)

    def create_class_with_property(self, url, iri1, iri2, relation_iri, class_label, subclass_label):
        newElementClass = self.ontology_obj.createElement("owl:Class")
        newElementClass.setAttribute("rdf:about", url + "#" + iri1)
        newElementSubClass = self.ontology_obj.createElement("rdfs:subClassOf")

        newElementRestriction = self.ontology_obj.createElement("owl:Restriction")
        newElementProperty = self.ontology_obj.createElement("owl:onProperty")
        newElementProperty.setAttribute("rdf:resource", url + "#" + relation_iri)
        newElementsomeValuesFrom = self.ontology_obj.createElement("owl:someValuesFrom")
        newElementsomeValuesFrom.setAttribute("rdf:resource", url + "#" + iri2)

        newelementclasslabel = self.ontology_obj.createElement("rdfs:label")
        newelementclasslabel.setAttribute("xml:lang","en")
        text = self.ontology_obj.createTextNode(class_label)
        newelementclasslabel.appendChild(text)
        
        newElementRestriction.appendChild(newElementProperty)
        newElementRestriction.appendChild(newElementsomeValuesFrom)
        newElementSubClass.appendChild(newElementRestriction)

        newElementClass.appendChild(newElementSubClass)
        newElementClass.appendChild(newelementclasslabel)

        self.memberify_created_classes(url, [iri1, iri2], newElementClass)

        self.create_new_class_for_range(url, iri2, subclass_label)

    def parse_data_properties(self):
        '''
        Parse all datatype properties, including functional and inverse functional datatype properties
        '''
        data_properties = [el for el in self.get_child_node(self.root, 'owl:DatatypeProperty')]
        fn_data_properties = [el for el in self.get_child_node(self.root, 'owl:FunctionalProperty') if el]
        fn_data_properties = [el for el in fn_data_properties if type(el)==minidom.Element and 
            [el for el in self.get_child_node(el, "rdf:type") if 
             self.has_attribute_value(el, "rdf:resource", "DatatypeProperty")]]
        inv_fn_data_properties = [el for el in self.get_child_node(self.root, 'owl:InverseFunctionalProperty') if el]
        inv_fn_data_properties = [el for el in inv_fn_data_properties if type(el)==minidom.Element and 
            [el for el in self.get_child_node(el, "rdf:type") if 
             self.has_attribute_value(el, "rdf:resource", "DatatypeProperty")]]
        return data_properties + fn_data_properties + inv_fn_data_properties
        
    def parse_object_properties(self):
        '''
        Parse all object properties, including functional and inverse functional object properties
        '''
        obj_properties = [el for el in self.get_child_node(self.root, 'owl:ObjectProperty')]
        fn_obj_properties = [el for el in self.get_child_node(self.root, 'owl:FunctionalProperty') if el]
        fn_obj_properties = [el for el in fn_obj_properties if type(el)==minidom.Element and 
            [el for el in self.get_child_node(el, "rdf:type") if 
             self.has_attribute_value(el, "rdf:resource", "ObjectProperty")]]
        inv_fn_obj_properties = [el for el in self.get_child_node(self.root, 'owl:InverseFunctionalProperty') if el]
        inv_fn_obj_properties = [el for el in inv_fn_obj_properties if type(el)==minidom.Element and 
            [el for el in self.get_child_node(el, "rdf:type") if 
             self.has_attribute_value(el, "rdf:resource", "ObjectProperty")]]
        return obj_properties + fn_obj_properties + inv_fn_obj_properties

    def memberify_created_classes(self, url, iris, new_class, is_instance=False):
        needed = self.ontology_obj.getElementsByTagName("owl:Class")
        needed[0].parentNode.insertBefore(new_class, needed[0])
        search = self.ontology_obj.getElementsByTagName("owl:members")
        if not search:
            return
        if not is_instance:
            search = search[0]
        else:
            search = search[-1]
        if search.getAttribute("rdf:parseType"):
            for iri in iris:
                # print (iri)
                newelementclass = self.ontology_obj.createElement("rdf:Description")
                newelementclass.setAttribute("rdf:about", url + "#" + iri)
                search.appendChild(newelementclass)

    
    def write(self, file):
        outputfile = open(file,"w+")
        outputfile.write(self.ontology_obj.toprettyxml())
        outputfile.close()