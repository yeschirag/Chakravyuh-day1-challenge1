// Silk Canvas Animation
const canvas = document.getElementById("silkCanvas")
const ctx = canvas.getContext("2d")

function resizeCanvas() {
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
}

resizeCanvas()
window.addEventListener("resize", resizeCanvas)

// Improved Perlin-like noise function (from shader)
function noise(x, y) {
  // Using gl_FragCoord.xy magic from shader
  const G = 2.718281828459045;
  const r_x = G * Math.sin(G * x);
  const r_y = G * Math.sin(G * y);
  const n = r_x * r_y * (1.0 + x);
  return n - Math.floor(n); // fract()
}

// Silk texture animation with shader-like effects
let time = 0
const particles = []

class Particle {
  constructor() {
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.vx = (Math.random() - 0.5) * 0.5
    this.vy = (Math.random() - 0.5) * 0.5
    this.life = Math.random() * 100 + 50
    this.maxLife = this.life
    this.size = Math.random() * 2 + 1
  }

  update() {
    this.x += this.vx
    this.y += this.vy
    this.life--

    if (this.x < 0 || this.x > canvas.width) this.vx *= -1
    if (this.y < 0 || this.y > canvas.height) this.vy *= -1
  }

  draw() {
    const alpha = (this.life / this.maxLife) * 0.3
    ctx.fillStyle = `rgba(220, 20, 60, ${alpha})` // Crimson red
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
}

function drawSilkTexture() {
  // Clear with dark background
  ctx.fillStyle = "#0a0a0a"
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  time += 0.01
  const speed = 5
  const scale = 1
  const rotation = 0 // Rotation from React code was 0
  const noiseIntensity = 1.5

  // Create image data for pixel-level control
  const imageData = ctx.createImageData(canvas.width, canvas.height)
  const data = imageData.data

  // Generate silk pattern using shader-like logic
  for (let py = 0; py < canvas.height; py += 2) {
    for (let px = 0; px < canvas.width; px += 2) {
      
      // --- Start of logic adapted from fragment shader ---
      let uv_x = px / canvas.width
      let uv_y = py / canvas.height
      uv_x *= scale
      uv_y *= scale
      const cos_r = Math.cos(rotation)
      const sin_r = Math.sin(rotation)
      const rotated_x = uv_x * cos_r - uv_y * sin_r
      const rotated_y = uv_x * sin_r + uv_y * cos_r
      const tex_x = rotated_x * scale
      const tex_y = rotated_y * scale
      // --- End of logic adapted from fragment shader ---

      const tOffset = speed * time
      const distorted_y = tex_y + 0.03 * Math.sin(8.0 * tex_x - tOffset)

      const pattern =
        0.6 +
        0.4 *
          Math.sin(
            5.0 * (tex_x + distorted_y + Math.cos(3.0 * tex_x + 5.0 * distorted_y) + 0.02 * tOffset) +
              Math.sin(20.0 * (tex_x + distorted_y - 0.1 * tOffset)),
          )

      const rnd = noise(px, py)
      const noiseValue = (rnd / 15.0) * noiseIntensity
      const colorIntensity = Math.max(0, Math.min(1, pattern - noiseValue))

      const r = Math.floor(220 * colorIntensity)
      const g = Math.floor(20 * colorIntensity)
      const b = Math.floor(60 * colorIntensity)
      const a = Math.floor(255 * colorIntensity * 0.4) // Apply alpha for silk transparency

      const index = (py * canvas.width + px) * 4
      data[index] = r
      data[index + 1] = g
      data[index + 2] = b
      data[index + 3] = a

      // Mirror to adjacent pixels for performance
      if (px + 1 < canvas.width) {
        data[index + 4] = r
        data[index + 5] = g
        data[index + 6] = b
        data[index + 7] = a
      }
      if (py + 1 < canvas.height) {
        const nextIndex = ((py + 1) * canvas.width + px) * 4
        data[nextIndex] = r
        data[nextIndex + 1] = g
        data[nextIndex + 2] = b
        data[nextIndex + 3] = a
        if (px + 1 < canvas.width) {
          data[nextIndex + 4] = r
          data[nextIndex + 5] = g
          data[nextIndex + 6] = b
          data[nextIndex + 7] = a
        }
      }
    }
  }

  ctx.putImageData(imageData, 0, 0)

  // Update and draw particles (existing feature)
  if (Math.random() < 0.3) {
    particles.push(new Particle())
  }

  for (let i = particles.length - 1; i >= 0; i--) {
    particles[i].update()
    particles[i].draw()

    if (particles[i].life <= 0) {
      particles.splice(i, 1)
    }
  }

  // --- START: Line Options ---
  ctx.strokeStyle = "rgba(220, 20, 60, 0.08)"
  ctx.lineWidth = 1 // Lines are now 1px thin
  for (let i = 0; i < 5; i++) {
    ctx.beginPath()
    ctx.moveTo(0, canvas.height * (i / 5) + Math.sin(time + i) * 30)
    ctx.quadraticCurveTo(
      canvas.width * 0.25,
      canvas.height * (i / 5) + Math.cos(time + i) * 40,
      canvas.width * 0.5,
      canvas.height * (i / 5) + Math.sin(time + i) * 30,
    )
    ctx.quadraticCurveTo(
      canvas.width * 0.75,
      canvas.height * (i / 5) + Math.cos(time + i) * 40,
      canvas.width,
      canvas.height * (i / 5) + Math.sin(time + i) * 30,
    )
    ctx.stroke()
  }
}

function animate() {
  drawSilkTexture()
  requestAnimationFrame(animate)
}

// Start the animation
animate()

// --- Form Handling ---

// Screens
const loginScreen = document.getElementById("loginScreen")
const riddleScreen = document.getElementById("riddleScreen")
const successScreen = document.getElementById("successScreen") // NEW

// Login Screen
const loginForm = document.getElementById("loginForm")
const teamIdInput = document.getElementById("teamId")
const passwordInput = document.getElementById("password")

// Riddle Screen
const displayTeamId = document.getElementById("displayTeamId")
const nextBtn = document.getElementById("nextBtn")
const logoutBtn = document.getElementById("logoutBtn")

// NEW: Verification Portal (Level 5)
const verificationForm = document.getElementById("verificationForm")
const finalAnswerInput = document.getElementById("finalAnswer")
const submitAnswerBtn = document.getElementById("submitAnswerBtn")

// NEW: Success Screen
const displayTeamIdSuccess = document.getElementById("displayTeamIdSuccess")
const logoutSuccessBtn = document.getElementById("logoutSuccessBtn")


// --- Mock Riddles & Answers ---
const riddlesPool = [
  {
    riddle:
      "Step by step I descend, each gradient pays the cost. Hours stand still, yet outcomes rearrange—Not magic, just models that make time strange.",
    lead: "AI/ML Lead",
  },
  {
    riddle:
      "I build bridges between worlds, connecting what was separate. My threads weave patterns invisible to the eye, yet felt in every interaction.",
    lead: "Web Development Lead",
  },
  {
    riddle:
      "I guard the gates of knowledge, deciding who enters and what stays hidden. Trust is my currency, encryption my language.",
    lead: "Security Lead",
  },
]

// Mock answer database
const correctAnswers = {
    "TEAM-001": "THIS IS MARVEL",
    "TEAM-002": "AVENGERS ASSEMBLE",
    "DEFAULT": "THIS IS MARVEL" // Fallback for any team
}

// Global var to store logged-in team ID
let currentTeamId = "";

// --- Custom Modal ---
function showCustomAlert(message, buttonText = "PROCEED") {
    // Check if an alert already exists
    if (document.querySelector('.custom-alert-overlay')) {
        return;
    }

    const overlay = document.createElement('div');
    overlay.className = 'custom-alert-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'custom-alert-modal';
    
    const messageP = document.createElement('p');
    messageP.innerHTML = message.replace(/\n/g, '<br>'); // Respect newlines
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'custom-alert-btn';
    closeBtn.textContent = buttonText;
    
    modal.appendChild(messageP);
    modal.appendChild(closeBtn);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    closeBtn.onclick = () => {
        overlay.classList.add('fade-out');
        setTimeout(() => {
            if (document.body.contains(overlay)) {
                document.body.removeChild(overlay);
            }
        }, 300);
    };
    
    // Add styles for the custom alert
    const alertStyles = `
        .custom-alert-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(5px);
            animation: fadeIn 0.3s ease;
        }
        .custom-alert-overlay.fade-out {
            animation: fadeOut 0.3s ease forwards;
        }
        .custom-alert-modal {
            background: var(--card-bg, rgba(20, 10, 20, 0.9));
            border: 2px solid var(--primary-red, #dc143c);
            border-radius: 16px;
            padding: 30px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 0 40px var(--glow-red, rgba(220, 20, 60, 0.6));
            text-align: center;
            animation: slideIn 0.3s ease-out;
        }
        .custom-alert-modal p {
            font-size: 16px;
            line-height: 1.6;
            color: var(--text-primary, #fff);
            margin-bottom: 25px;
        }
        .custom-alert-btn {
            position: relative;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-family: "Inter", sans-serif;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            overflow: hidden;
            background: linear-gradient(135deg, var(--primary-red, #dc143c), #ff1744);
            color: white;
            border: 1px solid var(--primary-red, #dc143c);
            box-shadow: 0 0 20px var(--glow-red, rgba(220, 20, 60, 0.6));
        }
        .custom-alert-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 30px var(--glow-red, rgba(220, 20, 60, 0.8));
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        @keyframes slideIn {
            from { transform: scale(0.9) translateY(10px); opacity: 0.5; }
            to { transform: scale(1) translateY(0); opacity: 1; }
        }
    `;
    
    let styleTag = document.getElementById('custom-alert-styles');
    if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.id = 'custom-alert-styles';
        styleTag.innerHTML = alertStyles;
        document.head.appendChild(styleTag);
    }
}


