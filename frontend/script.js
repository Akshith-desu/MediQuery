// Global variables
let map;
let userMarker;
let doctorMarkers = [];
let userLocation = null;

// Initialize Google Map
window.initMap = function() {
    const defaultLocation = { lat: 12.9716, lng: 77.5946 }; // Bangalore
    
    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultLocation,
        zoom: 12,
        styles: [
            {
                "featureType": "poi.medical",
                "elementType": "geometry",
                "stylers": [{"color": "#ffdede"}]
            }
        ]
    });
    
    console.log("✅ Map initialized successfully");
};

// Update distance slider display
function updateDistance(value) {
    document.getElementById('distanceValue').textContent = value + ' km';
}

// Get user's current location
function getMyLocation() {
    if (navigator.geolocation) {
        document.getElementById('results').innerHTML = 
            '<div class="loading">📍 Getting your location...</div>';
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                map.setCenter(userLocation);
                map.setZoom(13);
                
                if (userMarker) userMarker.setMap(null);
                userMarker = new google.maps.Marker({
                    position: userLocation,
                    map: map,
                    title: "Your Location",
                    icon: {
                        url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
                    }
                });
                
                document.getElementById('results').innerHTML = 
                    '<div class="loading">✅ Location found! Enter symptoms to search.</div>';
            },
            (error) => {
                document.getElementById('results').innerHTML = 
                    '<div class="error">❌ Could not get location. Using default area.</div>';
            }
        );
    } else {
        alert("Geolocation is not supported by your browser");
    }
}

// Search for doctors based on symptoms
async function searchDoctors() {
    const symptoms = document.getElementById('symptoms').value.trim();
    const maxDistance = document.getElementById('distanceRange').value;
    
    if (!symptoms) {
        alert("Please enter your symptoms");
        return;
    }
    
    document.getElementById('results').innerHTML = 
        '<div class="loading">🔍 Analyzing symptoms and finding doctors...</div>';
    
    // Clear previous markers
    doctorMarkers.forEach(marker => marker.setMap(null));
    doctorMarkers = [];
    
    try {
        const response = await fetch("http://127.0.0.1:5000/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                symptoms: symptoms,
                latitude: userLocation?.lat,
                longitude: userLocation?.lng,
                max_distance_km: parseInt(maxDistance)
            })
        });
        
        const data = await response.json();

// 🔍 DEBUG: Log the entire response
        console.log("🔍 FULL BACKEND RESPONSE:");
        console.log(JSON.stringify(data, null, 2));

        // 🔍 DEBUG: Check follow-up questions specifically
        if (data.matches && data.matches.length > 0) {
            data.matches.forEach((match, idx) => {
                console.log(`\n✨ Match ${idx + 1}: ${match.disease}`);
                console.log(`   Follow-up questions:`, match.follow_up_questions);
                console.log(`   Questions count: ${match.follow_up_questions?.length || 0}`);
            });
        }

        displayResults(data);
        
    } catch (error) {
        console.error("Search error:", error);
        document.getElementById('results').innerHTML = 
            '<div class="error">❌ Error connecting to server. Please try again.</div>';
    }
}

