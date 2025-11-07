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

let lastUpdate = 0;
let updating = false;
async function update() {
  if (updating) return;
  updating = true;
  try {
    const res = await fetch("/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ a1, a2, av1, av2 }),
    });

    if (!res.ok) {
      console.error("Bad response:", res.status);
      return;
    }

    const data = await res.json();

    a1 = data.a1;
    a2 = data.a2;
    av1 = data.av1;
    av2 = data.av2;
    L1 = data.L1;
    L2 = data.L2;
    M1 = data.M1;
    M2 = data.M2;
  } catch (err) {
    console.error("Fetch error:", err);
  } finally {
    updating = false;
  }
}

function animate(timestamp) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawCartesianPlane();
  if (timestamp - lastUpdate > 50) {
    update();
    lastUpdate = timestamp;
  }

  const x1 = L1 * Math.sin(a1);
  const y1 = L1 * Math.cos(a1);
  const x2 = x1 + L2 * Math.sin(a2);
  const y2 = y1 + L2 * Math.cos(a2);

  // draw arms
  ctx.strokeStyle = "black";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(canvas.width / 2, canvas.height / 2);
  ctx.lineTo(canvas.width / 2 + x1, canvas.height / 2 + y1);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(canvas.width / 2 + x1, canvas.height / 2 + y1);
  ctx.lineTo(canvas.width / 2 + x2, canvas.height / 2 + y2);
  ctx.stroke();

  // draw bobs
  ctx.fillStyle = "red";
  ctx.beginPath();
  ctx.arc(canvas.width / 2 + x1, canvas.height / 2 + y1, M1, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "blue";
  ctx.beginPath();
  ctx.arc(canvas.width / 2 + x2, canvas.height / 2 + y2, M2, 0, Math.PI * 2);
  ctx.fill();

  requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
