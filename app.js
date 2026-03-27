const DATA_URL = "./data/rundhoje.min.json";

const locateButton = document.querySelector("#locate-button");
const statusEl = document.querySelector("#status");
const resultCard = document.querySelector("#result-card");
const resultTitle = document.querySelector("#result-title");
const resultDistance = document.querySelector("#result-distance");
const resultMeta = document.querySelector("#result-meta");
const sourceLink = document.querySelector("#source-link");
const mapsLink = document.querySelector("#maps-link");

let rundhoje = [];

function haversineKm(lat1, lon1, lat2, lon2) {
  const toRad = (value) => (value * Math.PI) / 180;
  const earthRadiusKm = 6371.0088;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * earthRadiusKm * Math.asin(Math.sqrt(a));
}

function formatDistance(km) {
  if (km < 1) {
    return `${Math.round(km * 1000)} m væk`;
  }
  return `${km.toFixed(2)} km væk`;
}

function setStatus(message) {
  statusEl.textContent = message;
}

function buildMapsUrl(lat, lon) {
  return `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
}

function buildSourceUrl(id) {
  return `https://www.kulturarv.dk/fundogfortidsminder/Lokalitet/${id}`;
}

function renderResult(entry, distanceKm) {
  resultTitle.textContent = "Gravhøj";
  resultDistance.textContent = formatDistance(distanceKm);

  const metaBits = [];
  if (entry.dating) metaBits.push(`Dating: ${entry.dating}`);
  if (entry.stednr) metaBits.push(`Stednr: ${entry.stednr}`);
  if (entry.frednr) metaBits.push(`Frednr: ${entry.frednr}`);
  resultMeta.textContent = metaBits.join(" · ");

  sourceLink.href = buildSourceUrl(entry.id);
  mapsLink.href = buildMapsUrl(entry.lat, entry.lon);

  resultCard.classList.remove("hidden");
}

async function loadData() {
  if (rundhoje.length) return rundhoje;

  setStatus("Indlæser lokal gravhøj-data...");
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error(`data kunne ikke hentes (${response.status})`);
  }

  const payload = await response.json();
  rundhoje = payload.features || [];
  setStatus("Klar. Ingen placering brugt endnu.");
  return rundhoje;
}

function getCurrentPosition() {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000,
    });
  });
}

async function runLookup() {
  locateButton.disabled = true;

  try {
    const entries = await loadData();
    setStatus("Henter din placering...");
    const pos = await getCurrentPosition();
    const { latitude, longitude } = pos.coords;

    setStatus("Finder nærmeste gravhøj...");
    const ranked = entries
      .map((entry) => ({
        ...entry,
        distanceKm: haversineKm(latitude, longitude, entry.lat, entry.lon),
      }))
      .sort((a, b) => a.distanceKm - b.distanceKm);

    if (!ranked.length) {
      throw new Error("Ingen gravhøje fundet i lokal data.");
    }

    renderResult(ranked[0], ranked[0].distanceKm);
    setStatus("Færdig. Din placering blev ikke gemt.");
  } catch (error) {
    setStatus(`Kunne ikke fuldføre søgningen: ${error.message}`);
  } finally {
    locateButton.disabled = false;
  }
}

locateButton.addEventListener("click", runLookup);
loadData().catch((error) => {
  setStatus(`Kunne ikke indlæse lokal data: ${error.message}`);
});
