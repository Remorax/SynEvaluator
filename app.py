from flask import Flask, render_template, request
import os
from pitfall_scanner import PitfallScanner
app = Flask(__name__)

@app.route('/results', methods = ['POST'])
def show_results():
    i, all_pitfalls = 0, []

    file = request.files["file"]
    if not file.filename:
        return jsonify([])
    
    while request.form.get("subject-select-" + str(i), ""):
        Subject = request.form.get("subject-select-" + str(i))
        Predicate = request.form.getlist("predicate-select-" + str(i))
        Object = request.form.getlist("object-select-" + str(i))
        Criticality = request.form.get("criticality-select-" + str(i))
        all_pitfalls.append((Subject, Predicate, Object, Criticality))
        i+=1

    ontology = os.path.abspath(os.path.join("temp/", file.filename))
    file.save(ontology)
    if not pitfalls_dict or not final_data:
        for ontology in ontologies:
            scanner = PitfallScanner(ontology, all_pitfalls)
            curr_pitfalls = scanner.scan()
            counts = {"High": 0, "Medium": 0, "Low": 0}
            counts.update(Counter([el[0] for el in curr_pitfalls]))
            ontology_name = '.'.join(ontology.split('/')[-1].split('.')[:-1])
            final_data.append((ontology_name, list(counts.values())))
            pitfalls_dict[ontology_name] = curr_pitfalls

    
    return render_template("results.html")

# A welcome message to test our server
@app.route('/')
def main():
    return render_template("index.html")

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)