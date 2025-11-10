const canvas = document.getElementById("pendulum-canvas");
const ctx = canvas.getContext("2d");
let trailEnabled = true;
let zoom = 1;
let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let lastX, lastY;
function applyTransform() {
  ctx.setTransform(zoom, 0, 0, zoom, offsetX, offsetY);
}
// wheel scrolling
canvas.addEventListener("wheel", (e) => {
  e.preventDefault();
  const direction = e.deltaY < 0 ? 1 : -1;
  const scale = 1.1;
  const mouseX = e.offsetX;
  const mouseY = e.offsetY;
  const newZoom = direction > 0 ? zoom * scale : zoom / scale;
  const clamped = Math.min(Math.max(newZoom, 0.5), 5);
  const factor = clamped / zoom;
  offsetX = mouseX - factor * (mouseX - offsetX);
  offsetY = mouseY - factor * (mouseY - offsetY);
  zoom = clamped;
});

// pinch zoom on mobiles
let lastDist = 0;
canvas.addEventListener("touchmove", (e) => {
  if (e.touches.length == 2) {
    e.preventDefault();
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    const dist = Math.hypot(dx, dy);
    if (!lastDist) lastDist = dist;
    const scale = dist / lastDist;
    zoom = Math.min(Math.max(zoom * scale, 0.5), 5);
    lastDist = dist;
  }
});
canvas.addEventListener("touchend", () => (lastDist = 0));
canvas.addEventListener("dblclick", () => {
  zoom = 1;
  offsetX = 0;
  offsetY = 0;
});
// plane
function drawCartesianPlane() {
  const gridSize = 20;
  const gridColor = "#ccc";
  ctx.beginPath();
  ctx.strokeStyle = gridColor;
  ctx.lineWidth = 1;
  for (let x = 0; x <= canvas.width; x += gridSize) {
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
  }
  for (let y = 0; y <= canvas.height; y += gridSize) {
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
  }
  ctx.stroke();
}
const ORIGIN_X = canvas.width / 2;
const ORIGIN_Y = canvas.height / 2;
window.addEventListener("resize", () => {
  ORIGIN_X = canvas.width / 2;
  ORIGIN_Y = canvas.height / 2;
});
function drawPendulum(coords) {
  ctx.save();
  applyTransform();
  ctx.clearRect(
    -offsetX / zoom,
    -offsetY / zoom,
    canvas.width / zoom,
    canvas.height / zoom,
  );
  drawCartesianPlane();

  // pivot thingy
  ctx.beginPath();
  ctx.arc(ORIGIN_X, ORIGIN_Y, 4, 0, Math.PI * 2);
  ctx.fillStyle = "#444";
  ctx.fill();

  // arms
  ctx.beginPath();
  ctx.moveTo(ORIGIN_X, ORIGIN_Y);
  ctx.lineTo(coords[0].x, coords[0].y);
  ctx.lineTo(coords[1].x, coords[1].y);
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 1.5 / zoom;
  ctx.stroke();

  for (let i = 0; i < coords.length; i++) {
    ctx.beginPath();
    ctx.arc(
      coords[i].x,
      coords[i].y,
      i === 0 ? coords[2].m1 : coords[2].m2,
      0,
      2 * Math.PI,
    );
    ctx.fillStyle = i === 0 ? "#1976d2" : "#ef6c00";
    ctx.fill();
    ctx.strokeStyle = "#222";
    ctx.stroke();
  }
  ctx.restore();
}
let latestCoords = null;
const trail1 = [];
const trail2 = [];
const MAX_TRAIL = 300;
async function pollCoords() {
  try {
    const response = await fetch("/coords", { cache: "no-store" });
    if (response.ok) {
      latestCoords = await response.json();
    }
  } catch (e) {}
}
function animate() {
  if (latestCoords) {
    updateAccelerationData(latestCoords);
    updateAngularVelocityData(latestCoords);
    if (trailEnabled) {
      trail1.push({ x: latestCoords[0].x, y: latestCoords[0].y });
      trail2.push({ x: latestCoords[1].x, y: latestCoords[1].y });
      if (trail1.length > MAX_TRAIL) trail1.shift();
      if (trail2.length > MAX_TRAIL) trail2.shift();
    }
    drawPendulum(latestCoords);
    const drawTrail = (trail, color) => {
      if (trail.length < 2) return;
      ctx.beginPath();
      const startX = trail[0].x * zoom + offsetX;
      const startY = trail[0].y * zoom + offsetY;
      ctx.moveTo(startX, startY);
      for (let i = 1; i < trail.length; i++) {
        const x = trail[i].x * zoom + offsetX;
        const y = trail[i].y * zoom + offsetY;
        ctx.lineTo(x, y);
      }
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.25;
      ctx.stroke();
    };
    drawTrail(trail1, "rgba(25,118,210,0.7)");
    drawTrail(trail2, "rgba(239,108,0,0.7)");
  }
  requestAnimationFrame(animate);
}
setInterval(pollCoords, 40);
requestAnimationFrame(animate);
document.getElementById("reset-btn").addEventListener("click", async () => {
  await fetch("/reset", { method: "POST" });
  trail1.length = 0;
  trail2.length = 0;
  trailEnabled = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCartesianPlane();

  setTimeout(() => {
    trailEnabled = true;
  }, 500);
});