// --- Event Listeners ---

// LEVEL 1: Login
loginForm.addEventListener("submit", (e) => {
  e.preventDefault()

  const teamId = teamIdInput.value.trim().toUpperCase()
  const password = passwordInput.value.trim()

  if (teamId && password) {
    currentTeamId = teamId; // Store team ID
    
    // Trigger screen shake
    const loginCard = document.querySelector('.login-card');
    loginCard.classList.add('shake');
    setTimeout(() => { loginCard.classList.remove('shake'); }, 500);

    // Simulate successful login
    displayTeamId.textContent = currentTeamId;
    displayTeamIdSuccess.textContent = currentTeamId; // Set for success screen

    // Assign a random riddle (as per PDF)
    const randomRiddle = riddlesPool[Math.floor(Math.random() * riddlesPool.length)]
    document.getElementById("riddleText").textContent = randomRiddle.riddle
    
    // Switch screens
    loginScreen.classList.remove("active")
    setTimeout(() => {
      riddleScreen.classList.add("active")
    }, 100)

    loginForm.reset()
  }
})

// "PROCEED" button
nextBtn.addEventListener("click", () => {
  // Trigger screen shake
  const riddleCard = document.querySelector('.riddle-card');
  riddleCard.classList.add('shake');
  setTimeout(() => { riddleCard.classList.remove('shake'); }, 500);

  // Show custom alert as per PDF flow
  // UPDATED: Made message cryptic
  showCustomAlert("Your riddle is now active. Good luck, Avenger.", "GOOD LUCK")
})

