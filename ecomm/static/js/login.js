const togglePasswordVisibility = (inputId, iconClass) => {
  const passwordInput = document.getElementById(inputId);
  const icon = document.getElementById(iconClass);

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  } else {
    passwordInput.type = "password";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  }
}