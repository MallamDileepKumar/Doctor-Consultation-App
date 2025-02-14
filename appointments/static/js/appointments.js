function updateAppointmentStatus(appointmentId) {
    let newStatus = document.getElementById(`status-select-${appointmentId}`).value;

    fetch(`/update-appointment-status/${appointmentId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: `status=${newStatus}`
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById(`status-${appointmentId}`).innerText = newStatus;
        if (data.meeting_link) {
            document.getElementById(`meeting-link-${appointmentId}`).innerHTML = `<a href="${data.meeting_link}" target="_blank">Join Meeting</a>`;
        }
    })
    .catch(error => console.error("Error:", error));
}