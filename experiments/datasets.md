# Datasets

We include here the triples used to enrich the Stanford Pizza and ISO-IEC 27001 Information Security ontologies, as part of our experiments.

## Stanford Pizza Ontology

|       Term A      	|     Term B    	|     Relation    	| Label 	|
|:-----------------:	|:-------------:	|:---------------:	|:-----:	|
|     Anchovies     	| Pizza Topping 	|     Subclass    	|  True 	|
|     Neapolitan    	|     Pizza     	|     Subclass    	|  True 	|
|       Basil       	| Pizza Topping 	|     Subclass    	|  True 	|
| Quad Cities Pizza 	|     Italy     	| Originates from 	| False 	|
|    Greek Pizza    	|     Pizza     	|     Subclass    	|  True 	|

## Information Security Ontology

|       Term A       	|      Term B      	| Relation 	| Label 	|
|:------------------:	|:----------------:	|:--------:	|:-----:	|
|       Botnet       	|      Malware     	| Subclass 	| False 	|
|      Firewall      	| Network Security 	| Subclass 	|  True 	|
|         PII        	|       Data       	| Subclass 	|  True 	|
| Barracuda CloudGen 	|     Firewall     	| Instance 	|  True 	|
|      ILoveYou      	|    Ransomware    	| Instance 	| False 	|