# test_all_documents.py
import requests
import json
from pprint import pprint

def test_document_extraction(image_path, doc_type=None):
    """
    Test document extraction
    """
    url = "http://localhost:8000/extract-id"
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        
        print("=" * 60)
        print(f"DOCUMENT TYPE: {data.get('document_type', 'UNKNOWN').upper()}")
        print("=" * 60)
        
        print(f"\n📄 Confidence: {data.get('confidence', 0)}")
        print(f"🌍 Country: {data.get('country', 'unknown')}")
        
        print("\n📋 EXTRACTED FIELDS:")
        print("-" * 30)
        fields = data.get("fields", {})
        
        for key, value in fields.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        if data.get("profile_photo"):
            print(f"\n📸 Profile Photo: {data['profile_photo']['url']}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# HTML Template for Universal Form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Universal ID Auto-fill Form</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 8px; box-sizing: border-box; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; margin-right: 10px; }
        button.secondary { background: #6c757d; }
        #result { margin-top: 30px; display: none; }
        .photo-preview { max-width: 200px; margin-top: 10px; border: 1px solid #ddd; padding: 5px; }
        .doc-type-badge { 
            display: inline-block; 
            padding: 5px 10px; 
            background: #28a745; 
            color: white; 
            border-radius: 3px;
            margin-bottom: 20px;
        }
        .field-group {
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .field-group h4 {
            margin-top: 0;
            color: #007bff;
        }
    </style>
</head>
<body>
    <h2>Universal ID Document Auto-fill</h2>
    <p>Upload any ID document (Voter's Card, NIN, Passport, Driver's License)</p>
    
    <form id="uploadForm" enctype="multipart/form-data">
        <div class="form-group">
            <label>Select ID Document Image:</label>
            <input type="file" id="idDocument" accept="image/*" required>
        </div>
        <button type="submit">Extract and Auto-fill Form</button>
        <button type="button" class="secondary" onclick="clearForm()">Clear Form</button>
    </form>
    
    <div id="result">
        <div id="docTypeBadge" class="doc-type-badge"></div>
        
        <div class="field-group">
            <h4>Personal Information</h4>
            <div class="form-group">
                <label>Full Name:</label>
                <input type="text" id="full_name" readonly>
            </div>
            
            <div class="form-group">
                <label>Surname:</label>
                <input type="text" id="surname">
            </div>
            
            <div class="form-group">
                <label>First Name:</label>
                <input type="text" id="first_name">
            </div>
            
            <div class="form-group">
                <label>Middle Name:</label>
                <input type="text" id="middle_name">
            </div>
            
            <div class="form-group">
                <label>Date of Birth:</label>
                <input type="date" id="date_of_birth">
            </div>
            
            <div class="form-group">
                <label>Gender:</label>
                <select id="gender">
                    <option value="">Select</option>
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                </select>
            </div>
        </div>
        
        <div class="field-group">
            <h4>Document Information</h4>
            <div class="form-group" id="docNumberGroup">
                <label id="docNumberLabel">Document Number:</label>
                <input type="text" id="document_number">
            </div>
            
            <div class="form-group" id="issueDateGroup">
                <label>Issue Date:</label>
                <input type="date" id="issue_date">
            </div>
            
            <div class="form-group" id="expiryDateGroup">
                <label>Expiry Date:</label>
                <input type="date" id="expiry_date">
            </div>
        </div>
        
        <div class="field-group">
            <h4>Contact Information</h4>
            <div class="form-group">
                <label>Address:</label>
                <textarea id="address" rows="3"></textarea>
            </div>
            
            <div class="form-group">
                <label>Phone Number:</label>
                <input type="tel" id="phone_number">
            </div>
            
            <div class="form-group">
                <label>State:</label>
                <input type="text" id="state">
            </div>
            
            <div class="form-group">
                <label>LGA:</label>
                <input type="text" id="lga">
            </div>
        </div>
        
        <div class="field-group">
            <h4>Additional Information</h4>
            <div class="form-group" id="occupationGroup">
                <label>Occupation:</label>
                <input type="text" id="occupation">
            </div>
            
            <div class="form-group" id="bloodGroupGroup">
                <label>Blood Group:</label>
                <input type="text" id="blood_group">
            </div>
            
            <div class="form-group" id="heightGroup">
                <label>Height:</label>
                <input type="text" id="height">
            </div>
            
            <div class="form-group" id="nationalityGroup">
                <label>Nationality:</label>
                <input type="text" id="nationality">
            </div>
            
            <div class="form-group" id="placeOfBirthGroup">
                <label>Place of Birth:</label>
                <input type="text" id="place_of_birth">
            </div>
        </div>
        
        <div class="field-group">
            <h4>Profile Photo</h4>
            <img id="photoPreview" class="photo-preview">
            <div>
                <button type="button" onclick="downloadPhoto()">Download Photo</button>
            </div>
        </div>
        
        <button onclick="submitForm()">Submit Form</button>
        <button type="button" class="secondary" onclick="viewJSON()">View JSON Data</button>
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
            console.log('Extracted data:', data);
            
            if (data.success) {
                // Show document type
                const docType = data.document_type || 'unknown';
                document.getElementById('docTypeBadge').textContent = 
                    `Detected: ${docType.replace('_', ' ').toUpperCase()} (Confidence: ${data.confidence})`;
                
                // Auto-fill form based on document type
                fillForm(data.fields, docType);
                
                // Load photo
                if (data.profile_photo) {
                    document.getElementById('photoPreview').src = 
                        `http://localhost:8000${data.profile_photo.url}`;
                }
                
                document.getElementById('result').style.display = 'block';
            } else {
                alert('Error processing document: ' + (data.error || 'Unknown error'));
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error processing image: ' + error.message);
        }
    });
    
    function fillForm(fields, docType) {
        // Clear all fields first
        clearForm();
        
        // Common fields
        setFieldValue('full_name', fields.full_name);
        setFieldValue('surname', fields.surname);
        setFieldValue('first_name', fields.first_name);
        setFieldValue('middle_name', fields.middle_name);
        setFieldValue('date_of_birth', formatDate(fields.date_of_birth));
        setFieldValue('gender', fields.gender);
        setFieldValue('address', fields.address);
        setFieldValue('phone_number', fields.phone_number);
        setFieldValue('state', fields.state);
        setFieldValue('lga', fields.lga);
        
        // Document type specific fields
        switch(docType) {
            case 'voters_card':
                setFieldValue('document_number', fields.vin);
                document.getElementById('docNumberLabel').textContent = 'VIN (Voter ID):';
                setFieldValue('occupation', fields.occupation);
                showField('occupationGroup');
                break;
                
            case 'nin':
                setFieldValue('document_number', fields.nin);
                document.getElementById('docNumberLabel').textContent = 'NIN Number:';
                break;
                
            case 'international_passport':
                setFieldValue('document_number', fields.passport_number);
                document.getElementById('docNumberLabel').textContent = 'Passport Number:';
                setFieldValue('issue_date', formatDate(fields.issue_date));
                setFieldValue('expiry_date', formatDate(fields.expiry_date));
                setFieldValue('nationality', fields.nationality);
                setFieldValue('place_of_birth', fields.place_of_birth);
                showField('issueDateGroup');
                showField('expiryDateGroup');
                showField('nationalityGroup');
                showField('placeOfBirthGroup');
                break;
                
            case 'drivers_license':
                setFieldValue('document_number', fields.license_number);
                document.getElementById('docNumberLabel').textContent = 'License Number:';
                setFieldValue('issue_date', formatDate(fields.issue_date));
                setFieldValue('expiry_date', formatDate(fields.expiry_date));
                setFieldValue('blood_group', fields.blood_group);
                setFieldValue('height', fields.height);
                showField('issueDateGroup');
                showField('expiryDateGroup');
                showField('bloodGroupGroup');
                showField('heightGroup');
                break;
        }
    }
    
    function setFieldValue(id, value) {
        const element = document.getElementById(id);
        if (element && value) {
            element.value = value;
        }
    }
    
    function showField(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'block';
        }
    }
    
    function hideField(id) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    }
    
    function formatDate(dateStr) {
        if (!dateStr) return '';
        // Convert DD-MM-YYYY to YYYY-MM-DD
        const parts = dateStr.split('-');
        if (parts.length === 3 && parts[2].length === 4) {
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return dateStr;
    }
    
    function clearForm() {
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => input.value = '');
        document.getElementById('photoPreview').src = '';
        
        // Hide conditional fields
        ['issueDateGroup', 'expiryDateGroup', 'occupationGroup', 
         'bloodGroupGroup', 'heightGroup', 'nationalityGroup', 
         'placeOfBirthGroup'].forEach(id => hideField(id));
    }
    
    function downloadPhoto() {
        const photoSrc = document.getElementById('photoPreview').src;
        if (photoSrc) {
            window.open(photoSrc, '_blank');
        }
    }
    
    function submitForm() {
        const formData = {
            personal_info: {
                full_name: document.getElementById('full_name').value,
                surname: document.getElementById('surname').value,
                first_name: document.getElementById('first_name').value,
                middle_name: document.getElementById('middle_name').value,
                date_of_birth: document.getElementById('date_of_birth').value,
                gender: document.getElementById('gender').value
            },
            document_info: {
                document_number: document.getElementById('document_number').value,
                issue_date: document.getElementById('issue_date').value,
                expiry_date: document.getElementById('expiry_date').value
            },
            contact_info: {
                address: document.getElementById('address').value,
                phone_number: document.getElementById('phone_number').value,
                state: document.getElementById('state').value,
                lga: document.getElementById('lga').value
            },
            additional_info: {
                occupation: document.getElementById('occupation').value,
                blood_group: document.getElementById('blood_group').value,
                height: document.getElementById('height').value,
                nationality: document.getElementById('nationality').value,
                place_of_birth: document.getElementById('place_of_birth').value
            }
        };
        
        console.log('Form Data:', formData);
        alert('Form data ready! Check console for details.');
        
        // You can send this to your backend
        // fetch('/api/submit-form', {
        //     method: 'POST',
        //     headers: {'Content-Type': 'application/json'},
        //     body: JSON.stringify(formData)
        // });
    }
    
    function viewJSON() {
        const formData = {
            full_name: document.getElementById('full_name').value,
            surname: document.getElementById('surname').value,
            first_name: document.getElementById('first_name').value,
            middle_name: document.getElementById('middle_name').value,
            date_of_birth: document.getElementById('date_of_birth').value,
            gender: document.getElementById('gender').value,
            document_number: document.getElementById('document_number').value,
            issue_date: document.getElementById('issue_date').value,
            expiry_date: document.getElementById('expiry_date').value,
            address: document.getElementById('address').value,
            phone_number: document.getElementById('phone_number').value,
            state: document.getElementById('state').value,
            lga: document.getElementById('lga').value,
            occupation: document.getElementById('occupation').value,
            blood_group: document.getElementById('blood_group').value,
            height: document.getElementById('height').value,
            nationality: document.getElementById('nationality').value,
            place_of_birth: document.getElementById('place_of_birth').value
        };
        
        alert(JSON.stringify(formData, null, 2));
    }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # Test with different document types
    documents = {
        "voters_card": "voters_card.jpeg",
        "nin": "nin_card.jpg", 
        "passport": "passport.jpg",
        "drivers_license": "license.jpg"
    }
    
    for doc_type, path in documents.items():
        print(f"\nTesting {doc_type}...")
        result = test_document_extraction(path)
    
    # Save HTML template
    with open("universal_id_form.html", "w") as f:
        f.write(HTML_TEMPLATE)
    print("\n✅ Universal form saved as 'universal_id_form.html'")