// Display search results
function displayResults(data) {
    if (!data.matches || data.matches.length === 0) {
        document.getElementById('results').innerHTML = 
            '<div class="error">No matching diseases or doctors found.</div>';
        return;
    }
    
    let html = '<div class="results">';
    
    data.matches.forEach((match, index) => {
        const confidenceClass = 
            match.confidence > 0.7 ? 'confidence-high' :
            match.confidence > 0.4 ? 'confidence-medium' : 'confidence-low';
        
        html += `
            <div class="disease-card">
                <h2>
                    ${index + 1}. ${match.disease}
                    <span class="confidence-badge ${confidenceClass}">
                        ${Math.round(match.confidence * 100)}% Match
                    </span>
                </h2>
                <p><strong>Matched Symptoms:</strong> ${match.matched_symptoms.join(', ')}</p>
        `;
        
        if (match.requires_urgent_care) {
            html += `
                <div class="urgent-care">
                    ⚠️ <strong>Urgent Care Recommended</strong> - Consider immediate medical attention
                </div>
            `;
        }

        // Show follow-up questions if available
        // 🔍 DEBUG: Check if follow-up questions exist
        console.log(`\n🔍 Checking follow-up for ${match.disease}:`);
        console.log(`   Has follow_up_questions? ${!!match.follow_up_questions}`);
        console.log(`   Is array? ${Array.isArray(match.follow_up_questions)}`);
        console.log(`   Length: ${match.follow_up_questions?.length || 0}`);

        // Show follow-up questions if available
        if (match.follow_up_questions && match.follow_up_questions.length > 0) {
            console.log(`   ✅ Calling displayFollowUpQuestions()`);
            html += displayFollowUpQuestions(match.disease, match.follow_up_questions);
        } else {
            console.log(`   ❌ NOT showing follow-up questions`);
        }
        
        if (match.doctors && match.doctors.length > 0) {
            html += '<div class="doctor-list">';
            
            match.doctors.forEach(doctor => {
                // Add marker to map for each doctor
                const marker = new google.maps.Marker({
                    position: { 
                        lat: parseFloat(doctor.latitude), 
                        lng: parseFloat(doctor.longitude) 
                    },
                    map: map,
                    title: doctor.doctor_name + ' - ' + doctor.hospital_name,
                    icon: {
                        url: "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
                    }
                });
                
                // Add click event to marker
                marker.addListener('click', () => {
                    new google.maps.InfoWindow({
                        content: `
                            <strong>${doctor.doctor_name}</strong><br>
                            ${doctor.hospital_name}<br>
                            ${doctor.distance_km ? doctor.distance_km + ' km away' : ''}
                        `
                    }).open(map, marker);
                });
                
                doctorMarkers.push(marker);
                
                // Build doctor card HTML
                html += `
                    <div class="doctor-card">
                        <div class="doctor-name">👨‍⚕️ ${doctor.doctor_name}</div>
                        <div class="doctor-info">
                            <span class="icon">🏥</span>
                            ${doctor.hospital_name}
                        </div>
                        <div class="doctor-info">
                            <span class="icon">🎯</span>
                            ${doctor.specialization}
                        </div>
                        ${doctor.distance_km ? 
                            `<span class="distance-badge">📍 ${doctor.distance_km} km away</span>` 
                            : ''}
                        ${doctor.success_rate ? 
                            `<div class="doctor-info">
                                <span class="icon">⭐</span>
                                ${doctor.success_rate}% Success Rate (${doctor.total_cases} cases)
                            </div>` 
                            : ''}
                        ${doctor.base_fee ? 
                            `<div class="doctor-info">
                                <span class="icon">💰</span>
                                ₹${doctor.base_fee} consultation
                            </div>` 
                            : ''}
                        
                        ${doctor.available_slots && doctor.available_slots.length > 0 ? `
                            <div class="slots">
                                <strong>Available Slots:</strong><br>
                                ${doctor.available_slots.map(slot => 
                                    `<button class="slot-btn" onclick="bookSlot(${slot.slot_id}, ${doctor.doctor_id})">
                                        ${slot.slot_date} ${slot.slot_time}
                                    </button>`
                                ).join('')}
                            </div>
                        ` : '<p style="color: #999; margin-top: 10px;">No slots available</p>'}
                    </div>
                `;
            });
            
            html += '</div>';
        } else {
            html += '<p>No doctors found in your area for this condition.</p>';
        }
        
        html += '</div>';
    });
    
    html += '</div>';
    document.getElementById('results').innerHTML = html;
    
    // Fit map to show all markers
    if (doctorMarkers.length > 0 && map) {
        const bounds = new google.maps.LatLngBounds();
        if (userMarker) bounds.extend(userMarker.getPosition());
        doctorMarkers.forEach(marker => bounds.extend(marker.getPosition()));
        map.fitBounds(bounds);
    }
}

function displayFollowUpQuestions(disease, questions) {
    let html = `
        <div class="followup-section">
            <h3>🤔 Help us understand better - Answer a few questions about ${disease}:</h3>
            <form id="followupForm-${disease.replace(/\s/g, '')}">
    `;
    
    questions.forEach((q, idx) => {
        if (q.type === "yes_no") {
            html += `
                <div class="followup-question">
                    <p><strong>${idx + 1}. ${q.question}</strong></p>
                    <label>
                        <input type="radio" name="q${idx}" value="yes" required> Yes
                    </label>
                    <label>
                        <input type="radio" name="q${idx}" value="no"> No
                    </label>
                </div>
            `;
        } else if (q.type === "multiple_choice") {
            html += `
                <div class="followup-question">
                    <p><strong>${idx + 1}. ${q.question}</strong></p>
                    ${q.options.map(opt => `
                        <label>
                            <input type="radio" name="q${idx}" value="${opt}" required> ${opt}
                        </label>
                    `).join('')}
                </div>
            `;
        }
    });
    
    html += `
                <button type="button" onclick="submitFollowUp('${disease}', ${questions.length})" class="btn-primary">
                    Submit Answers
                </button>
            </form>
        </div>
    `;
    
    return html;
}

