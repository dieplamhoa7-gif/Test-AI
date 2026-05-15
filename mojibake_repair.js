// Repairs UTF-8 Vietnamese text that was accidentally decoded/rendered as CP437/OEM.
// Example: "Gi├í B─ÉS" -> "Giá BĐS".

const CP437 = (() => {
  const chars = 'ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ';
  const m = new Map();
  for (let i = 0; i < chars.length; i++) m.set(chars[i], 0x80 + i);
  return m;
})();

function repairMojibake(input) {
  const s = String(input ?? '');
  if (!/[├─╞║╗╝╜╛╟╠╣╦╩╬╨╧╤╥╙╘╒╓╫╪┐└┴┬┼╡╢╖╕�]/.test(s)) return s;
  const bytes = [];
  let convertible = 0;
  for (const ch of s) {
    const code = ch.codePointAt(0);
    if (code <= 0x7f) bytes.push(code);
    else if (CP437.has(ch)) { bytes.push(CP437.get(ch)); convertible++; }
    else bytes.push(...Buffer.from(ch, 'utf8'));
  }
  if (!convertible) return s;
  const repaired = Buffer.from(bytes).toString('utf8');
  // Only accept if it reduced obvious mojibake.
  const bad = (x) => (x.match(/[├─╞║╗╝╜╛╟╠╣╦╩╬╨╧╤╥╙╘╒╓╫╪┐└┴┬┼╡╢╖╕]/g) || []).length;
  return bad(repaired) < bad(s) ? repaired : s;
}

module.exports = { repairMojibake };
