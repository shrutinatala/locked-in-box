const tablesContainer = document.getElementById("tables-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");

const TOTAL_TABLES = 10;
const MAX_OCCUPANCY = 4;
const MAX_CAPACITY = TOTAL_TABLES * MAX_OCCUPANCY;

// State: track occupancy locally
let tableData = {};
for (let i = 1; i <= TOTAL_TABLES; i++) {
  tableData[i] = 0; // start with 0 occupants
  const div = document.createElement("div");
  div.classList.add("table-box");
  div.id = `table-${i}`;
  div.innerHTML = `Table ${i}<br>Occupancy: 0/${MAX_OCCUPANCY}`;
  updateTableColor(div, 0); // initialize green
  tablesContainer.appendChild(div);
}

// Function: set background color based on occupancy
function updateTableColor(div, occupancy) {
  let color = "lightgreen"; // default
  if (occupancy === 0) {
    color = "lightgreen";
  } else if (occupancy === 1) {
    color = "#d9f542"; // yellow-green
  } else if (occupancy === 2) {
    color = "#f5d742"; // yellow
  } else if (occupancy === 3) {
    color = "#f59e42"; // orange
  } else if (occupancy === 4) {
    color = "#f54242"; // red
  }

  div.style.transition = "background-color 0.5s ease"; // smooth fade
  div.style.backgroundColor = color;
}

// Function: update progress bar
function updateProgressBar() {
  const totalOccupancy = Object.values(tableData).reduce((a, b) => a + b, 0);
  const percentage = Math.round((totalOccupancy / MAX_CAPACITY) * 100);

  progressBar.style.width = `${percentage}%`;
  progressText.textContent = `${percentage}% Occupancy`;

  // Change bar color gradually (green → yellow → red)
  if (percentage < 50) {
    progressBar.style.backgroundColor = "#4caf50"; // green
  } else if (percentage < 80) {
    progressBar.style.backgroundColor = "#f5d742"; // yellow
  } else {
    progressBar.style.backgroundColor = "#f54242"; // red
  }
}

// Click handler
tablesContainer.addEventListener("click", (e) => {
  const div = e.target.closest(".table-box");
  if (!div) return;

  const tableId = div.id.split("-")[1];
  let occupancy = tableData[tableId];

  // Increment occupancy, wrap back to 0
  occupancy = (occupancy + 1) % (MAX_OCCUPANCY + 1);
  tableData[tableId] = occupancy;

  // Update UI
  div.innerHTML = `Table ${tableId}<br>Occupancy: ${occupancy}/${MAX_OCCUPANCY}`;
  updateTableColor(div, occupancy);
  updateProgressBar();
});
