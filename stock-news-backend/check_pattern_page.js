const fs=require('fs');
const s=fs.readFileSync('firebase_public/pattern-reco.html','utf8');
const js=s.match(/<script>([\s\S]*)<\/script>/)[1];
new Function(js);
console.log('JS OK', s.includes('addEngineOverlay'), s.includes('level-chip'), s.length);
