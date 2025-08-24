from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://diyarjoshy:vqIERSaq7hkeUedZ@kerala.ktsnxy5.mongodb.net/")
db = client["Kerala_culture"]
collection = db["3D_map_details"]

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/mainpage')
def mainpage():
    return render_template("mainpage.html")

@app.route('/slider')
def slider():
    return render_template("slider.html")

@app.route('/festival-calendar')
def festival_calendar():
    return render_template("festival-calendar.html")

@app.route('/timeline')
def timeline():
    return render_template("timeline.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/trip-planner')
def trip_planner():
    return render_template("trip-planner.html")

@app.route("/get_quiz", methods=["POST"])
def get_quiz():
    data = request.get_json()
    print(data)
    activity = data.get("activity")
    print("Received activity:",activity)  # Debugging line to check received activity
    print(activity)
    if not activity:
        return jsonify({"error": "No activity provided"}), 400
    
    # Fetch the document based on the activity name
    document = collection.find_one( 
   {"activities.name": activity},
    {"activities.$": 1, "_id": 0})
    

   # Flatten the questions
    questions_list = []

    for activity in document['activities']:
      for q in activity['questions']:
        questions_list.append({
            "question": q['question'],
            "options": q['options'],
            "answer": q['answer']
        })
    if questions_list!=None:
       return jsonify(questions_list)
        
    else:
        return jsonify({"questions": []})
    
@app.route('/get_image', methods=['POST'])
def get_image():
    data = request.get_json()
    
    name = data.get("name")

    # Search for the activity with the given name
    result = collection.find_one(
        
    {"activities.name": name},{"activities": {"$elemMatch": {"name": name}}, "_id": 0}
    
)   
    dict=result["activities"]
    image=dict[0]["image"]
    if image:
        return jsonify({"image": image})
    else:
            # Not found
         return jsonify({"error": "Activity not found"}), 404


@app.route("/get_summary", methods=["POST"])
def get_summary():
    data = request.get_json()
    activity_name = data.get("activity")  # e.g., "Padmanabhaswamy Temple"


    # Fetch the summary from MongoDB
    result = collection.find_one(
        
    {"activities.name": activity_name},
    {"activities": {"$elemMatch": {"name": activity_name}}, "_id": 0})
      # Return only the matching activity
    
    dict=result["activities"]
    summary=dict[0]["summary"]

    return jsonify({"summary": summary})

@app.route('/get_preview', methods=['POST'])
def get_preview():
    data = request.get_json()
    
    name = data.get("name")

    # Search for the activity with the given name
    result = collection.find_one(
        
    {"activities.name": name},{"activities": {"$elemMatch": {"name": name}}, "_id": 0}
    
)   
    dict=result["activities"]
    preview=dict[0]["preview"]
    if preview:
        return jsonify({"preview": preview})
    else:
            # Not found
         return jsonify({"error": "Activity not found"}), 404

@app.route('/get_district_images', methods=['POST'])
def get_district_images():
    data = request.get_json()
    district = data.get("district")
    print("the district is",district)
    
    if not district:
        return jsonify({"error": "No district provided"}), 400
    
    # District ID to name mapping (3D model uses generic IDs)
    district_mapping = {
                'district001': 'Alappuzha',
                'district004': 'Kasargod',
                'district003': 'Kannur',
                'district013': 'Wayanad',
                'district007': 'Kozhikode',
                'district008': 'Malappuram',
                'district009': 'Palakkad',
                'district012': 'Thrissur',
                'district001': 'Ernakulam',
                'district002': 'Idukki',
                'district006': 'Kottayam',
                'district014': 'Alappuzha',
                'district010': 'Pathanamthitta',
                'district005': 'Kollam',
                'district011': 'Thiruvananthapuram'}
    
    # Convert district ID to actual name
    actual_district = district_mapping.get(district, district)
    print(f"Mapped {district} to {actual_district}")
    
    # Fetch all activities for the given district
    result = collection.find_one(
        {"district": actual_district},
        {"activities": 1, "_id": 0}
    )
    
    if not result or not result.get("activities"):
        return jsonify({"error": "District not found or no activities"}), 404
    
    # Extract image categories from activities
    images = []
    # Mapping for filename corrections
    filename_mapping = {
        "museum": "musem",  # Handle the typo in your filename
        "musem": "musem"    # Keep as is if already correct
    }
    
    for activity in result["activities"]:
        if activity.get("image"):
            # Use the image field as category name to construct local path
            category = activity["image"]  # e.g., "temple", "beach", "museum"
            
            # Apply filename mapping if needed
            filename = filename_mapping.get(category.lower(), category.lower())
            
            images.append({
                "name": activity.get("name", ""),
                "category": category,
                "imagePath": f"/static/Pictures/{filename}.png"  # Construct local path
            })
            print(f"Activity: {activity.get('name')}, Category: {category}, Path: /static/Pictures/{filename}.png")
    
    return jsonify({"images": images})



if __name__ == "__main__":
    app.run()