// VERIFICATION: Submit Final Answer
verificationForm.addEventListener("submit", (e) => {
    e.preventDefault();
    
    const answer = finalAnswerInput.value.trim().toUpperCase();
    if (!answer) return;

    // Trigger screen shake
    const riddleCard = document.querySelector('.riddle-card');
    riddleCard.classList.add('shake');
    setTimeout(() => { riddleCard.classList.remove('shake'); }, 500);

    // Check answer (mocked)
    const expectedAnswer = correctAnswers[currentTeamId] || correctAnswers["DEFAULT"];

    if (answer === expectedAnswer) {
        // CORRECT!
        setTimeout(() => {
            riddleScreen.classList.remove("active");
            successScreen.classList.add("active");
        }, 600); // Wait for shake to finish
    } else {
        // INCORRECT!
        showCustomAlert("ACCESS DENIED\n\nThat is not the correct code. The timeline is in danger!", "TRY AGAIN");
    }

    finalAnswerInput.value = ""; // Clear input
});


// Logout Function
function logout() {
    riddleScreen.classList.remove("active");
    successScreen.classList.remove("active"); // Hide success screen too
    setTimeout(() => {
        loginScreen.classList.add("active");
    }, 100);
    currentTeamId = ""; // Clear stored team
}

// Attach logout to both buttons
logoutBtn.addEventListener("click", logout);
logoutSuccessBtn.addEventListener("click", logout);


// Magic particle effects on mouse move
document.addEventListener("mousemove", (e) => {
  const magicParticles = document.querySelector(".magic-particles")

  if (Math.random() < 0.1) {
    const particle = document.createElement("div")
    particle.style.position = "fixed"
    particle.style.left = e.clientX + "px"
    particle.style.top = e.clientY + "px"
    particle.style.width = "4px"
    particle.style.height = "4px"
    particle.style.background = "rgba(220, 20, 60, 0.6)"
    particle.style.borderRadius = "50%"
    particle.style.pointerEvents = "none"
    particle.style.boxShadow = "0 0 10px rgba(220, 20, 60, 0.8)"

    magicParticles.appendChild(particle)

    // Animate particle
    let opacity = 1
    let scale = 1
    const interval = setInterval(() => {
      opacity -= 0.05
      scale += 0.1
      particle.style.opacity = opacity
      particle.style.transform = `scale(${scale})`

      if (opacity <= 0) {
        clearInterval(interval)
        if (magicParticles.contains(particle)) {
            particle.remove()
        }
      }
    }, 30)
  }
})

