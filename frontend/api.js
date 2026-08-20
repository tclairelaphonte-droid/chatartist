function authHeaders() {
  const headers = {
    "Content-Type": "application/json",
    "x-vercel-protection-bypass": "backstageBypassSecretKey2026xx",
    "x-vercel-set-bypass-cookie": "true"
  };

  const token = getToken();
  if (token) {
    headers.Authorization = "Bearer " + token;
  }

  const actAs = sessionStorage.getItem("backstage_act_as_manager");
  if (actAs) {
    headers["X-Act-As-Manager"] = actAs;
  }

  return headers;
}