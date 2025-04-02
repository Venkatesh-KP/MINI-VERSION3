from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load and preprocess the CSV file
file_path = 'sample data-50.csv'  # Ensure this path is correct
df = pd.read_csv(file_path)

# Preprocess data to make it more efficient for searching
df_normalized = df.apply(lambda x: x.astype(str).str.strip().str.lower())

# Function to search by name and roll number and return full details
def search_students(name=None, roll_no=None):
    filtered_df = df_normalized.copy()  # Make a copy of the normalized dataframe

    # If name is provided, filter based on name
    if name:
        filtered_df = filtered_df[filtered_df['name'] == name.strip().lower()]
    
    # If roll number is provided, filter based on roll number
    if roll_no:
        filtered_df = filtered_df[filtered_df['roll_no'] == roll_no.strip().lower()]

    return filtered_df

@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/search', methods=['POST'])
def search():
    name = request.form.get('name')
    roll_no = request.form.get('roll_no')

    print(f"Searching for Name: {name}, Roll No: {roll_no}")  # Debugging

    # Perform search
    result_df = search_students(name, roll_no)

    if not result_df.empty:
        result = format_detailed_response(result_df)
    else:
        result = "No matching entry found."

    return jsonify(result)

def format_detailed_response(df):
    """
    Formats the response to be more user-friendly and detailed.
    """
    response = []
    for index, row in df.iterrows():
        response.append(f"Roll No: {row['roll_no']}, Name: {row['name']}, Age: {row['age']}, Major: {row['major']}, Graduation: {row['graduation']}")
    return "\n".join(response)

if __name__ == '__main__':
    app.run(debug=True)
