document.addEventListener("DOMContentLoaded", function() {
  const tabs = document.querySelectorAll('.tab-btn');
  const categoryInput = document.getElementById('selectedCategory');
  const form = document.getElementById('smsForm');
  const messageInput = document.getElementById('message');
  const sendBtn = document.getElementById('sendSmsBtn');
  const recipientsContainer = document.getElementById('recipientsContainer'); // div to show checkboxes

  // Fetch pastors dynamically via AJAX
  function fetchPastors(category) {
    fetch(`/get_pastors/?category=${category}`)
      .then(response => response.json())
      .then(data => renderPastorsCheckboxes(data.pastors))
      .catch(err => console.error("Error fetching pastors:", err));
  }

  // Tab click handling
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const category = tab.dataset.category;
      categoryInput.value = category;

      // Remove 'selected' from all tabs
      tabs.forEach(t => t.classList.remove('selected'));
      tab.classList.add('selected');

      // Fetch pastors for this category
      fetchPastors(category);
    });
  });

  // Function to render pastors checkboxes
  function renderPastorsCheckboxes(pastors) {
    recipientsContainer.innerHTML = ""; // clear previous
    pastors.forEach(pastor => {
      const label = document.createElement('label');
      label.style.display = "block";
      label.style.margin = "5px 0";

      const checkbox = document.createElement('input');
      checkbox.type = "checkbox";
      checkbox.name = "recipients";
      checkbox.value = pastor.phone;

      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(` ${pastor.name} (${pastor.phone})`));

      recipientsContainer.appendChild(label);
    });
  }

  // Form submit validation
  form.addEventListener('submit', function(e) {
    const checkedBoxes = form.querySelectorAll('input[name="recipients"]:checked');

    if (!categoryInput.value) {
      e.preventDefault();
      alert("Please select a category before sending the message.");
      return;
    }
    if (!checkedBoxes.length) {
      e.preventDefault();
      alert("Please select at least one recipient.");
      return;
    }
    if (!messageInput.value.trim()) {
      e.preventDefault();
      alert("Please type a message before sending.");
      messageInput.focus();
      return;
    }

    // Change button to 'sent' state
    sendBtn.classList.add('sent');
    sendBtn.textContent = 'Sent';
    sendBtn.disabled = true;

    // Reset button after 3 seconds
    setTimeout(() => {
      sendBtn.classList.remove('sent');
      sendBtn.textContent = 'Send SMS';
      sendBtn.disabled = false;
    }, 3000);
  });
});
