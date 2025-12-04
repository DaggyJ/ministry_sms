document.addEventListener("DOMContentLoaded", () => {

  // Generic function to handle any AJAX form
  const handleForm = (formId, submitUrl, onSuccess, onError) => {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(form);

      try {
        const response = await fetch(submitUrl, {
          method: "POST",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": form.querySelector('input[name="csrfmiddlewaretoken"]').value
          },
          body: formData
        });

        const data = await response.json();

        if (data.success) {
          if (onSuccess) onSuccess(data);
        } else {
          if (onError) onError(data);
        }

      } catch (err) {
        console.error("AJAX error:", err);
        if (onError) onError({ error: "Network error" });
      }
    });
  };

  // Login form
  handleForm("loginForm", "/accounts/login/",
    (data) => {
      alert(data.message || "Logged in successfully!");
      if (data.redirect_url) window.location.href = data.redirect_url;
    },
    (data) => alert(data.error || "Login failed")
  );

  // Signup form
  handleForm("signupForm", "/accounts/signup/",
    (data) => {
      alert(data.message || "Account created successfully!");
      if (data.redirect_url) window.location.href = data.redirect_url;
    },
    (data) => alert(data.error || "Signup failed")
  );

  // Reset PIN form
  handleForm("resetPinForm", "/accounts/reset-pin/",
    (data) => {
      alert(data.message || "6-digit code sent!");
      if (data.redirect_url) window.location.href = data.redirect_url;
    },
    (data) => alert(data.error || "Failed to send code")
  );

  // Verify PIN form
  handleForm("verifyPinForm", "/accounts/verify-pin/",
    (data) => {
      alert(data.message || "Code verified!");
      if (data.redirect_url) window.location.href = data.redirect_url;
    },
    (data) => alert(data.error || "Invalid code")
  );

  // Set new password form
  handleForm("setNewPasswordForm", "/accounts/set-new-password/",
    (data) => {
      alert(data.message || "Password reset successfully!");
      if (data.redirect_url) window.location.href = data.redirect_url;
    },
    (data) => alert(data.error || "Failed to reset password")
  );

});


document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("setNewPasswordForm");
  const errorDiv = document.getElementById("passwordError");

  form.addEventListener("submit", function(e) {
    e.preventDefault();
    errorDiv.textContent = "";

    const formData = new FormData(form);

    fetch("{% url 'accounts:set_new_password' %}", {
      method: "POST",
      headers: {"X-Requested-With": "XMLHttpRequest"},
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert(data.message);
        window.location.href = data.redirect_url;
      } else {
        if (data.errors) {
          errorDiv.innerHTML = Object.values(data.errors).map(arr => arr.join('<br>')).join('<br>');
        } else {
          errorDiv.textContent = data.error || "Validation failed";
        }
      }
    })
    .catch(err => {
      console.error(err);
      errorDiv.textContent = "An unexpected error occurred.";
    });
  });
});