document.getElementById("restart-btn").addEventListener("click", async () => {
  await fetch("/restart", { method: "POST" });
  trail1.length = 0;
  trail2.length = 0;
  trailEnabled = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCartesianPlane();

  setTimeout(() => {
    trailEnabled = true;
  }, 500);
});

document.getElementById("update-btn").addEventListener("click", async () => {
  const lengthRod1 = document.getElementById("rod1-length").value;
  const lengthRod2 = document.getElementById("rod2-length").value;
  const massBob1 = document.getElementById("bob1-mass").value;
  const massBob2 = document.getElementById("bob2-mass").value;
  const accG = document.getElementById("acc-g").value;
  if (!lengthRod1 || !lengthRod2 || !massBob1 || !massBob2 || !accG) {
    alert("fill all the fields :angry:");
    return;
  } else {
    const data = {
      length_rod_1: lengthRod1,
      length_rod_2: lengthRod2,
      mass_bob_1: massBob1,
      mass_bob_2: massBob2,
      g: accG,
    };
    await fetch("/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((dataR) => {
        console.log("Success:", dataR);
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    trail1.length = 0;
    trail2.length = 0;
    trailEnabled = false;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCartesianPlane();

    setTimeout(() => {
      trailEnabled = true;
    }, 500);
  }
});
const acceleratCtx = document
  .getElementById("acceleration-grph")
  .getContext("2d");

const accelerationChart = new Chart(acceleratCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Bob 1 Acceleration",
        borderColor: "rgba(25,118,210,1)",
        backgroundColor: "rgba(25,118,210,0.08)",
        borderWidth: 3,
        data: [],
        tension: 0.3,
      },
      {
        label: "Bob 2 Acceleration",
        borderColor: "rgba(239,108,0,1)",
        backgroundColor: "rgba(239,108,0,0.08)",
        borderWidth: 3,
        data: [],
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: {
        title: { display: true, text: "Time (s)" },
        ticks: { color: "#555", maxTicksLimit: 12 },
        grid: { color: "rgba(0,0,0,0.05)" },
      },
      y: {
        title: { display: true, text: "Acceleration (m/s²)" },
        ticks: { color: "#555" },
        grid: { color: "rgba(0,0,0,0.05)" },
      },
    },
    plugins: {
      legend: {
        position: "top",
        labels: { color: "#222", font: { size: 14, weight: "bold" } },
      },
    },
  },
});

let lastPositions = null;
let lastVelocities = null;
const dt = 0.04; // this too is milliseconds
let time = 0;
const updatePeriod = 500; // this is milliseconds
let lastUpdate = Date.now();

