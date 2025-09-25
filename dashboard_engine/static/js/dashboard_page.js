document.getElementById("gotoJobEngine").addEventListener("click", function() {
    const url = this.dataset.url; // read data-url attribute
    window.location.href = url;
});

// Function to render Plotly dashboards
function renderPlotlyDashboard(containerId, figure, height = 400) {
    console.log(`Rendering ${containerId}:`, figure);
    const container = document.getElementById(containerId);

    if (container && figure) {
        try {
            // Clear loading content
            container.innerHTML = '';

            // Plotly configuration
            const config = {
                responsive: true,
                displayModeBar: false, // Hide toolbar for cleaner look
                displaylogo: false
            };

            // Enhanced layout for better display
            const layout = {
                ...figure.layout,
                autosize: true,
                height: height,
                margin: {
                    l: 50,
                    r: 50,
                    t: 50,
                    b: 50
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {
                    family: 'Inter, system-ui, sans-serif',
                    size: 12,
                    color: '#374151'
                }
            };

            // Special handling for map
            if (containerId === 'mapDashboard') {
                layout.height = 500;
                layout.margin = { l: 0, r: 0, t: 20, b: 0 };
            }

            Plotly.newPlot(container, figure.data, layout, config);

        } catch (error) {
            console.error(`Error rendering ${containerId}:`, error);
            container.innerHTML = `<div class="flex items-center justify-center h-full text-red-500">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Erreur de chargement
            </div>`;
        }
    } else {
        console.warn(`Missing container or figure for ${containerId}`);
        if (container) {
            container.innerHTML = `<div class="flex items-center justify-center h-full text-gray-500">
                <i class="fas fa-chart-line mr-2"></i>
                Aucune donnée disponible
            </div>`;
        }
    }
}

// Refresh function
document.getElementById('refreshBtn').addEventListener('click', function() {
    const btn = this;
    const icon = btn.querySelector('i');

    // Loading animation
    icon.classList.add('fa-spin');
    btn.disabled = true;
    btn.classList.add('opacity-50');

    // Simulate reload
    setTimeout(() => {
        window.location.reload();
    }, 1000);
});

// Initialization when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Correctly get the data from the script tag
    const dataElement = document.getElementById('dashboardsData');
    if (!dataElement) {
        console.error("The 'dashboardsData' script tag was not found.");
        return;
    }

    try {
        const dashboardsData = JSON.parse(dataElement.textContent);
        console.log("Parsed Dashboards Data:", dashboardsData);
        
        // This is the correct data access based on your provided log
        if (dashboardsData) {
            // The map and skills_pie are nested JSON strings, so they need to be parsed again
            if (dashboardsData.map) {
                renderPlotlyDashboard('mapDashboard', JSON.parse(dashboardsData.map), 500);
            }
            if (dashboardsData.skills_pie) {
                renderPlotlyDashboard('skillsPieDashboard', JSON.parse(dashboardsData.skills_pie));
            }
            // The timeline_dashboards are a nested object, access its properties directly
            if (dashboardsData.timeline_dashboards) {
                if (dashboardsData.timeline_dashboards.hourly) {
                    renderPlotlyDashboard('hourlyDashboard', dashboardsData.timeline_dashboards.hourly);
                }
                if (dashboardsData.timeline_dashboards.daily) {
                    renderPlotlyDashboard('dailyDashboard', dashboardsData.timeline_dashboards.daily);
                }
            }
        } else {
            console.error("No data found in 'dashboardsData' script tag.");
        }
    } catch (error) {
        console.error("Failed to parse JSON data from 'dashboardsData' script tag.", error);
    }

    // Progressive fade-in animation
    const cards = document.querySelectorAll('.fade-in');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});

// Responsive handling for Plotly
window.addEventListener('resize', function() {
    setTimeout(() => {
        const plotlyDivs = document.querySelectorAll('[id$="Dashboard"]');
        plotlyDivs.forEach(div => {
            if (div.data) {
                Plotly.Plots.resize(div);
            }
        });
    }, 100);
});