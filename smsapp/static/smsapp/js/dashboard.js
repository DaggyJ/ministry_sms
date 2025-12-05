document.addEventListener("DOMContentLoaded", function() {

  const tabs = document.querySelectorAll('.tab-btn');
  const categoryInput = document.getElementById('selectedCategory');
  const form = document.getElementById('smsForm');
  const messageInput = document.getElementById('message');
  const sendBtn = document.getElementById('sendSmsBtn');
  const recipientsContainer = document.getElementById('dynamicRecipients'); // Updated div

  const categoryMap = {
    'Regional': 'Regional Overseer',
    'Subregional': 'Subregional Pastor',
    'Pastor': 'Pastor'
  };

  // Fetch contacts based on tab/category
  function fetchContacts(tabCategory) {
    const categoryName = categoryMap[tabCategory] || '';
    fetch(`/get_pastors/?category=${encodeURIComponent(categoryName)}`)
      .then(res => res.json())
      .then(data => renderContacts(data.pastors || []))
      .catch(err => console.error("Error fetching contacts:", err));
  }

  // Render contacts in dynamicRecipients div
  function renderContacts(contacts) {
    recipientsContainer.innerHTML = "";

    if (!contacts.length) {
      recipientsContainer.textContent = "No contacts found for this category.";
      return;
    }

    // Group contacts by region and subregion
    const grouped = {};
    contacts.forEach(c => {
      const region = c.region || "No Region";
      const subregion = c.subregion || "No Subregion";
      if (!grouped[region]) grouped[region] = {};
      if (!grouped[region][subregion]) grouped[region][subregion] = [];
      grouped[region][subregion].push(c);
    });

    // Top-level select all
    const selectAllDiv = document.createElement('div');
    const topCheckbox = document.createElement('input');
    topCheckbox.type = 'checkbox';
    topCheckbox.style.marginRight = '5px';
    topCheckbox.addEventListener('change', function() {
      recipientsContainer.querySelectorAll('input.contact-checkbox').forEach(cb => cb.checked = this.checked);
      updateSendButton();
    });
    selectAllDiv.appendChild(topCheckbox);
    selectAllDiv.appendChild(document.createTextNode('Select All Contacts'));
    selectAllDiv.style.marginBottom = '10px';
    recipientsContainer.appendChild(selectAllDiv);

    // Render grouped contacts
    for (const region in grouped) {
      const regionDiv = document.createElement('div');
      const regionHeader = document.createElement('strong');
      regionHeader.textContent = region;
      regionDiv.appendChild(regionHeader);
      regionDiv.style.marginBottom = '10px';

      for (const subregion in grouped[region]) {
        const subDiv = document.createElement('div');
        const subHeader = document.createElement('em');
        subHeader.textContent = subregion;
        subDiv.appendChild(subHeader);
        subDiv.style.marginLeft = '20px';
        subDiv.style.marginBottom = '5px';

        // Subregion select all
        const subSelectDiv = document.createElement('div');
        const subCheckbox = document.createElement('input');
        subCheckbox.type = 'checkbox';
        subCheckbox.style.marginRight = '5px';
        subCheckbox.addEventListener('change', function() {
          subDiv.querySelectorAll('input.contact-checkbox').forEach(cb => cb.checked = this.checked);
          updateSendButton();
        });
        subSelectDiv.appendChild(subCheckbox);
        subSelectDiv.appendChild(document.createTextNode('Select All in this Subregion'));
        subSelectDiv.style.marginBottom = '5px';
        subDiv.appendChild(subSelectDiv);

        // Individual contacts
        grouped[region][subregion].forEach(c => {
          const label = document.createElement('label');
          label.style.display = 'block';
          label.style.margin = '2px 0';

          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.classList.add('contact-checkbox');
          checkbox.name = 'recipients';
          checkbox.value = c.phone;
          checkbox.addEventListener('change', updateSendButton);

          label.appendChild(checkbox);
          label.appendChild(document.createTextNode(` ${c.name} (${c.phone})`));
          subDiv.appendChild(label);
        });

        regionDiv.appendChild(subDiv);
      }

      recipientsContainer.appendChild(regionDiv);
    }

    // Update send button initially
    updateSendButton();
  }

  // Enable/disable send button dynamically
  function updateSendButton() {
    const anyChecked = recipientsContainer.querySelectorAll('input.contact-checkbox:checked').length > 0;
    sendBtn.disabled = !anyChecked;
  }

  // Tab click event
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      categoryInput.value = tab.dataset.category;
      tabs.forEach(t => t.classList.remove('selected'));
      tab.classList.add('selected');
      fetchContacts(tab.dataset.category);
    });
  });

  // Auto-select first tab
  if (tabs.length > 0) tabs[0].click();

  // Form submit validation
  form.addEventListener('submit', function(e) {
    const checkedBoxes = recipientsContainer.querySelectorAll('input.contact-checkbox:checked');
    if (!categoryInput.value) {
      e.preventDefault();
      alert("Please select a category before sending the message.");
      return;
    }
    if (checkedBoxes.length === 0) {
      e.preventDefault();
      alert("Please select at least one recipient before sending.");
      return;
    }
    if (!messageInput.value.trim()) {
      e.preventDefault();
      alert("Please type a message before sending.");
      messageInput.focus();
      return;
    }

    // Optional: show "Sent" state
    sendBtn.classList.add('sent');
    sendBtn.textContent = 'Sent';
    sendBtn.disabled = true;
    setTimeout(() => {
      sendBtn.classList.remove('sent');
      sendBtn.textContent = 'Send SMS';
      sendBtn.disabled = false;
    }, 3000);
  });

});