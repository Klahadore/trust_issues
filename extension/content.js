// Check if a popup already exists
if(!document.getElementById("extension-popup-modal")) {
  // Create a container for the popup
  const modal = document.createElement("div");
  modal.id = "extension-popup-modal";
  modal.style.position = "fixed";
  modal.style.top = "5%";
  modal.style.left = "5%";
  modal.style.width = "90%";
  modal.style.height = "90%";
  modal.style.background = "rgba(255, 248, 220, 0.95)";
  modal.style.borderRadius = "20px";
  modal.style.boxShadow = "0px 4px 10px rgba(0, 0, 0, 0.25)";
  modal.style.zIndex = "10000";
  modal.style.display = "flex";
  modal.style.flexDirection = "column";
  modal.style.justifyContent = "center";
  modal.style.alignItems = "center";
  modal.style.padding = "20px";
  modal.style.boxSizing = "border-box";

  // Add content to the popup
  modal.innerHTML = `
    <h2 style="font-size: 2rem; margin-bottom: 20px; color: #000;">TRUST ISSUES</h2>
    <button id="close-modal" style="
      padding: 15px 30px;
      background: #a9741e;
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 1.2rem;
      cursor: pointer;
      transition: background-color 0.3s ease;
    ">Close</button>
  `;

  // Append the modal to the document body
  document.body.appendChild(modal);

  // Close the modal when the button is clicked
  document.getElementById("close-modal").addEventListener("click", () => {
    modal.remove();
  });
} else {
  console.log("Popup already exists!");
}
