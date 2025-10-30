import os

import random

import pandas as pd

from flask import Flask, render_template, jsonify, send_from_directory



app = Flask(__name__, template_folder='templates', static_folder='static')



# --- S.H.I.E.L.D. Pattern Logic ---

# This logic MUST match the logic used to create your CSV files.

PATTERNS = {

    0: lambda a, b: (a ** 2) - (b ** 2),

    1: lambda a, b: (a ** 3) - (b ** 3),

}



# --- File Paths ---

STATIC_DIR = os.path.join(os.getcwd(), 'static')

DATASET_FILES = [f'dataset{i}.csv' for i in range(1, 11)]



@app.route('/')

def index():

    """Serves the main HTML page."""

    return render_template('index.html')



@app.route('/get-mission')

def get_mission():

    """

    Picks a random dataset, reads it, calculates the answers,

    and returns the CSV text and answers.

    """

    try:

        # 1. Pick a random dataset file

        chosen_file = random.choice(DATASET_FILES)

        file_path = os.path.join(STATIC_DIR, chosen_file)



        if not os.path.exists(file_path):

            return jsonify({"error": f"File not found: {chosen_file}. Make sure it's in the 'static' folder."}), 404



        # 2. Read the file with pandas

        # *** IMPORTANT FIX ***

        # Read the 'Output' column as a string (object) so we can find the '?'

        df = pd.read_csv(file_path, dtype={'Output': str})

       

        # 3. Store the raw CSV text to send to the user

        with open(file_path, 'r') as f:

            csv_data_string = f.read()



        # 4. Find the '?' rows and calculate answers

        answers = []

        # Now this search for the string '?' will work correctly

        unknown_rows = df[df['Output'] == '?']

       

        if unknown_rows.empty:

             return jsonify({"error": f"No rows with '?' found in {chosen_file}. Check file data."}), 500



        for _, row in unknown_rows.iterrows():

            ptype = int(row['PatternType'])

            a = int(row['A'])

            b = int(row['B'])

           

            if ptype in PATTERNS:

                answer = PATTERNS[ptype](a, b)

                answers.append(answer)

            else:

                return jsonify({"error": f"Unknown PatternType {ptype} in {chosen_file}"}), 500

       

        # 5. Return the CSV text and the calculated answers

        return jsonify({

            "csv_data": csv_data_string,

            "answers": answers

        })



    except Exception as e:

        print(f"Error in /get-mission: {e}")

        return jsonify({"error": str(e)}), 500



@app.route('/<path:filename>')

def serve_static_file(filename):

    """Serves static files (like link.txt) from the 'static' directory."""

    # This route is used to serve 'link.txt'

    return send_from_directory(STATIC_DIR, filename)



if __name__ == '__main__':

    app.run(debug=True)