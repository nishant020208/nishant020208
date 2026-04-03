<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nishant | Terminal Portfolio</title>

<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600&family=Source+Code+Pro&display=swap" rel="stylesheet">

<style>
*{
  margin:0;
  padding:0;
  box-sizing:border-box;
  font-family:'Source Code Pro', monospace;
}

body{
  background: radial-gradient(circle at top, #0d1117, #02040a);
  color:#00f7ff;
  overflow-x:hidden;
}

/* NAV */
nav{
  position:fixed;
  width:100%;
  top:0;
  background:rgba(0,0,0,0.6);
  backdrop-filter: blur(10px);
  display:flex;
  justify-content:center;
  gap:40px;
  padding:15px;
  z-index:1000;
}

nav a{
  color:#00f7ff;
  text-decoration:none;
  transition:0.3s;
}
nav a:hover{color:#00ff9c}

/* HERO */
.hero{
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  flex-direction:column;
  text-align:center;
}

.glow{
  font-size:2.5rem;
  text-shadow:0 0 10px #00f7ff, 0 0 40px #00f7ff;
}

/* typing */
.typing{
  border-right:2px solid #00f7ff;
  white-space:nowrap;
  overflow:hidden;
  animation: typing 4s steps(30), blink .5s infinite alternate;
}
@keyframes typing{
  from{width:0}
  to{width:100%}
}
@keyframes blink{
  50%{border-color:transparent}
}

/* cards */
.container{
  padding:80px 10%;
}

.card{
  background:rgba(255,255,255,0.05);
  border:1px solid rgba(0,255,255,0.2);
  padding:20px;
  border-radius:20px;
  backdrop-filter: blur(15px);
  margin:20px 0;
  transition:0.3s;
}
.card:hover{
  transform:scale(1.03);
  box-shadow:0 0 20px #00f7ff;
}

/* grid */
.grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
  gap:20px;
}

/* terminal */
.terminal{
  background:#000;
  padding:20px;
  border-radius:10px;
  color:#00ff9c;
  height:200px;
  overflow:auto;
}

/* button */
button{
  padding:10px 20px;
  border:none;
  background:#00f7ff;
  color:#000;
  cursor:pointer;
  border-radius:10px;
  margin-top:10px;
}

/* footer */
footer{
  text-align:center;
  padding:30px;
  color:#aaa;
}
</style>
</head>

<body>

<nav>
<a href="#">Home</a>
<a href="#about">About</a>
<a href="#projects">Projects</a>
<a href="#terminal">Terminal</a>
</nav>

<section class="hero">
<h1 class="glow typing">> Initializing Nishant...</h1>
<p>Developer | Builder | No Excuses</p>
</section>

<section class="container" id="about">
<h2>About</h2>
<div class="card">
<pre>
> whoami
Nishant

> focus
Web Dev | Blockchain | ERP

> quote
"you can sleep when you are dead"
</pre>
</div>
</section>

<section class="container" id="projects">
<h2>Projects</h2>
<div class="grid">

<div class="card">
<h3>SVIT ERP</h3>
<p>Full campus management system</p>
</div>

<div class="card">
<h3>Vardant</h3>
<p>Shopkeeper + voting system</p>
</div>

<div class="card">
<h3>Blockchain App</h3>
<p>Learning platform</p>
</div>

<div class="card">
<h3>Terminal UI</h3>
<p>Hacker-style portfolio</p>
</div>

</div>
</section>

<section class="container" id="terminal">
<h2>Terminal</h2>

<div class="terminal" id="output">
> type "help"
</div>

<input type="text" id="cmd" placeholder="Enter command..." style="width:100%;padding:10px;background:black;color:#00ff9c;border:none;">
<button onclick="run()">Run</button>

</section>

<footer>
© 2026 Nishant | Built like a machine
</footer>

<script>
function run(){
  let input = document.getElementById("cmd").value;
  let out = document.getElementById("output");

  let response = "";

  if(input=="help"){
    response = "commands: about, skills, projects";
  }
  else if(input=="about"){
    response = "Nishant | Developer";
  }
  else if(input=="skills"){
    response = "HTML CSS JS Bootstrap";
  }
  else if(input=="projects"){
    response = "ERP | Vardant | Blockchain";
  }
  else{
    response = "command not found";
  }

  out.innerHTML += "<br>> " + input + "<br>" + response;
}
</script>

</body>
</html>
