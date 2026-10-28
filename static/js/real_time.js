/**
 * MedCare Hospital Management System - Real-Time Engine
 * Controls dynamic AJAX counters, doctor availability polling, and live status updates.
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log("MedCare Real-Time Module Initialized.");

    // Auto-dismiss Django message alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000);
    });

    // Initialize Dashboard Live Stats Polling if stats elements exist
    const statsContainer = document.getElementById('live-stats-container');
    if (statsContainer) {
        pollDashboardStats();
        setInterval(pollDashboardStats, 15000); // Poll every 15 seconds
    }

    // Appointment Doctor Availability Real-time check
    const doctorSelect = document.getElementById('id_doctor');
    const dateInput = document.getElementById('id_appointment_date');
    const timeSelect = document.getElementById('id_appointment_time');

    if (doctorSelect && dateInput && timeSelect) {
        function checkSlotAvailability() {
            const doctorId = doctorSelect.value;
            const selectedDate = dateInput.value;

            if (!doctorId || !selectedDate) return;

            fetch(`/appointments/api/availability/?doctor_id=${doctorId}&date=${selectedDate}`)
                .then(response => response.json())
                .then(data => {
                    const bookedSlots = data.booked_slots || [];
                    const options = timeSelect.options;

                    for (let i = 0; i < options.length; i++) {
                        const optionValue = options[i].value;
                        if (bookedSlots.includes(optionValue)) {
                            options[i].disabled = true;
                            options[i].text = options[i].text.replace(' (Booked)', '') + ' (Booked)';
                            options[i].style.color = '#ef4444';
                        } else {
                            options[i].disabled = false;
                            options[i].text = options[i].text.replace(' (Booked)', '');
                            options[i].style.color = '';
                        }
                    }
                })
                .catch(err => console.error("Error checking availability:", err));
        }

        doctorSelect.addEventListener('change', checkSlotAvailability);
        dateInput.addEventListener('change', checkSlotAvailability);
    }
});

/**
 * Poll live dashboard statistical counters via JSON API
 */
function pollDashboardStats() {
    fetch('/api/dashboard-stats/')
        .then(response => {
            if (!response.ok) throw new Error("Stats API failed");
            return response.json();
        })
        .then(data => {
            updateCounter('count-total-patients', data.total_patients);
            updateCounter('count-total-doctors', data.total_doctors);
            updateCounter('count-total-departments', data.total_departments);
            updateCounter('count-total-appointments', data.total_appointments);
            updateCounter('count-pending-appointments', data.pending_appointments);
            updateCounter('count-completed-appointments', data.completed_appointments);
            updateCounter('count-cancelled-appointments', data.cancelled_appointments);
            updateCounter('count-confirmed-appointments', data.confirmed_appointments);

            const lastUpdatedElem = document.getElementById('stats-last-updated');
            if (lastUpdatedElem) {
                lastUpdatedElem.innerText = `Live synced at ${data.timestamp}`;
            }
        })
        .catch(err => console.log("Stats poll suppressed:", err));
}

/**
 * Smooth Counter Animation Helper
 */
function updateCounter(elementId, newValue) {
    const elem = document.getElementById(elementId);
    if (!elem) return;

    const currentValue = parseInt(elem.innerText.replace(/,/g, '')) || 0;
    if (currentValue !== newValue) {
        elem.classList.add('text-primary');
        elem.innerText = newValue.toLocaleString();
        setTimeout(() => elem.classList.remove('text-primary'), 1000);
    }
}
