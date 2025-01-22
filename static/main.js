console.log("WELCOME TO MLTI")

chatSend = document.getElementById('chat-send');
chatBox = document.getElementById('message-input');
chatMessages = document.getElementById('chat-messages');

chatSend.addEventListener('click', function() {
    const message = chatBox.value;

    if (message.trim() !== '') {
        const newMessage = document.createElement('div');
        newMessage.className = 'chat-message chat-to';
        newMessage.textContent = message;

        chatMessages.appendChild(newMessage);

        // get llm response and create text box

        document.getElementById('message-input').value = '';
    }
});

chatBox.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatSend.click();
    }
});

// Modal elements
const uploadDealBtn = document.getElementById('upload-deal-btn');
const modal = document.getElementById('upload-modal');
const closeModalBtn = document.querySelector('.close-modal');
const fileUploadBtn = document.querySelector('.file-upload-btn');
const fileInput = document.getElementById('deal-file-input');
const fileNameDisplay = document.querySelector('.file-name');
const dealNameInput = document.getElementById('deal-name-input');
const submitDealBtn = document.getElementById('submit-deal');

// Modal open/close
uploadDealBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
});

closeModalBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    // Reset form
    dealNameInput.value = '';
    fileInput.value = '';
    fileNameDisplay.textContent = 'No file chosen';
});

// Close modal if clicking outside
modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.add('hidden');
    }
});

// File selection handling
fileUploadBtn.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileNameDisplay.textContent = e.target.files[0].name;
    } else {
        fileNameDisplay.textContent = 'No file chosen';
    }
});

// Form submission
submitDealBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    const dealName = dealNameInput.value.trim();

    if (!file || !dealName) {
        alert('Please provide both a deal name and a file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('deal_name', dealName);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Update deal dropdown
            const dealSelect = document.getElementById('deal');
            const newOption = document.createElement('option');
            newOption.value = dealName;
            newOption.textContent = dealName;
            dealSelect.appendChild(newOption);

            // Close modal and reset form
            modal.classList.add('hidden');
            dealNameInput.value = '';
            fileInput.value = '';
            fileNameDisplay.textContent = 'No file chosen';

            // Show success message in chat area
            const successMessage = document.createElement('div');
            successMessage.className = 'chat-message chat-from';
            successMessage.textContent = `Deal "${dealName}" uploaded successfully`;
            chatMessages.appendChild(successMessage);
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Error:', error);
        const errorMessage = document.createElement('div');
        errorMessage.className = 'chat-message chat-from';
        errorMessage.textContent = `Error: ${error.message}`;
        chatMessages.appendChild(errorMessage);
    }
});

// Load deals into dropdown when page loads
async function loadDeals() {
    try {
        const response = await fetch('/api/deals');
        const deals = await response.json();

        const dealSelect = document.getElementById('deal');
        // Clear existing options except the first disabled one
        dealSelect.innerHTML = '<option value="" disabled selected>Select a Deal to Analyze</option>';

        deals.forEach(deal => {
            const option = document.createElement('option');
            option.value = deal;
            option.textContent = deal;
            dealSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading deals:', error);
    }
}

// Call this when page loads
document.addEventListener('DOMContentLoaded', loadDeals);

// Go button handler
// Go button handler
const goButton = document.getElementById('deal-submit');

goButton.addEventListener('click', async () => {
    const selectedDeal = document.getElementById('deal').value;
    console.log('Go button clicked for deal:', selectedDeal);
    
    if (!selectedDeal) {
        console.log('No deal selected');
        return;
    }

    try {
        // First run the populator
        const populatorResponse = await fetch('/api/populator', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deal_name: selectedDeal
            })
        });

        if (!populatorResponse.ok) {
            throw new Error('Populator failed');
        }

        // Then get the CSV data
        const csvResponse = await fetch(`/api/get-csv/${selectedDeal}`);
        const csvData = await csvResponse.json();

        // Display in spreadsheet
        const container = document.getElementById('spreadsheet-container');
        
        let tableHTML = '<table id="spreadsheet-table"><thead><tr>';
        const headers = Object.keys(csvData[0]);
        
        headers.forEach(header => {
            tableHTML += `<th>${header}</th>`;
        });
        
        tableHTML += '</tr></thead><tbody>';
        
        csvData.forEach(row => {
            tableHTML += '<tr>';
            headers.forEach(header => {
                tableHTML += `<td>${row[header] || ''}</td>`;
            });
            tableHTML += '</tr>';
        });
        
        tableHTML += '</tbody></table>';
        container.innerHTML = tableHTML;

    } catch (error) {
        console.log('Error:', error);
    }
});
