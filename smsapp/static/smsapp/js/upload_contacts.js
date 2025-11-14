document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("uploadForm");
  const fileInput = form.querySelector('input[type="file"]');
  const uploadBtn = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", function(e) {
    if (!fileInput.value) {
      e.preventDefault();
      alert("Please select an Excel file before uploading.");
      fileInput.focus();
      return;
    }

    // Change button to 'sent' state
    uploadBtn.classList.add('sent');
    uploadBtn.textContent = 'Uploaded';
    uploadBtn.disabled = true;

    // Reset button after 3 seconds
    setTimeout(() => {
      uploadBtn.classList.remove('sent');
      uploadBtn.textContent = 'Upload';
      uploadBtn.disabled = false;
    }, 3000);
  });
});
