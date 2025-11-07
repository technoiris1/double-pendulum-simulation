const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

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

let a1 = Math.PI / 2;
let a2 = Math.PI / 2;
let av1 = 0;
let av2 = 0;
let L1 = 150,
  L2 = 150,
  M1 = 10,
  M2 = 10;

let latest = null;

async function pollCoords() {
  try {
    const res = await fetch("/coords", { cache: "no-store" });
    if (res.ok) latest = await res.json();
  } catch (e) {
    console.error(e);
  }
}

setInterval(pollCoords, 50);

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCartesianPlane();

  if (latest) {
    const { x1, y1, x2, y2 } = latest;

    ctx.strokeStyle = "black";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, canvas.height / 2);
    ctx.lineTo(canvas.width / 2 + x1, canvas.height / 2 + y1);
    ctx.lineTo(canvas.width / 2 + x2, canvas.height / 2 + y2);
    ctx.stroke();

    ctx.fillStyle = "red";
    ctx.beginPath();
    ctx.arc(canvas.width / 2 + x1, canvas.height / 2 + y1, 10, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "blue";
    ctx.beginPath();
    ctx.arc(canvas.width / 2 + x2, canvas.height / 2 + y2, 10, 0, Math.PI * 2);
    ctx.fill();
  }

  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