// Book appointment slot
async function bookSlot(slotId, doctorId) {
    // Always prompt for patient details on every booking
    let patientId = prompt("Enter your Patient ID (or any number for new user):");
    if (!patientId) {
        alert("Patient ID is required");
        return;
    }

    let patientName = prompt("Enter your full name:");
    if (!patientName) patientName = "Guest Patient";
    
    try {
        const response = await fetch("http://127.0.0.1:5000/book-appointment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                slot_id: slotId,
                patient_id: parseInt(patientId),
                patient_name: patientName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Appointment Booked!
            
Doctor: ${data.appointment_details.doctor}
Hospital: ${data.appointment_details.hospital}
Date: ${data.appointment_details.date}
Time: ${data.appointment_details.time}
Fee: ₹${data.appointment_details.fee || 'TBD'}

Booking ID: ${data.booking_id}`);
            
            searchDoctors();  // Refresh
        } else {
            alert("❌ " + data.error);
        }
    } catch (error) {
        alert("❌ Booking failed: " + error);
    }
}

async function submitFollowUp(disease, numQuestions) {
    const form = document.getElementById(`followupForm-${disease.replace(/\s/g, '')}`);
    const formData = new FormData(form);
    
    // Build answers object
    const answers = {};
    const questions = Array.from(form.querySelectorAll('.followup-question p strong'));
    
    for (let i = 0; i < numQuestions; i++) {
        const questionText = questions[i].textContent.replace(/^\d+\.\s*/, '');
        const answer = formData.get(`q${i}`);
        answers[questionText] = answer;
    }
    
    // Get original symptoms
    const originalSymptoms = document.getElementById('symptoms').value;
    
    // Show loading
    document.getElementById('results').innerHTML = 
        '<div class="loading">🔄 Refining diagnosis based on your answers...</div>';
    
    try {
        const response = await fetch("http://127.0.0.1:5000/submit-followup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                original_symptoms: originalSymptoms,
                follow_up_answers: answers
            })
        });
        
        const data = await response.json();
        
        // Display refined results
        displayResults({ matches: data.refined_matches });
        
    } catch (error) {
        console.error("Follow-up error:", error);
        alert("❌ Failed to process answers. Please try again.");
    }
}

// View My Appointments
async function viewMyAppointments() {
    const patientId = prompt("Enter your Patient ID to view appointments:");
    
    if (!patientId) {
        alert("Patient ID is required");
        return;
    }
    
    document.getElementById('appointmentsList').innerHTML = 
        '<div class="loading">Loading appointments...</div>';
    document.getElementById('appointmentsModal').style.display = 'block';
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/appointment-history/${patientId}`);
        const data = await response.json();
        
        if (data.appointments && data.appointments.length > 0) {
            let html = '';
            
            data.appointments.forEach(apt => {
                const isCancelled = apt.status === 'cancelled';
                
                html += `
                    <div class="appointment-card" style="${isCancelled ? 'opacity: 0.6; border-left: 4px solid #dc3545;' : ''}">
                        <h3>👨‍⚕️ Dr. ${apt.doctor_name}</h3>
                        <div class="appointment-detail">
                            <span class="icon">🎯</span>
                            <span>${apt.specialization}</span>
                        </div>
                        <div class="appointment-detail">
                            <span class="icon">🏥</span>
                            <span>${apt.hospital_name} - ${apt.location}</span>
                        </div>
                        <div class="appointment-detail">
                            <span class="icon">📅</span>
                            <span><strong>${apt.appointment_date}</strong> at <strong>${apt.appointment_time}</strong></span>
                        </div>
                        ${apt.consultation_fee ? `
                            <div class="appointment-detail">
                                <span class="icon">💰</span>
                                <span>₹${apt.consultation_fee}</span>
                            </div>
                        ` : ''}
                        <div class="appointment-detail">
                            <span class="icon">🕐</span>
                            <span>Booked: ${new Date(apt.booking_timestamp).toLocaleString()}</span>
                        </div>
                        <span class="status-badge" style="background: ${isCancelled ? '#dc3545' : '#28a745'}">
                            ${isCancelled ? '✗ CANCELLED' : '✓ CONFIRMED'}
                        </span>
                        ${!isCancelled ? `
                            <button onclick="cancelAppointment('${apt.booking_id}')" 
                                    style="margin-top: 10px; background: #dc3545; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer;">
                                Cancel Appointment
                            </button>
                        ` : `
                            <div style="color: #999; margin-top: 10px; font-size: 0.9em;">
                                Cancelled on: ${new Date(apt.cancelled_at).toLocaleString()}
                            </div>
                        `}
                    </div>
                `;
            });
            
            document.getElementById('appointmentsList').innerHTML = html;
        } else {
            document.getElementById('appointmentsList').innerHTML = `
                <div class="no-appointments">
                    <h3>📭 No Appointments Yet</h3>
                    <p>Book your first appointment!</p>
                </div>
            `;
        }
        
    } catch (error) {
        document.getElementById('appointmentsList').innerHTML = 
            '<div class="error">❌ Failed to load appointments</div>';
    }
}

// Close Appointments Modal
function closeAppointments() {
    document.getElementById('appointmentsModal').style.display = 'none';
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('appointmentsModal');
    if (event.target === modal) {
        closeAppointments();
    }
});

// Cancel appointment
async function cancelAppointment(bookingId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
    }
    
    const patientId = prompt("Enter your Patient ID to confirm cancellation:");

    if (!patientId) {
        alert("Patient ID is required");
        return;
    }
    
    try {
        const response = await fetch("http://127.0.0.1:5000/cancel-appointment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                booking_id: bookingId,
                patient_id: parseInt(patientId)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert("✅ Appointment cancelled successfully");
            viewMyAppointments();  // Refresh the list
        } else {
            alert("❌ " + data.error);
        }
    } catch (error) {
        alert("❌ Cancellation failed: " + error);
    }
}

// ============================================
// PRESCRIPTION MANAGEMENT FUNCTIONS
// ============================================

// Upload Prescription
async function uploadPrescription() {
    const patientId = prompt("Enter your Patient ID:");
    
    if (!patientId) {
        alert("Patient ID is required");
        return;
    }
    
    // Create file input dynamically
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*,application/pdf';
    
    fileInput.onchange = async (e) => {
        const file = e.target.files[0];
        
        if (!file) return;
        
        // Show loading
        document.getElementById('results').innerHTML = 
            '<div class="loading">📄 Uploading and processing prescription...</div>';
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('patient_id', patientId);
            
            const response = await fetch("http://127.0.0.1:5000/upload-prescription", {
                method: "POST",
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Display extracted data
                displayExtractedPrescription(data.extracted_data);
                alert("✅ Prescription uploaded successfully!");
            } else {
                alert("❌ " + data.error);
            }
            
        } catch (error) {
            console.error("Upload error:", error);
            alert("❌ Failed to upload prescription");
        }
    };
    
    fileInput.click();
}

