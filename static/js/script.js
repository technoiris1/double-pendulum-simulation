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
  ctx.lineWidth = zoom;
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
