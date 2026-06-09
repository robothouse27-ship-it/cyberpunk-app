// Encrypt the plaintext app (app.src.html) into a password-locked index.html.
// Matches the original combat-zone-roster gate: PBKDF2(SHA-256, 250k) -> AES-GCM-256,
// decrypted client-side into a Blob URL. The password is read from the CZ_PW env var
// so it never has to be written into a file or the repo.
//
// Usage:  CZ_PW='your-password' node build_locked.mjs
import { readFileSync, writeFileSync } from 'fs';
import { webcrypto as crypto } from 'crypto';

const pw = process.env.CZ_PW;
if (!pw) { console.error('ERROR: set the password first, e.g.  CZ_PW=1234 node build_locked.mjs'); process.exit(1); }

// SRC/OUT and the lock-screen labels can be overridden via env so the same
// script builds both apps:
//   CZ_PW=… node build_locked.mjs                                  -> index.html (Combat Zone)
//   CZ_PW=… CZ_SRC=playtest.src.html CZ_OUT=playtest.html \
//     CZ_TITLE='PLAYTEST — Locked' CZ_HEADING='PLAYTEST' node build_locked.mjs
const SRC = process.env.CZ_SRC || 'app.src.html';
const OUT = process.env.CZ_OUT || 'index.html';
const LOCK_TITLE = process.env.CZ_TITLE || 'Combat Zone — Locked';
const LOCK_HEADING = process.env.CZ_HEADING || 'Combat Zone Roster';
const ITER = 250000;

const plaintext = readFileSync(SRC);
const enc = new TextEncoder();
const salt = crypto.getRandomValues(new Uint8Array(16));
const iv = crypto.getRandomValues(new Uint8Array(12));
const base = await crypto.subtle.importKey('raw', enc.encode(pw), 'PBKDF2', false, ['deriveKey']);
const key = await crypto.subtle.deriveKey(
  { name: 'PBKDF2', salt, iterations: ITER, hash: 'SHA-256' },
  base, { name: 'AES-GCM', length: 256 }, false, ['encrypt']);
const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, plaintext));
const b64 = u => Buffer.from(u).toString('base64');

const wrapper = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${LOCK_TITLE}</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    background:#0a0a12;color:#e8e8f0;
    background-image:radial-gradient(circle at 30% 20%,rgba(255,0,90,.12),transparent 60%),radial-gradient(circle at 70% 80%,rgba(0,200,255,.12),transparent 60%);}
  .box{width:min(360px,90vw);padding:32px 28px;border:1px solid #2a2a3a;border-radius:16px;
    background:rgba(18,18,28,.85);box-shadow:0 0 40px rgba(0,0,0,.6);text-align:center;backdrop-filter:blur(6px)}
  h1{font-size:20px;margin:0 0 4px;letter-spacing:.5px}
  .sub{font-size:13px;color:#8a8aa0;margin:0 0 22px}
  input{width:100%;padding:13px 14px;font-size:16px;border-radius:10px;border:1px solid #34344a;
    background:#0e0e18;color:#fff;outline:none;text-align:center;letter-spacing:2px}
  input:focus{border-color:#ff2d6e}
  button{margin-top:14px;width:100%;padding:13px;font-size:15px;font-weight:600;border:none;border-radius:10px;
    background:linear-gradient(90deg,#ff2d6e,#ff6a3d);color:#fff;cursor:pointer}
  button:active{transform:translateY(1px)}
  .err{color:#ff5a7a;font-size:13px;min-height:18px;margin-top:12px}
  .lock{font-size:34px;margin-bottom:8px}
</style>
</head>
<body>
  <form class="box" id="f">
    <div class="lock">&#128274;</div>
    <h1>${LOCK_HEADING}</h1>
    <p class="sub">Enter the password to unlock.</p>
    <input id="pw" type="password" inputmode="numeric" autocomplete="current-password" placeholder="Password" autofocus>
    <button type="submit" id="btn">Unlock</button>
    <div class="err" id="err"></div>
  </form>
<script>
const SALT=dec64("${b64(salt)}"), IV=dec64("${b64(iv)}"), DATA=dec64("${b64(ct)}"), ITER=${ITER};
function dec64(s){const b=atob(s),u=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u;}
async function unlock(pw){
  const enc=new TextEncoder();
  const base=await crypto.subtle.importKey("raw",enc.encode(pw),"PBKDF2",false,["deriveKey"]);
  const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:SALT,iterations:ITER,hash:"SHA-256"},base,{name:"AES-GCM",length:256},false,["decrypt"]);
  const buf=await crypto.subtle.decrypt({name:"AES-GCM",iv:IV},key,DATA);
  return new TextDecoder().decode(buf);
}
const f=document.getElementById("f"),err=document.getElementById("err"),btn=document.getElementById("btn");
f.addEventListener("submit",async e=>{
  e.preventDefault();err.textContent="";btn.textContent="Unlocking\\u2026";btn.disabled=true;
  try{
    let html=await unlock(document.getElementById("pw").value);
    sessionStorage.setItem("cz_pw_ok","1");
    // The app runs from a blob: URL, where relative paths (e.g. cards/x.png) can't
    // resolve to the real site. Inject the true base so the app can build absolute
    // asset URLs from it.
    var ab=location.href.replace(/[?#].*$/,"").replace(/[^/]*$/,"");
    var inj="<scr"+"ipt>window.__APP_BASE__="+JSON.stringify(ab)+"</scr"+"ipt>";
    html=html.replace("<head>","<head>"+inj);
    const blob=new Blob([html],{type:"text/html"});
    location.replace(URL.createObjectURL(blob));
  }catch(_){
    err.textContent="Wrong password \\u2014 try again.";
    btn.textContent="Unlock";btn.disabled=false;
    document.getElementById("pw").select();
  }
});
</script>
</body>
</html>
`;
writeFileSync(OUT, wrapper);
console.log(`Wrote locked ${OUT} (${ct.length} bytes ciphertext from ${plaintext.length} bytes source).`);
