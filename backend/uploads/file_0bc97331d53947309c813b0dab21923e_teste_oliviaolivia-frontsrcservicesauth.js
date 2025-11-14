export function decodeJwt(token) {
  try {
    const [, payload] = token.split('.');
    if (!payload) return null;
    let b64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const pad = b64.length % 4;
    if (pad) b64 += '='.repeat(4 - pad);
    const json = atob(b64);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function scheduleAutoLogout(expUnix, onLogout, skewSec = 60) {
  if (!expUnix) return;
  const msUntil = expUnix * 1000 - Date.now() - skewSec * 1000;
  if (msUntil <= 0) {
    onLogout();
    return;
  }
  if (window.__logoutTimer) clearTimeout(window.__logoutTimer);
  window.__logoutTimer = setTimeout(onLogout, msUntil);
}