// Display extracted prescription data
function displayExtractedPrescription(data) {
    let html = `
        <div class="results">
            <div class="disease-card">
                <h2>📄 Prescription Details (Extracted)</h2>
                
                ${data.doctor_name ? `<p><strong>Doctor:</strong> ${data.doctor_name}</p>` : ''}
                ${data.hospital ? `<p><strong>Hospital:</strong> ${data.hospital}</p>` : ''}
                ${data.patient_name ? `<p><strong>Patient:</strong> ${data.patient_name}</p>` : ''}
                ${data.date ? `<p><strong>Date:</strong> ${data.date}</p>` : ''}
                
                ${data.medicines && data.medicines.length > 0 ? `
                    <h3 style="margin-top: 20px;">Medicines:</h3>
                    <div class="doctor-list">
                        ${data.medicines.map(med => `
                            <div class="doctor-card">
                                <div class="doctor-name">${med.name} - ${med.dosage}</div>
                                <p style="margin: 10px 0;">${med.instructions}</p>
                                ${med.frequency ? `<p><strong>Frequency:</strong> ${med.frequency}</p>` : ''}
                                ${med.duration ? `<p><strong>Duration:</strong> ${med.duration}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : '<p style="color: #999;">No medicines detected</p>'}
                
                ${data.follow_up_date ? `
                    <p style="margin-top: 15px;"><strong>Follow-up:</strong> ${data.follow_up_date}</p>
                ` : ''}
                
                <details style="margin-top: 20px;">
                    <summary style="cursor: pointer; color: #667eea;">View Raw OCR Text</summary>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 10px;">${data.raw_text}</pre>
                </details>
            </div>
        </div>
    `;
    
    document.getElementById('results').innerHTML = html;
}

// View My Prescriptions
async function viewMyPrescriptions() {
    const patientId = prompt("Enter your Patient ID:");
    
    if (!patientId) {
        alert("Patient ID is required");
        return;
    }
    
    document.getElementById('prescriptionsModal').style.display = 'block';
    document.getElementById('prescriptionsList').innerHTML = 
        '<div class="loading">Loading prescriptions...</div>';
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/prescriptions/${patientId}`);
        const data = await response.json();
        
        if (data.prescriptions && data.prescriptions.length > 0) {
            let html = '';
            
            data.prescriptions.forEach(presc => {
                html += `
                    <div class="appointment-card">
                        <h3> ${presc.filename}</h3>
                        <div class="appointment-detail">
                            <span class="icon"></span>
                            <span>Uploaded: ${new Date(presc.upload_date).toLocaleString()}</span>
                        </div>
                        
                        ${presc.ocr_data.doctor_name ? `
                            <div class="appointment-detail">
                                <span class="icon"></span>
                                <span>Dr. ${presc.ocr_data.doctor_name}</span>
                            </div>
                        ` : ''}
                        
                        ${presc.ocr_data.hospital ? `
                            <div class="appointment-detail">
                                <span class="icon"></span>
                                <span>${presc.ocr_data.hospital}</span>
                            </div>
                        ` : ''}
                        
                        ${presc.ocr_data.medicines && presc.ocr_data.medicines.length > 0 ? `
                            <div class="appointment-detail">
                                <span class="icon"></span>
                                <span>${presc.ocr_data.medicines.length} medicines prescribed</span>
                            </div>
                        ` : ''}
                        
                        <button onclick="viewPrescriptionDetails('${presc.prescription_id}')" 
                                style="margin-top: 10px; background: #667eea; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer;">
                            View Details
                        </button>
                        
                        
                        <button onclick="downloadPrescription('${presc.prescription_id}', '${presc.filename}')" 
                                style="margin-top: 10px; background: #28a745; color: white; padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer;">
                             Download
                        </button>
                    </div>
                `;
            });
            
            document.getElementById('prescriptionsList').innerHTML = html;
        } else {
            document.getElementById('prescriptionsList').innerHTML = `
                <div class="no-appointments">
                    <h3>📭 No Prescriptions Yet</h3>
                    <p>Upload your first prescription!</p>
                </div>
            `;
        }
        
    } catch (error) {
        document.getElementById('prescriptionsList').innerHTML = 
            '<div class="error">❌ Failed to load prescriptions</div>';
    }
}

// View prescription details
// Add this to your existing script.js - Replace the viewPrescriptionDetails function

