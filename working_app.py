from flask import Flask, request, jsonify, render_template
import pandas as pd
import google.generativeai as palm

# Initialize the Flask app
app = Flask(__name__)

# Configure the Gemini API (replace with your actual API key)
palm.configure(api_key='AIzaSyBWBxsPBykuJ6z_kMYlAq9k9u3YU2Uy8Oc')

# Load the CSV file
file_path = 'sample data-50.csv'  # Ensure this path is correct
df = pd.read_csv(file_path)

# Preprocess data to lower case for comparison
df_normalized = df.apply(lambda x: x.astype(str).str.strip().str.lower())

# If the 'name' column exists, split it into first and last name
if 'name' in df_normalized.columns:
    df_normalized['first_name'] = df_normalized['name'].apply(lambda x: x.split()[0])  # Extract first name

# Function to search by a given field and return selected fields
def search_csv(search_value, search_by, return_fields):
    search_value = search_value.strip().lower()  # Normalize the search value

    if search_by not in df_normalized.columns:
        return "Invalid search field.", 400  # Error response for invalid field

    result = df_normalized[df_normalized[search_by] == search_value]

    if result.empty:
        return "No matching entry found.", 404  # No match found

    if any(field not in df_normalized.columns for field in return_fields):
        return "Invalid return fields requested.", 400  # Error for invalid return fields

    return result[return_fields].to_json(orient='records'), 200  # Successful response

# Generate natural language response using Gemini API
def generate_gemini_response(prompt):
    response = palm.generate_text(
        model='models/text-bison-001',
        prompt=prompt,
        temperature=0.7,
        max_output_tokens=256
    )
    return response.result

# Parse user query and search the dataset
def parse_user_query(query):
    # Simple parsing logic to interpret the user query
    if "details" in query:
        if "roll no" in query:
            roll_no = query.split()[-1]  # Extract the roll number
            return {
                "search_value": roll_no,
                "search_by": "roll_no",
                "return_fields": df.columns.tolist()  # Return all fields
            }
        elif "for" in query:
            name = query.split("for")[-1].strip()  # Extract the name after 'for'
            return {
                "search_value": name,
                "search_by": "first_name",  # Search by first name
                "return_fields": df.columns.tolist()  # Return all fields
            }
    return None

# Main route: Serve the HTML chatbot
@app.route('/')
def index():
    return render_template('chatbot.html', columns=df.columns)

# Search route for handling queries
@app.route('/search', methods=['POST'])
def search():
    user_query = request.form.get('user_query')
    if not user_query:
        return jsonify("No query provided"), 400  # Handle no input case

    # First, try to parse and search in the dataset
    parsed_query = parse_user_query(user_query.lower())

    if parsed_query:
        search_value = parsed_query.get('search_value')
        search_by = parsed_query.get('search_by')
        return_fields = parsed_query.get('return_fields')

        # Perform search in the CSV
        result_json, status_code = search_csv(search_value, search_by, return_fields)
        if status_code == 200:
            return jsonify(result_json), 200  # Return search results
        else:
            return jsonify(result_json), status_code  # Return error messages

    # If no structured data match, send query to Gemini for natural language processing
    else:
        gemini_prompt = f"""
        You are a chatbot that helps users with student information. I received this query:
        "{user_query}"
        Can you respond naturally to it based on the context of the student dataset and give an appropriate response?
        """

        try:
            gemini_response = generate_gemini_response(gemini_prompt)
            return jsonify(gemini_response), 200
        except Exception as e:
            return jsonify(f"Gemini API error: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=True)

