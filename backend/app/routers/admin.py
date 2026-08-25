<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin — Backstage Legends</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0a0a0b;--surface:#121214;--surface-2:#1a1a1e;
  --border:rgba(212,175,55,.22);
  --gold:#d4af37;--gold-light:#f0d77b;--gold-dark:#a8861f;
  --ink:#f5f0e6;--muted:#9a958c;
  --red:#e11d3c;--red-soft:rgba(225,29,60,.12);
  --green:#1a9c5e;--green-soft:rgba(26,156,94,.12);
  --font-display:'Cinzel',serif;--font-body:'Inter',sans-serif;--font-mono:'JetBrains Mono',monospace;
}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);min-height:100vh;display:flex;flex-direction:column;position:relative;}
a{color:inherit;text-decoration:none;}
.bg{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}
.glow{position:absolute;border-radius:50%;filter:blur(90px);opacity:.28;}
.g1{width:380px;height:380px;top:-10%;left:5%;background:radial-gradient(circle,rgba(212,175,55,.4),transparent 70%);}
.g2{width:300px;height:300px;bottom:5%;right:5%;background:radial-gradient(circle,rgba(240,215,123,.25),transparent 70%);}
nav{
  position:relative;z-index:2;display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:16px 24px;border-bottom:1px solid var(--border);background:rgba(10,10,11,.9);backdrop-filter:blur(12px);flex-wrap:wrap;
}
.logo{font-family:var(--font-display);font-weight:600;font-size:18px;color:var(--gold);}
.logo span{color:var(--gold-light);}
.nav-right{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
.who{font-family:var(--font-mono);font-size:11px;color:var(--muted);}
.who b{color:var(--gold-light);}
.btn{
  font-weight:600;font-size:13px;padding:8px 14px;border-radius:999px;border:1px solid var(--border);
  background:transparent;cursor:pointer;color:var(--ink);font-family:inherit;
}
.btn:hover{border-color:var(--gold);color:var(--gold-light);}
.btn.danger{border-color:rgba(225,29,60,.45);color:#f0a0a8;}
.btn.danger:hover{background:var(--red-soft);}
.btn.ok{border-color:rgba(26,156,94,.45);color:#7dcea0;}
.btn.ok:hover{background:var(--green-soft);}
.btn.primary{
  background:linear-gradient(135deg,var(--gold-light),var(--gold),var(--gold-dark));
  border:none;color:#0a0a0b;
}
.btn.primary:hover{filter:brightness(1.08);}
main{position:relative;z-index:1;flex:1;padding:28px 20px 48px;max-width:920px;width:100%;margin:0 auto;}
h1{font-family:var(--font-display);font-size:clamp(24px,4vw,30px);margin:0 0 8px;color:var(--gold-light);font-weight:600;}
.lead{color:var(--muted);font-size:14px;margin:0 0 24px;line-height:1.5;}
.section-title{font-family:var(--font-display);font-size:20px;margin:40px 0 8px;color:var(--gold-light);font-weight:600;}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px;}
.toolbar .count{font-family:var(--font-mono);font-size:12px;color:var(--muted);}
.card{
  background:rgba(18,18,20,.92);border:1px solid var(--border);border-radius:16px;padding:16px;margin-bottom:12px;
}
.card h2{margin:0;font-size:16px;font-weight:600;color:var(--ink);}
.meta{font-family:var(--font-mono);font-size:11px;color:var(--muted);margin-top:4px;word-break:break-all;}
.badge{display:inline-block;font-family:var(--font-mono);font-size:10px;padding:3px 8px;border-radius:999px;margin-top:8px;}
.badge.on{background:var(--green-soft);color:#7dcea0;}
.badge.off{background:var(--red-soft);color:#f0a0a8;}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;}
.artists{margin-top:12px;padding-top:12px;border-top:1px solid var(--border);display:none;}
.artists.show{display:block;}
.artists li{font-size:13px;color:var(--muted);margin:4px 0;}
.empty,.err{text-align:center;padding:40px 16px;color:var(--muted);font-family:var(--font-mono);font-size:13px;}
.err{color:#f0a0a8;}
.table-wrap{border:1px solid var(--border);border-radius:16px;overflow:hidden;background:rgba(18,18,20,.92);}
table{width:100%;border-collapse:collapse;}
th,td{padding:12px 14px;text-align:left;font-size:13px;border-bottom:1px solid var(--border);vertical-align:top;}
th{font-family:var(--font-mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--gold);background:rgba(212,175,55,.06);}
td.email{word-break:break-all;font-weight:500;}
td.muted{color:var(--muted);font-size:12px;}
tr:last-child td{border-bottom:none;}
@media(max-width:520px){th:nth-child(3),td:nth-child(3){display:none;}}
</style>
</head>
<body>
<div class="bg"><div class="glow g1"></div><div class="glow g2"></div></div>
<nav>
  <span class="logo"><span>◆</span> Backstage Legends</span>
  <div class="nav-right">
    <span class="who">Admin : <b id="who">—</b></span>
    <a class="btn" href="manager-dashboard.html">Espace artistes</a>
    <button type="button" class="btn primary" id="logoutBtn">Se déconnecter</button>
  </div>
</nav>
<main>
  <h1>Managers clients</h1>
  <p class="lead">Bloquez un compte en cas d’infraction. Débloquez après régularisation.</p>
  <div id="list"><div class="empty">Chargement…</div></div>

  <h2 class="section-title">Emails fans inscrits</h2>
  <p class="lead">Fans connectés par email. Copiez la liste pour envoyer des invitations.</p>
  <div class="toolbar">
    <button type="button" class="btn primary" id="btnCopyEmails">Copier tous les emails</button>
    <button type="button" class="btn" id="btnRefreshFans">Actualiser</button>
    <span class="count" id="fansCount">—</span>
  </div>
  <div id="fansBox"><div class="empty">Chargement…</div></div>
</main>
<script src="api.js"></script>
<script>
(function () {
  var token = localStorage.getItem('backstage_token');
  var role = localStorage.getItem('backstage_role');
  if (!token || role !== 'admin') { location.replace('login.html'); return; }

  document.getElementById('who').textContent =
    localStorage.getItem('backstage_username') || localStorage.getItem('backstage_email') || 'Admin';

  document.getElementById('logoutBtn').onclick = function () {
    if (typeof logout === 'function') logout();
    else {
      ['backstage_token','backstage_email','backstage_username','backstage_role'].forEach(function (k) { localStorage.removeItem(k); });
      location.href = 'login.html';
    }
  };

  var listEl = document.getElementById('list');
  var fansBox = document.getElementById('fansBox');
  var fansCount = document.getElementById('fansCount');
  var fanEmails = [];

  function formatDate(iso) {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch (e) { return '—'; }
  }

  async function loadFans() {
    fansBox.innerHTML = '<div class="empty">Chargement…</div>';
    fansCount.textContent = '—';
    fanEmails = [];
    try {
      var fans = await api('/admin/fans');
      if (!Array.isArray(fans)) fans = [];
      fanEmails = fans.map(function (f) { return f.email; }).filter(Boolean);
      fansCount.textContent = fans.length + ' fan(s)';
      if (!fans.length) {
        fansBox.innerHTML = '<div class="empty">Aucun fan inscrit pour le moment.</div>';
        return;
      }
      var rows = fans.map(function (f) {
        return '<tr><td class="email">' + (f.email || '') + '</td><td class="muted">' + (f.username || '—') +
          '</td><td class="muted">' + formatDate(f.created_at) + '</td><td><span class="badge ' +
          (f.is_blocked ? 'off' : 'on') + '">' + (f.is_blocked ? 'Bloqué' : 'Actif') + '</span></td></tr>';
      }).join('');
      fansBox.innerHTML = '<div class="table-wrap"><table><thead><tr><th>Email</th><th>Pseudo</th><th>Inscrit le</th><th>Statut</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
    } catch (err) {
      fansBox.innerHTML = '<div class="err">' + (err.message || err) + '</div>';
      fansCount.textContent = 'erreur';
    }
  }

  document.getElementById('btnCopyEmails').onclick = function () {
    if (!fanEmails.length) { alert('Aucun email à copier.'); return; }
    var text = fanEmails.join(', ');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        alert(fanEmails.length + ' email(s) copiés.');
      }).catch(function () { prompt('Copiez :', text); });
    } else prompt('Copiez :', text);
  };
  document.getElementById('btnRefreshFans').onclick = loadFans;

  async function load() {
    listEl.innerHTML = '<div class="empty">Chargement…</div>';
    try {
      var managers = await api('/admin/managers');
      if (!managers.length) {
        listEl.innerHTML = '<div class="empty">Aucun manager client.</div>';
        return;
      }
      listEl.innerHTML = '';
      managers.forEach(function (m) {
        var card = document.createElement('div');
        card.className = 'card';
        var blocked = !!m.is_blocked;
        card.innerHTML =
          '<div><h2>' + (m.username || '') + '</h2>' +
          '<div class="meta">' + (m.email || '') + '</div>' +
          '<div class="meta">' + (m.artist_count || 0) + ' artiste(s)</div>' +
          '<span class="badge ' + (blocked ? 'off' : 'on') + '">' + (blocked ? 'Bloqué' : 'Actif') + '</span></div>' +
          '<div class="actions">' +
            '<button type="button" class="btn" data-art="1">Voir artistes</button>' +
            (blocked
              ? '<button type="button" class="btn ok" data-un="1">Débloquer</button>'
              : '<button type="button" class="btn danger" data-bl="1">Bloquer</button>') +
          '</div><ul class="artists" data-box="1"></ul>';

        var box = card.querySelector('[data-box]');
        card.querySelector('[data-art]').onclick = async function () {
          if (box.classList.contains('show') && box.dataset.loaded) { box.classList.toggle('show'); return; }
          box.innerHTML = '<li>Chargement…</li>';
          box.classList.add('show');
          try {
            var arts = await api('/admin/managers/' + encodeURIComponent(m.id) + '/artists');
            box.innerHTML = !arts.length ? '<li>Aucun artiste</li>' :
              arts.map(function (a) { return '<li>' + (a.name || '') + (a.is_published ? '' : ' (brouillon)') + '</li>'; }).join('');
            box.dataset.loaded = '1';
          } catch (err) {
            box.innerHTML = '<li style="color:#f0a0a8">' + (err.message || 'Erreur') + '</li>';
          }
        };
        var bl = card.querySelector('[data-bl]');
        if (bl) bl.onclick = async function () {
          if (!confirm('Bloquer ' + m.email + ' ?')) return;
          try { await api('/admin/managers/' + encodeURIComponent(m.id) + '/block', { method: 'POST' }); await load(); }
          catch (err) { alert(err.message || 'Erreur'); }
        };
        var un = card.querySelector('[data-un]');
        if (un) un.onclick = async function () {
          try { await api('/admin/managers/' + encodeURIComponent(m.id) + '/unblock', { method: 'POST' }); await load(); }
          catch (err) { alert(err.message || 'Erreur'); }
        };
        listEl.appendChild(card);
      });
    } catch (err) {
      listEl.innerHTML = '<div class="err">' + (err.message || err) + '</div>';
    }
  }

  load();
  loadFans();
})();
</script>
</body>
</html>