// View prescription details in modal
async function viewPrescriptionDetails(prescriptionId) {
    try {
        // Fetch prescription data
        const patientId = prompt("Enter your Patient ID:");
        if (!patientId) return;
        
        const response = await fetch(`http://127.0.0.1:5000/prescriptions/${patientId}`);
        const data = await response.json();
        
        // Find the specific prescription
        const prescription = data.prescriptions.find(p => p.prescription_id === prescriptionId);
        
        if (!prescription) {
            alert("Prescription not found");
            return;
        }
        
        // Display in modal
        const prescData = prescription.ocr_data;
        
        let html = `
            <div class="prescription-details">
                <h2>Prescription Details</h2>
                
                ${prescData.doctor_name ? `
                    <div class="detail-row">
                        <strong>Doctor:</strong> Dr. ${prescData.doctor_name}
                    </div>
                ` : ''}
                
                ${prescData.hospital ? `
                    <div class="detail-row">
                        <strong>Hospital:</strong> ${prescData.hospital}
                    </div>
                ` : ''}
                
                ${prescData.patient_name ? `
                    <div class="detail-row">
                        <strong>Patient:</strong> ${prescData.patient_name}
                    </div>
                ` : ''}
                
                ${prescData.date ? `
                    <div class="detail-row">
                        <strong>Date:</strong> ${prescData.date}
                    </div>
                ` : ''}
                
                ${prescData.medicines && prescData.medicines.length > 0 ? `
                    <h3 style="margin-top: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                        Medicines Prescribed
                    </h3>
                    <div class="medicines-grid">
                        ${prescData.medicines.map((med, idx) => `
                            <div class="medicine-card" style="background:  #1e1e2f; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #333;">
                                <h4 style="margin: 0 0 10px 0; color: white;">${idx + 1}. ${med.name}</h4>
                                <p style="margin: 5px 0; color: white;"><strong>Dosage:</strong> ${med.dosage}</p>
                                <p style="margin: 5px 0; color: white;"><strong>Instructions:</strong> ${med.instructions}</p>
                                ${med.frequency ? `<p style="margin: 5px 0;"><strong>Frequency:</strong> ${med.frequency}</p>` : ''}
                                ${med.duration ? `<p style="margin: 5px 0;"><strong>Duration:</strong> ${med.duration}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : '<p style="color: #999; margin-top: 15px;">No medicines detected in this prescription</p>'}
                
                ${false && prescData.follow_up_date ? `
                    <div class="detail-row" style="margin-top: 20px; padding: 15px; background: #9e8225; border-radius: 8px;">
                        <strong> Follow-up Date:</strong> ${prescData.follow_up_date}
                    </div>
                ` : ''}
                
                <details style="margin-top: 25px; border: 1px solid #ddd; padding: 15px; border-radius: 8px;">
                    <summary style="cursor: pointer; color: #667eea; font-weight: bold;">
                         View Raw OCR Text
                    </summary>
                    <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 10px; font-size: 12px; line-height: 1.5;">${prescData.raw_text}</pre>
                </details>
                
                <div style="margin-top: 25px; padding-top: 20px; border-top: 2px solid #eee;">
                    <button onclick="generateShareLink('${prescriptionId}', ${patientId})" 
                            style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-right: 10px;">
                        🔗 Generate Shareable Link
                    </button>
                    
                    <button onclick="downloadPrescription('${prescriptionId}', '${prescription.filename}')" 
                            style="background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;">
                        📥 Download Original
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('prescriptionsList').innerHTML = html;
        
    } catch (error) {
        console.error("Error loading prescription details:", error);
        alert("❌ Failed to load prescription details");
    }
    
}

// Generate shareable link for prescription
async function generateShareLink(prescriptionId, patientId) {
    const expiryHours = prompt("Link valid for how many hours? (Default: 24)", "24");
    const requirePassword = confirm("Do you want to password-protect this link?");
    
    let password = null;
    if (requirePassword) {
        password = prompt("Enter a password for this link:");
        if (!password) {
            alert("Password is required!");
            return;
        }
    }
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/generate-share-link/${patientId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                expiry_hours: parseInt(expiryHours) || 24,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create a nice modal to show the link
            const linkHtml = `
                <div style="background: black; padding: 30px; border-radius: 10px; max-width: 600px; margin: 20px auto;">
                    <h2 style="color: #28a745; margin-bottom: 20px;">Shareable Link Generated</h2>
                    
                    <div style="background: #db4c51; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; word-break: break-all; font-family: monospace; font-size: 14px;">
                            ${data.share_url}
                        </p>
                    </div>
                    
                    <div style="background: #369f44; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Expires:</strong> ${new Date(data.expires_at).toLocaleString()}</p>
                        <p style="margin: 5px 0;"><strong>Password Protected:</strong> ${data.requires_password ? 'Yes' : 'No'}</p>
                    </div>
                    
                    <button onclick="copyShareLink('${data.share_url}')" 
                            style="background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; margin-top: 10px;">
                            Copy Link to Clipboard
                    </button>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 20px; text-align: center;">
                        Share this link with doctors, family members, or healthcare providers
                    </p>
                </div>
            `;
            
            document.getElementById('prescriptionsList').innerHTML = linkHtml;
            
        } else {
            alert("❌ Failed to generate link: " + data.error);
        }
        
    } catch (error) {
        console.error("Error generating share link:", error);
        alert("❌ Failed to generate shareable link");
    }
}

// Copy link to clipboard
function copyShareLink(url) {
    navigator.clipboard.writeText(url).then(() => {
        alert("✅ Link copied to clipboard!");
    }).catch(err => {
        alert("❌ Failed to copy link. Please copy manually:\n\n" + url);
    });
}

// View shared prescription (for recipients)
async function viewSharedPrescription() {
    const token = prompt("Enter the share token/link you received:");
    
    if (!token) return;
    
    // Extract token from URL if full URL provided
    const tokenMatch = token.match(/view-shared\/([a-zA-Z0-9_-]+)/);
    const actualToken = tokenMatch ? tokenMatch[1] : token;
    
    const password = prompt("Enter password (leave blank if no password):");
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/view-shared/${actualToken}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password: password || null })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display shared prescriptions
            displaySharedPrescriptions(data.prescriptions);
        } else {
            alert("❌ " + data.error);
        }
        
    } catch (error) {
        console.error("Error viewing shared prescription:", error);
        alert("❌ Failed to access shared prescription");
    }
}