function updateAccelerationData(coords) {
  const bobs = coords.slice(0, 2);

  if (!lastPositions) {
    lastPositions = bobs.map((c) => ({ x: c.x, y: c.y }));
    lastVelocities = bobs.map(() => ({ x: 0, y: 0 }));
    return;
  }
  const newVelocities = bobs.map((c, i) => ({
    x: (c.x - lastPositions[i].x) / dt,
    y: (c.y - lastPositions[i].y) / dt,
  }));

  const accels = newVelocities.map((v, i) => ({
    x: (v.x - lastVelocities[i].x) / dt,
    y: (v.y - lastVelocities[i].y) / dt,
  }));

  const mag1 = Math.hypot(accels[0].x, accels[0].y);
  const mag2 = Math.hypot(accels[1].x, accels[1].y);
  const now = Date.now();
  if (now - lastUpdate >= updatePeriod) {
    const MAX_POINTS = 80;
    time += updatePeriod / 1000;
    accelerationChart.data.datasets[0].data.push(mag1);
    accelerationChart.data.datasets[1].data.push(mag2);
    accelerationChart.data.labels.push(time.toFixed(1));
    // functionality for the chart to adjust
    if (accelerationChart.data.labels.length > MAX_POINTS) {
      accelerationChart.data.labels.shift();
      accelerationChart.data.datasets[0].data.shift();
      accelerationChart.data.datasets[1].data.shift();
    }

    accelerationChart.update("none");
    lastUpdate = now;
  }

  lastPositions = bobs.map((c) => ({ x: c.x, y: c.y }));
  lastVelocities = newVelocities;
}

const angularvCtx = document.getElementById("angularv-grph").getContext("2d");
const angularVelocityChart = new Chart(angularvCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Bob 1 Angular Velocity (ω₁)",
        borderColor: "rgba(25,118,210,1)",
        backgroundColor: "rgba(25,118,210,0.08)",
        borderWidth: 3,
        data: [],
        tension: 0.3,
      },
      {
        label: "Bob 2 Angular Velocity (ω₂)",
        borderColor: "rgba(239,108,0,1)",
        backgroundColor: "rgba(239,108,0,0.08)",
        borderWidth: 3,
        data: [],
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: {
        title: { display: true, text: "Time (s)" },
        ticks: { color: "#555", maxTicksLimit: 12 },
        grid: { color: "rgba(0,0,0,0.05)" },
      },
      y: {
        title: { display: true, text: "Angular Velocity (rad/s)" },
        ticks: { color: "#555" },
        grid: { color: "rgba(0,0,0,0.05)" },
      },
    },
    plugins: {
      legend: {
        position: "top",
        labels: { color: "#222", font: { size: 14, weight: "bold" } },
      },
    },
  },
});

let lastAngles = null;
let lastAngularUpdate = Date.now();

function updateAngularVelocityData(coords) {
  const b1 = coords[0];
  const b2 = coords[1];

  const theta1 = Math.atan2(b1.y - ORIGIN_Y, b1.x - ORIGIN_X);
  const theta2 = Math.atan2(b2.y - b1.y, b2.x - b1.x);

  if (!lastAngles) {
    lastAngles = [theta1, theta2];
    return;
  }

  const angV1 = (theta1 - lastAngles[0]) / dt; // rad/s
  const angV2 = (theta2 - lastAngles[1]) / dt;

  const now = Date.now();
  if (now - lastAngularUpdate >= updatePeriod) {
    const MAX_POINTS = 80;
    time += updatePeriod / 1000;

    angularVelocityChart.data.datasets[0].data.push(angV1);
    angularVelocityChart.data.datasets[1].data.push(angV2);
    angularVelocityChart.data.labels.push(time.toFixed(1));

    if (angularVelocityChart.data.labels.length > MAX_POINTS) {
      angularVelocityChart.data.labels.shift();
      angularVelocityChart.data.datasets[0].data.shift();
      angularVelocityChart.data.datasets[1].data.shift();
    }

    angularVelocityChart.update("none");
    lastAngularUpdate = now;
  }

  lastAngles = [theta1, theta2];
}
