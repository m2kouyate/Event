document.addEventListener("DOMContentLoaded", function() {

    function updateEventList() {
        fetch('/api/events/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showMessageModal(data.error);
                    return;
                }

                const eventsList = document.querySelector('#event-list-ul');
                if (!eventsList) return;

                eventsList.innerHTML = '';

                data.result.forEach(event => {
                    const listItem = document.createElement('li');
                    listItem.className = 'event-list-item';
                    listItem.setAttribute('data-event-id', event.id);

                    const link = document.createElement('a');
                    link.href = `/events/${event.id}/`;
                    link.textContent = event.title;

                    listItem.appendChild(link);
                    eventsList.appendChild(listItem);
                });
            });
    }

    setInterval(updateEventList, 30000);

    function updateEventParticipants() {
        const eventIdElement = document.querySelector('.event-detail');
        if (!eventIdElement) return;

        const eventId = eventIdElement.getAttribute('data-event-id');
        fetch(`/api/events/${eventId}/`)
            .then(response => response.json())
            .then(data => {
                const participantsList = document.querySelector('.event-detail ul');
                if (!participantsList) return;

                participantsList.innerHTML = '';

                data.participants.forEach(participant => {
                    const listItem = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = `/users/profile/${participant.id}/`;
                    link.textContent = `${participant.first_name} ${participant.last_name} (${participant.username})`;

                    listItem.appendChild(link);
                    participantsList.appendChild(listItem);
                });
            });
    }

    setInterval(updateEventParticipants, 30000);

    // Функция для отображения сообщений в модальном окне
    function showMessageModal(message) {
        const modalBody = document.querySelector('#errorMessageModal .modal-body p');
        if (modalBody) {
            modalBody.textContent = message;
            // Используя jQuery, показываем модальное окно
            $('#errorMessageModal').modal('show');
        }
    }

    const errorElement = document.querySelector('#errorMessageModal .modal-body p');
    if (errorElement) {
        const errorMessage = errorElement.textContent.trim();
        if (errorMessage) {
            showMessageModal(errorMessage);
        }
    }
});