// Display shared prescriptions
// Replace the displaySharedPrescriptions function in script.js

function displaySharedPrescriptions(prescriptions) {
    let html = `
        <div class="results" style="padding: 20px;">
            <div class="disease-card" style="background: linear-gradient(135deg, #333 0%, #333 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px;">
                <h2 style="margin: 0; font-size: 28px;">Shared Medical Records</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">These records have been shared with you for viewing</p>
            </div>
    `;
    
    prescriptions.forEach((presc, index) => {
        const prescData = presc.ocr_data;
        const uploadDate = new Date(presc.upload_date).toLocaleDateString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
        
        html += `
            <div class="disease-card" style="background: #ffffff; border: 2px solid #e0e0e0; border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                
                <!-- Header Section -->
                <div style="border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 20px;">
                    <h2 style="margin: 0 0 10px 0; color: #2c3e50; font-size: 24px;">
                        Prescription ${index + 1}
                    </h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">
                        ${prescData.patient_name ? `
                            <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;">
                                <span style="color: #666; font-size: 12px; display: block; margin-bottom: 5px;">PATIENT NAME</span>
                                <strong style="color: #2c3e50; font-size: 16px;">${prescData.patient_name}</strong>
                            </div>
                        ` : ''}
                        
                        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #28a745;">
                            <span style="color: #666; font-size: 12px; display: block; margin-bottom: 5px;">UPLOADED ON</span>
                            <strong style="color: #2c3e50; font-size: 16px;">${uploadDate}</strong>
                        </div>
                        
                        ${prescData.date ? `
                            <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #ffc107;">
                                <span style="color: #666; font-size: 12px; display: block; margin-bottom: 5px;">PRESCRIPTION DATE</span>
                                <strong style="color: #2c3e50; font-size: 16px;">${prescData.date}</strong>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Doctor & Hospital Info -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-bottom: 25px;">
                    ${prescData.doctor_name ? `
                        <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 15px; border-radius: 10px; border: 1px solid #333;">
                            <div style="color: #333; font-size: 14px; font-weight: 600; margin-bottom: 5px;"> DOCTOR</div>
                            <div style="color: #333; font-size: 18px; font-weight: bold;">Dr. ${prescData.doctor_name}</div>
                        </div>
                    ` : ''}
                    
                    ${prescData.hospital ? `
                        <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 15px; border-radius: 10px; border: 1px solid #333;">
                            <div style="color: #333; font-size: 14px; font-weight: 600; margin-bottom: 5px;"> HOSPITAL</div>
                            <div style="color: #2c3e50; font-size: 18px; font-weight: bold;">${prescData.hospital}</div>
                        </div>
                    ` : ''}
                </div>
                
                <!-- Medicines Section -->
                ${prescData.medicines && prescData.medicines.length > 0 ? `
                    <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #764ba220;">
                        <h3 style="margin: 0 0 20px 0; color: #333; font-size: 22px; display: flex; align-items: center; gap: 10px;">
                            Prescribed Medicines
                            <span style="background: #333; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px;">
                                ${prescData.medicines.length} items
                            </span>
                        </h3>
                        
                        <div style="display: grid; gap: 15px;">
                            ${prescData.medicines.map((med, idx) => `
                                <div style="background: white; padding: 18px; border-radius: 10px; border-left: 5px solid #333; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                                        <span style="background: #333; color: white; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px;">
                                            ${idx + 1}
                                        </span>
                                        <div style="flex: 1;">
                                            <h4 style="margin: 0; color: #333; font-size: 20px;">${med.name}</h4>
                                            <span style="background: #ffeef0; color: #333; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-block; margin-top: 5px;">
                                                ${med.dosage}
                                            </span>
                                        </div>
                                    </div>
                                    
                                    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                                        <div style="color: #666; font-size: 12px; margin-bottom: 5px; font-weight: 600;">INSTRUCTIONS</div>
                                        <div style="color: #2c3e50; font-size: 15px; line-height: 1.6;">${med.instructions}</div>
                                    </div>
                                    
                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                                        ${med.frequency ? `
                                            <div style="background: #e3f2fd; padding: 10px; border-radius: 6px;">
                                                <span style="color: #1976d2; font-size: 11px; font-weight: 600;">FREQUENCY</span>
                                                <div style="color: #1565c0; font-size: 14px; font-weight: 600; margin-top: 3px;">${med.frequency}</div>
                                            </div>
                                        ` : ''}
                                        
                                        ${med.duration ? `
                                            <div style="background: #fff3e0; padding: 10px; border-radius: 6px;">
                                                <span style="color: #f57c00; font-size: 11px; font-weight: 600;"> DURATION</span>
                                                <div style="color: #e65100; font-size: 14px; font-weight: 600; margin-top: 3px;">${med.duration}</div>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <div style="background: #fff3cd; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                        <strong style="color: #856404;">⚠️ No medicines detected in OCR</strong>
                        <p style="color: #856404; margin: 5px 0 0 0;">The prescription image may need manual review</p>
                    </div>
                `}
                
                <!-- Follow-up Section -->
                ${prescData.follow_up_date ? `
                    <div style="background: linear-gradient(135deg, #4facfe20 0%, #00f2fe20 100%); padding: 15px; border-radius: 10px; border: 2px solid #4facfe; margin-bottom: 20px;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="background: #4facfe; color: white; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                                📅
                            </div>
                            <div>
                                <div style="color: #0277bd; font-size: 13px; font-weight: 600;">FOLLOW-UP APPOINTMENT</div>
                                <div style="color: #01579b; font-size: 18px; font-weight: bold; margin-top: 3px;">${prescData.follow_up_date}</div>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Action Buttons -->
                <div style="display: flex; gap: 12px; margin-top: 25px; padding-top: 20px; border-top: 2px solid #e0e0e0; flex-wrap: wrap;">
                    <button onclick="downloadPrescriptionPDF('${presc._id}', '${presc.filename}')" 
                            style="flex: 1; min-width: 200px; background: linear-gradient(135deg, #333 0%, #333 100%); color: white; padding: 14px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: transform 0.2s;">
                        <span style="font-size: 20px;"></span>
                        Download Original File
                    </button>
                    
                    <button onclick="generatePrescriptionPDF(${JSON.stringify(prescData).replace(/"/g, '&quot;')})" 
                            style="flex: 1; min-width: 200px; background: linear-gradient(135deg, #333 0%, #333 100%); color: white; padding: 14px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: transform 0.2s;">
                        <span style="font-size: 20px;"></span>
                        Generate PDF Report
                    </button>
                </div>
                
                <!-- Raw OCR Text (Collapsible) -->
                <details style="margin-top: 20px; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">
                    <summary style="cursor: pointer; color: #667eea; font-weight: 600; font-size: 15px; padding: 5px;">
                        View Raw OCR Text
                    </summary>
                    <pre style="background: #ffffff; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 15px; font-size: 13px; line-height: 1.6; color: #2c3e50; border: 1px solid #e0e0e0;">${prescData.raw_text}</pre>
                </details>
            </div>
        `;
    });
    
    html += '</div>';
    document.getElementById('results').innerHTML = html;
}

// Download original prescription file
async function downloadPrescriptionPDF(prescriptionId, filename) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/download-prescription/${prescriptionId}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Show success message
        showNotification('Prescription downloaded successfully!', 'success');
    } catch (error) {
        console.error('Download error:', error);
        showNotification('Download failed', 'error');
    }
}

