from flask import Flask, render_template, request, jsonify
import os
from pitfall_scanner import PitfallScanner
app = Flask(__name__)

@app.route('/results', methods = ['POST'])
def show_results():
    i, all_pitfalls = 0, []
    print (request.files)
    file = request.files["input-b2"]
    if not file.filename:
        return jsonify([{"Error": "No ontology uploaded."}])
    
    while request.form.get("subject-select-" + str(i), ""):
        Subject = request.form.get("subject-select-" + str(i))
        Predicate = request.form.getlist("predicate-select-" + str(i))
        Object = request.form.getlist("object-select-" + str(i))
        Criticality = request.form.get("criticality-select-" + str(i))
        all_pitfalls.append((Subject, Predicate, Object, Criticality))
        i+=1

    ontology = os.path.abspath(os.path.join("temp/", file.filename))
    file.save(ontology)

    scanner = PitfallScanner(ontology, all_pitfalls)
    curr_pitfalls = scanner.scan()
    modified_pitfalls = []
    for pitfall in curr_pitfalls:
        color = "<div style='color: red; float:right; padding-right: 10px; font-weight:bold'>{}: {} Violations</div>".format(pitfall[0].upper(), len(pitfall[1]))
        modified_pitfalls.append((color, pitfall[1], pitfall[2], pitfall[3]))

    return render_template("results.html", pitfalls=modified_pitfalls, ontology_name=file.filename)

# A welcome message to test our server
@app.route('/')
def main():
    return render_template("index.html")

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)