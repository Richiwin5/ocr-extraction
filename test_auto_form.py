# test_form_autofill.py
import requests
import json
from pprint import pprint

def test_voters_card_extraction(image_path):
    """
    Test the Voter's Card extraction and form auto-fill
    """
    url = "http://localhost:8000/extract-id"
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        
        print("=" * 50)
        print("EXTRACTED VOTER'S CARD DATA")
        print("=" * 50)
        
        # Print raw text
        print("\n📄 RAW TEXT:")
        print("-" * 30)
        print(data.get("raw_text", "N/A"))
        
        # Print structured fields
        print("\n📋 STRUCTURED FIELDS:")
        print("-" * 30)
        fields = data.get("fields", {})
        
        # Define field mapping for form auto-fill
        form_mapping = {
            "vin": "Voter ID Number",
            "full_name": "Full Name",
            "surname": "Surname",
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "date_of_birth": "Date of Birth",
            "occupation": "Occupation",
            "address": "Address",
            "state": "State",
            "lga": "Local Government Area",
            "ward": "Ward",
            "polling_unit": "Polling Unit"
        }
        
        for field, label in form_mapping.items():
            if field in fields:
                print(f"{label}: {fields[field]}")
        
        # Generate form data for auto-fill
        print("\n📝 AUTO-FILL FORM DATA:")
        print("-" * 30)
        form_data = {}
        
        # Map to common form field names
        form_fields = {
            "vin": ["voter_id", "vin", "identification_number"],
            "full_name": ["fullname", "name"],
            "surname": ["lastname", "surname", "last_name"],
            "first_name": ["firstname", "first_name", "given_name"],
            "middle_name": ["middlename", "middle_name"],
            "date_of_birth": ["dob", "dateofbirth", "birth_date"],
            "occupation": ["occupation", "job_title"],
            "address": ["address", "residential_address"],
            "state": ["state", "state_of_origin"],
            "lga": ["lga", "local_government"],
            "ward": ["ward", "registration_ward"],
            "polling_unit": ["polling_unit", "pu", "polling_station"]
        }
        
        for field, form_names in form_fields.items():
            if field in fields:
                for form_name in form_names:
                    form_data[form_name] = fields[field]
        
        pprint(form_data)
        
        # Photo info
        if data.get("profile_photo"):
            print(f"\n📸 Profile Photo: {data['profile_photo']['url']}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# HTML/JavaScript template for form auto-fill
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Voter's Card Auto-fill Form</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        #result { margin-top: 30px; display: none; }
        .photo-preview { max-width: 200px; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Upload Voter's Card for Auto-fill</h2>
    
    <form id="uploadForm" enctype="multipart/form-data">
        <div class="form-group">
            <label>Select Voter's Card Image:</label>
            <input type="file" id="idDocument" accept="image/*" required>
        </div>
        <button type="submit">Extract and Auto-fill Form</button>
    </form>
    
    <div id="result">
        <h3>Extracted Information</h3>
        
        <div class="form-group">
            <label>VIN (Voter ID):</label>
            <input type="text" id="vin" readonly>
        </div>
        
        <div class="form-group">
            <label>Surname:</label>
            <input type="text" id="surname">
        </div>
        
        <div class="form-group">
            <label>First Name:</label>
            <input type="text" id="firstname">
        </div>
        
        <div class="form-group">
            <label>Middle Name:</label>
            <input type="text" id="middlename">
        </div>
        
        <div class="form-group">
            <label>Date of Birth:</label>
            <input type="date" id="dob">
        </div>
        
        <div class="form-group">
            <label>Occupation:</label>
            <input type="text" id="occupation">
        </div>
        
        <div class="form-group">
            <label>Address:</label>
            <textarea id="address" rows="3"></textarea>
        </div>
        
        <div class="form-group">
            <label>State:</label>
            <input type="text" id="state">
        </div>
        
        <div class="form-group">
            <label>LGA:</label>
            <input type="text" id="lga">
        </div>
        
        <div class="form-group">
            <label>Ward:</label>
            <input type="text" id="ward">
        </div>
        
        <div class="form-group">
            <label>Polling Unit:</label>
            <input type="text" id="polling_unit">
        </div>
        
        <div class="form-group">
            <label>Profile Photo:</label>
            <img id="photoPreview" class="photo-preview">
        </div>
        
        <button onclick="submitForm()">Submit Form</button>
    </div>

    <script>
    document.getElementById('uploadForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('idDocument');
        formData.append('file', fileInput.files[0]);
        
        try {
            const response = await fetch('http://localhost:8000/extract-id', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // Auto-fill form fields
            if (data.fields) {
                document.getElementById('vin').value = data.fields.vin || '';
                document.getElementById('surname').value = data.fields.surname || data.fields.full_name?.split(' ')[0] || '';
                document.getElementById('firstname').value = data.fields.first_name || data.fields.full_name?.split(' ')[1] || '';
                document.getElementById('middlename').value = data.fields.middle_name || '';
                document.getElementById('dob').value = formatDate(data.fields.date_of_birth);
                document.getElementById('occupation').value = data.fields.occupation || '';
                document.getElementById('address').value = data.fields.address || '';
                document.getElementById('state').value = data.fields.state || '';
                document.getElementById('lga').value = data.fields.lga || '';
                document.getElementById('ward').value = data.fields.ward || '';
                document.getElementById('polling_unit').value = data.fields.polling_unit || '';
                
                // Load profile photo
                if (data.profile_photo) {
                    document.getElementById('photoPreview').src = `http://localhost:8000${data.profile_photo.url}`;
                }
            }
            
            document.getElementById('result').style.display = 'block';
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error processing image: ' + error.message);
        }
    });
    
    function formatDate(dateStr) {
        if (!dateStr) return '';
        // Convert DD-MM-YYYY to YYYY-MM-DD for date input
        const parts = dateStr.split('-');
        if (parts.length === 3) {
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return dateStr;
    }
    
    function submitForm() {
        const formData = {
            vin: document.getElementById('vin').value,
            surname: document.getElementById('surname').value,
            firstname: document.getElementById('firstname').value,
            middlename: document.getElementById('middlename').value,
            dob: document.getElementById('dob').value,
            occupation: document.getElementById('occupation').value,
            address: document.getElementById('address').value,
            state: document.getElementById('state').value,
            lga: document.getElementById('lga').value,
            ward: document.getElementById('ward').value,
            polling_unit: document.getElementById('polling_unit').value
        };
        
        console.log('Form submitted:', formData);
        alert('Form data ready for submission! Check console for details.');
    }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # Test with your image
    image_path = "voters_card.jpeg"  # Update with your image path
    result = test_voters_card_extraction(image_path)
    
    # Save HTML template to file
    with open("voter_form_autofill.html", "w") as f:
        f.write(HTML_TEMPLATE)
    print("\n✅ HTML form template saved as 'voter_form_autofill.html'")