// Generate formatted PDF report from extracted data
function generatePrescriptionPDF(prescData) {
    // Create a printable HTML version
    const printWindow = window.open('', '_blank');
    
    const medicines = prescData.medicines || [];
    const medicinesHTML = medicines.map((med, idx) => `
        <tr style="border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 12px; font-weight: 600; color: #667eea;">${idx + 1}</td>
            <td style="padding: 12px; font-weight: 600; color: #2c3e50;">${med.name}</td>
            <td style="padding: 12px; color: #666;">${med.dosage}</td>
            <td style="padding: 12px; color: #666;">${med.frequency || '-'}</td>
            <td style="padding: 12px; color: #666;">${med.duration || '-'}</td>
            <td style="padding: 12px; color: #666; font-size: 13px;">${med.instructions}</td>
        </tr>
    `).join('');
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prescription - ${prescData.patient_name || 'Patient'}</title>
            <style>
                @media print {
                    body { margin: 0; }
                    .no-print { display: none; }
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 40px;
                    color: #2c3e50;
                    max-width: 1000px;
                    margin: 0 auto;
                }
                .header {
                    background: linear-gradient(135deg, #333 0%, #333 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }
                .header h1 { margin: 0 0 10px 0; }
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .info-box {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #333;
                }
                .info-box label {
                    color: #666;
                    font-size: 12px;
                    display: block;
                    margin-bottom: 5px;
                    font-weight: 600;
                }
                .info-box value {
                    color: #2c3e50;
                    font-size: 16px;
                    font-weight: 600;
                    display: block;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    background: white;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }
                th {
                    background: #333;
                    color: white;
                    padding: 15px 12px;
                    text-align: left;
                    font-weight: 600;
                }
                td {
                    padding: 12px;
                    border-bottom: 1px solid #e0e0e0;
                }
                .print-btn {
                    background: #28a745;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 20px;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e0e0e0;
                    color: #666;
                    font-size: 13px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Medical Prescription</h1>
                <p style="margin: 0; opacity: 0.9;">MediQuery - Smart Medical Consultation System</p>
            </div>
            
            <div class="info-grid">
                ${prescData.patient_name ? `
                    <div class="info-box">
                        <label>PATIENT NAME</label>
                        <value>${prescData.patient_name}</value>
                    </div>
                ` : ''}
                
                ${prescData.date ? `
                    <div class="info-box">
                        <label>PRESCRIPTION DATE</label>
                        <value>${prescData.date}</value>
                    </div>
                ` : ''}
                
                ${prescData.doctor_name ? `
                    <div class="info-box">
                        <label>DOCTOR</label>
                        <value>Dr. ${prescData.doctor_name}</value>
                    </div>
                ` : ''}
                
                ${prescData.hospital ? `
                    <div class="info-box">
                        <label>HOSPITAL/CLINIC</label>
                        <value>${prescData.hospital}</value>
                    </div>
                ` : ''}
            </div>
            
            <h2 style="color: #333; margin-top: 30px;">Prescribed Medicines</h2>
            <table>
                <thead>
                    <tr>
                        <th style="width: 40px;">#</th>
                        <th>Medicine Name</th>
                        <th>Dosage</th>
                        <th>Frequency</th>
                        <th>Duration</th>
                        <th>Instructions</th>
                    </tr>
                </thead>
                <tbody>
                    ${medicinesHTML || '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #999;">No medicines detected</td></tr>'}
                </tbody>
            </table>
            
            ${prescData.follow_up_date ? `
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin-top: 30px; border-left: 4px solid #333;">
                    <strong style="color: #333; font-size: 16px;">Follow-up Appointment: ${prescData.follow_up_date}</strong>
                </div>
            ` : ''}
            
            <div class="footer">
                <p><strong>Note:</strong> This is a computer-generated document from OCR-extracted prescription data. Please verify all details with the original prescription.</p>
                <p>Generated on: ${new Date().toLocaleString('en-IN')}</p>
            </div>
            
            <button class="print-btn no-print" onclick="window.print()"> Print / Save as PDF</button>
        </body>
        </html>
    `);
    
    printWindow.document.close();
}

// Notification helper
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-weight: 600;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
// Download prescription file
async function downloadPrescription(prescriptionId, filename) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/download-prescription/${prescriptionId}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert("❌ Download failed");
    }
}

// Close prescriptions modal
function closePrescriptions() {
    document.getElementById('prescriptionsModal').style.display = 'none';
}

// View Medical Timeline
async function viewMedicalTimeline() {
    const patientId = prompt("Enter your Patient ID:");
    
    if (!patientId) {
        alert("Patient ID is required");
        return;
    }
    
    document.getElementById('timelineModal').style.display = 'block';
    document.getElementById('timelineList').innerHTML = 
        '<div class="loading">Loading medical history...</div>';
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/medical-timeline/${patientId}`);
        const data = await response.json();
        
        if (data.timeline && data.timeline.length > 0) {
            let html = '<div style="position: relative;">';
            
            data.timeline.forEach((item, index) => {
                const iconMap = {
                    'prescription': '📄',
                    'appointment': '👨‍⚕️'
                };
                
                html += `
                    <div class="timeline-item" style="margin-bottom: 30px; padding-left: 40px; position: relative;">
                        <div style="position: absolute; left: 0; top: 0; font-size: 24px;">
                            ${iconMap[item.type]}
                        </div>
                        
                        <div class="appointment-card">
                            <h3>${item.title}</h3>
                            <div class="appointment-detail">
                                <span class="icon">📅</span>
                                <span>${new Date(item.date).toLocaleDateString()}</span>
                            </div>
                            
                            ${item.doctor ? `
                                <div class="appointment-detail">
                                    <span class="icon">👨‍⚕️</span>
                                    <span>Dr. ${item.doctor}</span>
                                </div>
                            ` : ''}
                            
                            ${item.hospital ? `
                                <div class="appointment-detail">
                                    <span class="icon">🏥</span>
                                    <span>${item.hospital}</span>
                                </div>
                            ` : ''}
                            
                            ${item.medicines_count ? `
                                <div class="appointment-detail">
                                    <span class="icon">💊</span>
                                    <span>${item.medicines_count} medicines</span>
                                </div>
                            ` : ''}
                            
                            ${item.status ? `
                                <span class="status-badge" style="background: ${item.status === 'confirmed' ? '#28a745' : '#dc3545'}">
                                    ${item.status.toUpperCase()}
                                </span>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            document.getElementById('timelineList').innerHTML = html;
        } else {
            document.getElementById('timelineList').innerHTML = `
                <div class="no-appointments">
                    <h3>📭 No Medical History</h3>
                    <p>Start by uploading prescriptions or booking appointments!</p>
                </div>
            `;
        }
        
    } catch (error) {
        document.getElementById('timelineList').innerHTML = 
            '<div class="error">❌ Failed to load timeline</div>';
    }
}

// Close timeline modal
function closeTimeline() {
    document.getElementById('timelineModal').style.display = 'none';
}

// Search Medicine in History
async function searchMedicineHistory() {
    const patientId = prompt("Enter your Patient ID:");
    if (!patientId) return;
    
    const medicineName = prompt("Enter medicine name to search:");
    if (!medicineName) return;
    
    document.getElementById('results').innerHTML = 
        '<div class="loading">🔍 Searching prescriptions...</div>';
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/search-medicine/${patientId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ medicine_name: medicineName })
        });
        
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            let html = `
                <div class="results">
                    <div class="disease-card">
                        <h2>Found ${data.count} prescriptions with "${medicineName}"</h2>
                        <div class="doctor-list">
            `;
            
            data.results.forEach(result => {
                html += `
                    <div class="doctor-card">
                        <div class="doctor-name">${result.medicine.name} - ${result.medicine.dosage}</div>
                        <p><strong>Date:</strong> ${result.date}</p>
                        <p><strong>Doctor:</strong> ${result.doctor}</p>
                        <p>${result.medicine.instructions}</p>
                    </div>
                `;
            });
            
            html += '</div></div></div>';
            document.getElementById('results').innerHTML = html;
        } else {
            document.getElementById('results').innerHTML = 
                '<div class="error">No prescriptions found with this medicine</div>';
        }
        
    } catch (error) {
        alert("❌ Search failed");
    }
}
