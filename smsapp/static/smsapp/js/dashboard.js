document.addEventListener("DOMContentLoaded", function() {
  const tabs = document.querySelectorAll('.tab-btn');
  const categoryInput = document.getElementById('selectedCategory');
  const form = document.getElementById('smsForm');
  const messageInput = document.getElementById('message');
  const sendBtn = document.getElementById('sendSmsBtn');
  const recipientsContainer = document.getElementById('recipientsContainer');

  const categoryMap = {
    'Regional': 'Regional Overseer',
    'Subregional': 'Subregional Pastor',
    'Pastor': 'Pastor'
  };

  function fetchContacts(tabCategory) {
    const categoryName = categoryMap[tabCategory] || '';
    fetch(`/get_pastors/?category=${encodeURIComponent(categoryName)}`)
      .then(response => response.json())
      .then(data => renderContacts(tabCategory, data.pastors))
      .catch(err => console.error("Error fetching contacts:", err));
  }

  function renderContacts(tabCategory, contacts) {
    recipientsContainer.innerHTML = "";

    // Filter contacts per tab
    contacts = contacts.filter(c => {
      if (tabCategory === 'Regional') return c.region && !c.subregion;
      if (tabCategory === 'Subregional') return c.subregion;
      return !c.region && !c.subregion;
    });

    if (!contacts.length) {
      const msg = document.createElement('p');
      msg.textContent = "No contacts found for this category.";
      recipientsContainer.appendChild(msg);
      return;
    }

    // Sort contacts by region → subregion → name
    contacts.sort((a, b) => {
      if ((a.region || '') !== (b.region || '')) return (a.region || '').localeCompare(b.region || '');
      if ((a.subregion || '') !== (b.subregion || '')) return (a.subregion || '').localeCompare(b.subregion || '');
      return a.name.localeCompare(b.name);
    });

    // Group contacts
    const grouped = {};
    contacts.forEach(c => {
      const region = c.region || 'No Region';
      const subregion = c.subregion || 'No Subregion';
      if (!grouped[region]) grouped[region] = {};
      if (!grouped[region][subregion]) grouped[region][subregion] = [];
      grouped[region][subregion].push(c);
    });

    // Top-level Select All
    const selectAllTop = document.createElement('div');
    selectAllTop.style.marginBottom = '10px';
    const topCheckbox = document.createElement('input');
    topCheckbox.type = 'checkbox';
    topCheckbox.style.marginRight = '5px';
    topCheckbox.addEventListener('change', function() {
      recipientsContainer.querySelectorAll('input.contact-checkbox').forEach(cb => cb.checked = this.checked);
      updateSendButton();
    });
    selectAllTop.appendChild(topCheckbox);
    selectAllTop.appendChild(document.createTextNode('Select All Contacts in this Tab'));
    recipientsContainer.appendChild(selectAllTop);

    // Render grouped contacts
    for (const region in grouped) {
      const regionDiv = document.createElement('div');
      regionDiv.style.marginBottom = '10px';
      const regionHeader = document.createElement('strong');
      regionHeader.textContent = region;
      regionDiv.appendChild(regionHeader);

      for (const subregion in grouped[region]) {
        const subDiv = document.createElement('div');
        subDiv.style.marginLeft = '20px';
        subDiv.style.marginBottom = '5px';
        const subHeader = document.createElement('em');
        subHeader.textContent = subregion;
        subDiv.appendChild(subHeader);

        // Subregion Select All
        const subSelectDiv = document.createElement('div');
        subSelectDiv.style.marginBottom = '5px';
        const subCheckbox = document.createElement('input');
        subCheckbox.type = 'checkbox';
        subCheckbox.style.marginRight = '5px';
        subCheckbox.addEventListener('change', function() {
          subDiv.querySelectorAll('input.contact-checkbox').forEach(cb => cb.checked = this.checked);
          updateSendButton();
        });
        subSelectDiv.appendChild(subCheckbox);
        subSelectDiv.appendChild(document.createTextNode('Select All in this Subregion'));
        subDiv.appendChild(subSelectDiv);

        // Add individual contacts
        grouped[region][subregion].forEach(c => {
          const label = document.createElement('label');
          label.style.display = 'block';
          label.style.margin = '2px 0';

          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.classList.add('contact-checkbox');
          checkbox.name = 'recipients';
          checkbox.value = c.phone || ""; // fallback if phone is missing

  // Optional: attach event to update send button
          checkbox.addEventListener('change', updateSendButton);

          label.appendChild(checkbox);
          label.appendChild(document.createTextNode(` ${c.name} (${c.phone})`));
          subDiv.appendChild(label);
        });


        regionDiv.appendChild(subDiv);
      }

      recipientsContainer.appendChild(regionDiv);
    }
  }

  // Update send button state dynamically
  function updateSendButton() {
  const anyChecked = recipientsContainer.querySelectorAll('input.contact-checkbox:checked').length > 0;
  sendBtn.disabled = !anyChecked;
}
    
  // Tab click event
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabCategory = tab.dataset.category;
      categoryInput.value = tabCategory;
      tabs.forEach(t => t.classList.remove('selected'));
      tab.classList.add('selected');
      fetchContacts(tabCategory);
    });
  });

  // Auto-select first tab on page load
  if (tabs.length > 0) tabs[0].click();

  // Form submit validation
  form.addEventListener('submit', function(e) {
    const checkedBoxes = recipientsContainer.querySelectorAll('input.contact-checkbox:checked[value]');

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

    // Mark as sent
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
