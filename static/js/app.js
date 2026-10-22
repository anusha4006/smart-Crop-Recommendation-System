/**
 * Sensorless Crop Recommendation System Frontend Script
 * Handles real-time weather API integration, soil mapping, and dynamic ML predictions.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements: Sliders & Badges
    const tempRange = document.getElementById('tempRange');
    const tempValue = document.getElementById('tempValue');
    const humidityRange = document.getElementById('humidityRange');
    const humidityValue = document.getElementById('humidityValue');
    const phRange = document.getElementById('phRange');
    const phValue = document.getElementById('phValue');
    const phLabel = document.getElementById('phLabel');
    const rainfallRange = document.getElementById('rainfallRange');
    const rainfallValue = document.getElementById('rainfallValue');

    const inputN = document.getElementById('inputN');
    const inputP = document.getElementById('inputP');
    const inputK = document.getElementById('inputK');

    const cityInput = document.getElementById('cityInput');
    const fetchWeatherBtn = document.getElementById('fetchWeatherBtn');
    const fetchSpinner = document.getElementById('fetchSpinner');
    const fetchStatus = document.getElementById('fetchStatus');
    const fetchStatusText = document.getElementById('fetchStatusText');

    const soilTypeSelect = document.getElementById('soilTypeSelect');
    const soilDescription = document.getElementById('soilDescription');

    const recommendForm = document.getElementById('recommendForm');
    const resetBtn = document.getElementById('resetBtn');

    // UI States
    const initialState = document.getElementById('initialState');
    const loadingState = document.getElementById('loadingState');
    const resultState = document.getElementById('resultState');

    // Result DOM Elements
    const resCropName = document.getElementById('resCropName');
    const resConfidence = document.getElementById('resConfidence');
    const resCategory = document.getElementById('resCategory');
    const resModelBadge = document.getElementById('resModelBadge');
    const resSeason = document.getElementById('resSeason');
    const resWater = document.getElementById('resWater');
    const resSoil = document.getElementById('resSoil');
    const resTips = document.getElementById('resTips');
    const paramChecksContainer = document.getElementById('paramChecksContainer');
    const alternativesList = document.getElementById('alternativesList');

    // Sync Slider values with displayed badges
    function updatePhLabel(val) {
        if (val < 6.0) {
            phLabel.textContent = "Acidic";
            phLabel.className = "badge bg-danger-soft text-danger ms-1";
        } else if (val <= 7.5) {
            phLabel.textContent = "Neutral";
            phLabel.className = "badge bg-success-soft text-success ms-1";
        } else {
            phLabel.textContent = "Alkaline";
            phLabel.className = "badge bg-primary-soft text-primary ms-1";
        }
    }

    tempRange.addEventListener('input', (e) => {
        tempValue.textContent = parseFloat(e.target.value).toFixed(1);
    });

    humidityRange.addEventListener('input', (e) => {
        humidityValue.textContent = parseFloat(e.target.value).toFixed(0);
    });

    phRange.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        phValue.textContent = val.toFixed(1);
        updatePhLabel(val);
    });

    rainfallRange.addEventListener('input', (e) => {
        rainfallValue.textContent = parseFloat(e.target.value).toFixed(1);
    });

    // Soil Type Change handler
    if (soilTypeSelect) {
        soilTypeSelect.addEventListener('change', (e) => {
            const selected = e.target.options[e.target.selectedIndex];
            if (!selected || !selected.value) return;

            const ph = selected.getAttribute('data-ph');
            const n = selected.getAttribute('data-n');
            const p = selected.getAttribute('data-p');
            const k = selected.getAttribute('data-k');

            if (ph) {
                phRange.value = ph;
                phValue.textContent = parseFloat(ph).toFixed(1);
                updatePhLabel(parseFloat(ph));
            }
            if (n && inputN && !inputN.value) inputN.placeholder = `Preset: ${n}`;
            if (p && inputP && !inputP.value) inputP.placeholder = `Preset: ${p}`;
            if (k && inputK && !inputK.value) inputK.placeholder = `Preset: ${k}`;

            soilDescription.textContent = `Applied default parameters for ${selected.text}.`;
        });
    }

    // Auto-Fetch Weather & Regional Soil Data
    async function fetchWeather(city) {
        if (!city || city.trim() === '') {
            alert('Please enter a city or district name.');
            return;
        }

        fetchSpinner.classList.remove('d-none');
        fetchStatus.classList.add('d-none');
        fetchWeatherBtn.disabled = true;

        try {
            const res = await fetch(`/api/weather?city=${encodeURIComponent(city.trim())}`);
            const data = await res.json();

            if (data.weather && data.weather.success) {
                const w = data.weather;
                tempRange.value = w.temperature;
                tempValue.textContent = w.temperature.toFixed(1);

                humidityRange.value = w.humidity;
                humidityValue.textContent = w.humidity.toFixed(0);

                rainfallRange.value = w.rainfall;
                rainfallValue.textContent = w.rainfall.toFixed(1);

                let statusMsg = `Fetched live weather for ${w.location_meta.name || city} from ${w.source} (Temp: ${w.temperature}°C, Humidity: ${w.humidity}%, Rain: ${w.rainfall}mm).`;

                // If regional soil profile matched
                if (data.soil) {
                    const s = data.soil;
                    phRange.value = s.ph;
                    phValue.textContent = s.ph.toFixed(1);
                    updatePhLabel(s.ph);

                    if (inputN) inputN.value = s.n;
                    if (inputP) inputP.value = s.p;
                    if (inputK) inputK.value = s.k;

                    // Match soil type dropdown if present
                    if (soilTypeSelect) {
                        for (let opt of soilTypeSelect.options) {
                            if (opt.value === s.soil_type_key) {
                                opt.selected = true;
                                break;
                            }
                        }
                    }

                    statusMsg += ` | Regional Soil Profile: ${s.soil_type_name} (pH ~${s.ph}).`;
                }

                fetchStatusText.textContent = statusMsg;
                fetchStatus.classList.remove('d-none');
            } else {
                fetchStatusText.textContent = 'Could not fetch live weather. Regional defaults retained.';
                fetchStatus.classList.remove('d-none');
            }
        } catch (err) {
            console.error('Weather fetch error:', err);
            fetchStatusText.textContent = 'Network or API error while querying Open-Meteo. You can set values manually.';
            fetchStatus.classList.remove('d-none');
        } finally {
            fetchSpinner.classList.add('d-none');
            fetchWeatherBtn.disabled = false;
        }
    }

    if (fetchWeatherBtn) {
        fetchWeatherBtn.addEventListener('click', () => {
            fetchWeather(cityInput.value);
        });
    }

    if (cityInput) {
        cityInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                fetchWeather(cityInput.value);
            }
        });
    }

    // Quick City Chips
    document.querySelectorAll('.chip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const city = btn.getAttribute('data-city');
            cityInput.value = city;
            fetchWeather(city);
        });
    });

    // Reset Form
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            tempRange.value = 25.0;
            tempValue.textContent = "25.0";
            humidityRange.value = 70;
            humidityValue.textContent = "70";
            phRange.value = 6.5;
            phValue.textContent = "6.5";
            updatePhLabel(6.5);
            rainfallRange.value = 120.0;
            rainfallValue.textContent = "120.0";
            cityInput.value = "";
            fetchStatus.classList.add('d-none');
            if (inputN) inputN.value = "";
            if (inputP) inputP.value = "";
            if (inputK) inputK.value = "";
            if (soilTypeSelect) soilTypeSelect.selectedIndex = 0;
            soilDescription.textContent = "Select soil type to auto-populate typical pH without laboratory sensors.";

            initialState.classList.remove('d-none');
            loadingState.classList.add('d-none');
            resultState.classList.add('d-none');
        });
    }

    // Handle Form Submit: Predict Recommended Crop
    recommendForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            temperature: parseFloat(tempRange.value),
            humidity: parseFloat(humidityRange.value),
            ph: parseFloat(phRange.value),
            rainfall: parseFloat(rainfallRange.value)
        };

        if (inputN && inputN.value.trim() !== '') payload.n = parseFloat(inputN.value);
        if (inputP && inputP.value.trim() !== '') payload.p = parseFloat(inputP.value);
        if (inputK && inputK.value.trim() !== '') payload.k = parseFloat(inputK.value);

        // Show loading state
        initialState.classList.add('d-none');
        resultState.classList.add('d-none');
        loadingState.classList.remove('d-none');

        try {
            const res = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (data.success) {
                renderResults(data);
            } else {
                alert(data.error || 'Prediction failed.');
                initialState.classList.remove('d-none');
            }
        } catch (err) {
            console.error('Prediction API error:', err);
            alert('Failed to obtain recommendation. Ensure server is active.');
            initialState.classList.remove('d-none');
        } finally {
            loadingState.classList.add('d-none');
        }
    });

    function renderResults(data) {
        const primary = data.top_recommendations[0];
        const details = primary.details;

        resCropName.textContent = primary.display_name;
        resConfidence.textContent = `${primary.confidence}% Match`;
        resCategory.textContent = details.category || "Agricultural Crop";
        resModelBadge.textContent = `${data.model_used} (${data.model_accuracy}% Accuracy)`;

        resSeason.textContent = details.season || "Seasonal";
        resWater.textContent = details.water_requirement || "Moderate";
        resSoil.textContent = details.soil_type || "Fertile Loam";
        resTips.textContent = details.tips || "Cultivate using recommended regional agricultural guidelines.";

        // Parameter Compatibility Checklist
        paramChecksContainer.innerHTML = '';
        const checks = primary.parameter_checks || {};
        const paramIcons = {
            temperature: 'fa-temperature-half text-danger',
            humidity: 'fa-droplet text-info',
            ph: 'fa-flask-vial text-success',
            rainfall: 'fa-cloud-showers-heavy text-primary'
        };

        for (const [param, status] of Object.entries(checks)) {
            const col = document.createElement('div');
            col.className = 'col-sm-6';
            const icon = paramIcons[param] || 'fa-check text-success';
            const isOpt = status.state === 'Optimal';
            const badgeClass = isOpt ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning';

            col.innerHTML = `
                <div class="p-2 rounded-3 border bg-light small d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fa-solid ${icon} me-1"></i>
                        <span class="text-capitalize fw-semibold">${param}:</span>
                        <span class="text-dark">${status.user_val}</span>
                    </div>
                    <span class="badge ${badgeClass} border">${status.state} (${status.optimal_range})</span>
                </div>
            `;
            paramChecksContainer.appendChild(col);
        }

        // Alternative Suitable Crops
        alternativesList.innerHTML = '';
        const alts = data.top_recommendations.slice(1);
        if (alts.length > 0) {
            alts.forEach(alt => {
                const item = document.createElement('div');
                item.className = 'list-group-item d-flex justify-content-between align-items-center py-2 px-3';
                item.innerHTML = `
                    <div class="d-flex align-items-center gap-2">
                        <span class="badge bg-secondary rounded-circle">#${alt.rank}</span>
                        <div>
                            <strong class="text-dark">${alt.display_name}</strong>
                            <small class="text-muted d-block">${alt.details.category || 'Alternative'}</small>
                        </div>
                    </div>
                    <div class="text-end">
                        <span class="fw-bold text-success">${alt.confidence}%</span>
                        <div class="progress" style="width: 70px; height: 5px;">
                            <div class="progress-bar bg-success" style="width: ${alt.confidence}%"></div>
                        </div>
                    </div>
                `;
                alternativesList.appendChild(item);
            });
        } else {
            alternativesList.innerHTML = '<div class="p-2 text-muted small">No other high-probability crops.</div>';
        }

        resultState.classList.remove('d-none');
        resultState.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
